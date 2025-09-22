"""Aggregation of pairwise matches into master-account groups.

Uses a union-find to connect related customer IDs and annotates groups with:
- Group ID (min customer id)
- Group Reasons (consolidated reasons)
- master account full name (derived via utils)

Also builds a client review subset with conservative filter rules.
"""
# master_audit_generator/aggregation.py
import pandas as pd
from logger import DQLogger

logger = DQLogger(__name__)

class UnionFind:
    def __init__(self, n):
        self.parent = list(range(n))
        self.reasons = [set() for _ in range(n)]

    def find(self, i):
        if self.parent[i] != i:
            self.parent[i] = self.find(self.parent[i])
        return self.parent[i]

    def union(self, i, j, reason):
        ri, rj = self.find(i), self.find(j)
        if ri == rj:
            self.reasons[ri].add(reason)
            return
        if ri < rj:
            self.parent[rj] = ri
            self.reasons[ri].update(self.reasons[rj])
            self.reasons[ri].add(reason)
            self.reasons[rj].clear()
        else:
            self.parent[ri] = rj
            self.reasons[rj].update(self.reasons[ri])
            self.reasons[rj].add(reason)
            self.reasons[ri].clear()

    def add_reason(self, i, reason):
        self.reasons[self.find(i)].add(reason)

def aggregate_groups(df_pairwise: pd.DataFrame, original_df: pd.DataFrame, get_name_fn):
    """Aggregate pairwise matches into master account groups.

    Parameters
    ----------
    df_pairwise : pd.DataFrame
        Output from :func:`matching.generate_pairwise`.
    original_df : pd.DataFrame
        Raw FR_CUSTOMER table used to generate ``df_pairwise``.
    get_name_fn : tuple[callable, callable]
        Functions returning first and last name for a row.

    Returns
    -------
    tuple[pd.DataFrame, pd.DataFrame]
        ``(aggregated, client_input)`` data frames.
    """

    logger.info("Aggregating pairwise groups")

    cid_col = "Customer ID" if "Customer ID" in original_df.columns else "CUSTOMER_ID"

    all_ids = set(df_pairwise[cid_col]) | set(df_pairwise["master account id"])
    all_ids = list(all_ids)
    index_by_id = {cid: idx for idx, cid in enumerate(all_ids)}

    uf = UnionFind(len(all_ids))

    # store original data
    cid_to_data = {}
    for _, row in original_df.iterrows():
        cid = row[cid_col]
        cid_to_data.setdefault(cid, row.to_dict())

    for _, row in df_pairwise.iterrows():
        cid_idx = index_by_id.get(row[cid_col])
        mid_idx = index_by_id.get(row["master account id"])
        if cid_idx is None or mid_idx is None:
            continue
        uf.union(cid_idx, mid_idx, row["Reason"])

    groups: dict[int, list[int]] = {}
    for cid, idx in index_by_id.items():
        root = uf.find(idx)
        groups.setdefault(root, []).append(cid)

    logger.info("Found groups", total=len(groups))

    aggregated_rows = []
    group_id_to_reasonset = {}
    for root_idx, cids_in_group in groups.items():
        if len(cids_in_group) < 2:
            continue
        reasons = uf.reasons[root_idx]
        reason_str = ", ".join(sorted(reasons))
        group_id = min(cids_in_group)
        rep_data = cid_to_data.get(group_id, {})
        first = get_name_fn[0](rep_data)
        last = get_name_fn[1](rep_data)
        master_name = f"{first} {last}".strip()
        group_id_to_reasonset[group_id] = reasons
        for cid in cids_in_group:
            row = cid_to_data.get(cid, {})
            row_copy = dict(row)
            row_copy.update({
                "Group ID": group_id,
                "Group Reasons": reason_str,
                "master account full name": master_name,
            })
            aggregated_rows.append(row_copy)

    aggregated = pd.DataFrame(aggregated_rows).sort_values(["Group ID", cid_col])

    client_rows = []
    seen = set()
    for _, row in aggregated.iterrows():
        cid = row[cid_col]
        if cid in seen:
            continue
        seen.add(cid)
        gid = row["Group ID"]
        reasons = group_id_to_reasonset.get(gid, set())
        if {"linked_property", "bill to customer id match"} & reasons:
            continue
        remaining = reasons - {"linked_property", "bill to customer id match"}
        if len(remaining) >= 2:
            continue
        client_rows.append(dict(row))

    client_input = pd.DataFrame(client_rows).sort_values(["Group ID", cid_col])
    logger.info(
        "Aggregation complete",
        aggregated_rows=len(aggregated),
        client_rows=len(client_input),
    )
    return aggregated, client_input
