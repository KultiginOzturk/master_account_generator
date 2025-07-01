# master_audit_generator/utils.py
import pandas as pd
import random
from itertools import combinations

BLANKS = {"", "nan", "none", "null", "n/a"}
DUMMY_PHONES = {"0", "0000000000", "n/a", "none", "null", ""}
DUMMY_EMAILS = {"no@email.com", "n/a", "none", "null", ""}

def clean_value(val: any) -> str | None:
    if pd.isnull(val):
        return None
    s = str(val).strip().lower()
    return None if s in BLANKS else s

def sample_pairs(indices: list[int], sample_size: int) -> list[tuple[int,int]]:
    n = len(indices)
    total = n * (n - 1) // 2
    if total <= sample_size:
        return list(combinations(indices, 2))
    pairs = set()
    while len(pairs) < sample_size:
        i, j = sorted(random.sample(indices, 2))
        pairs.add((i, j))
    return list(pairs)

def get_master_first_name(row: dict) -> str:
    for key in ("BILL_TO_BILLING_FNAME", "BILLING_FNAME", "FNAME"):
        v = row.get(key, "")
        if clean_value(v):
            return str(v).strip()
    return ""

def get_master_last_name(row: dict) -> str:
    for key in ("BILL_TO_BILLING_LNAME", "BILLING_LNAME", "LNAME"):
        v = row.get(key, "")
        if clean_value(v):
            return str(v).strip()
    return ""
