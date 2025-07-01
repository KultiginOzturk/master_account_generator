# master_audit_generator/aggregation.py
from itertools import groupby

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

def aggregate_groups(df_pairwise, original_df, get_name_fn):
    # ... build UnionFind over all CUSTOMER_IDs and master IDs ...
    # ... union each pair with its reason ...
    # ... then collect clusters into two DataFrames:
    #     - full aggregation with Group ID, Group Reasons, master name (sheet 2)
    #     - client‐input filtering (sheet 3)
    pass  # implement per your original logic
