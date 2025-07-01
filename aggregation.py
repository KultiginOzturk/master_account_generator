# master_audit_generator/aggregation.py
from itertools import groupby
import pandas as pd

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

    id_list = original_df["CUSTOMER_ID"].tolist()
    index_by_id = {cid: idx for idx, cid in enumerate(id_list)}

    uf = UnionFind(len(id_list))

    for _, row in df_pairwise.iterrows():
        cid_idx = index_by_id.get(row["CUSTOMER_ID"])
        mid_idx = index_by_id.get(row["master account id"])
        if cid_idx is None or mid_idx is None:
            continue
        reason = row.get("Reason")
        if cid_idx == mid_idx:
            uf.add_reason(cid_idx, reason)
        else:
            uf.union(cid_idx, mid_idx, reason)

    clusters: dict[int, list[int]] = {}
    for idx, cid in enumerate(id_list):
        root = uf.find(idx)
        clusters.setdefault(root, []).append(idx)

    aggregated_rows = []
    for root_idx, members in clusters.items():
        reasons = "; ".join(sorted(uf.reasons[root_idx]))
        root_row = original_df.iloc[root_idx].to_dict()
        first = get_name_fn[0](root_row)
        last = get_name_fn[1](root_row)
        master_name = f"{first} {last}".strip()
        group_id = id_list[root_idx]

        for member_idx in members:
            row = original_df.iloc[member_idx].to_dict()
            row.update({
                "Group ID": group_id,
                "Group Reasons": reasons,
                "master name": master_name,
            })
            aggregated_rows.append(row)

    aggregated = pd.DataFrame(aggregated_rows)
    client_input = aggregated[aggregated["CUSTOMER_ID"] == aggregated["Group ID"]].copy()
    return aggregated, client_input
