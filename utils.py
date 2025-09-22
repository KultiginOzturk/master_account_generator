"""Utility helpers for normalization and display values.

Includes:
- Baton record detection
- Value cleaning and sampling of index pairs
- Functions to derive master first/last name for group display
"""
# master_audit_generator/utils.py
import pandas as pd
import random
from itertools import combinations
from logger import DQLogger

logger = DQLogger(__name__)

BLANKS = {"", "nan", "none", "null", "n/a"}
DUMMY_PHONES = {"0", "0000000000", "n/a", "none", "null", ""}
DUMMY_EMAILS = {"no@email.com", "n/a", "none", "null", ""}


def is_baton(row: dict) -> bool:
    """Return True if any name/company field contains the word 'baton'."""
    for col in [
        "First Name",
        "Last Name",
        "Company Name",
        "Billing Company Name",
        "Company",
        "FNAME",
        "LNAME",
        "COMPANY_NAME",
        "BILLING_COMPANY_NAME",
    ]:
        val = str(row.get(col, "")).lower()
        if "baton" in val:
            return True
    return False

def clean_value(val: any) -> str | None:
    if pd.isnull(val):
        return None
    s = str(val).strip().lower()
    return None if s in BLANKS else s

def sample_pairs(indices: list[int], sample_size: int) -> list[tuple[int,int]]:
    n = len(indices)
    total = n * (n - 1) // 2
    if total <= sample_size:
        pairs = list(combinations(indices, 2))
        return pairs
    pairs = set()
    while len(pairs) < sample_size:
        i, j = sorted(random.sample(indices, 2))
        pairs.add((i, j))
    result = list(pairs)
    return result

def get_master_first_name(row: dict) -> str:
    keys = [
        "Bill To Billing First Name",
        "Billing First Name",
        "First Name",
        "BILL_TO_BILLING_FNAME",
        "BILLING_FNAME",
        "FNAME",
    ]
    for key in keys:
        v = row.get(key, "")
        if clean_value(v):
            return str(v).strip()
    return ""

def get_master_last_name(row: dict) -> str:
    keys = [
        "Bill To Billing Last Name",
        "Billing Last Name",
        "Last Name",
        "BILL_TO_BILLING_LNAME",
        "BILLING_LNAME",
        "LNAME",
    ]
    for key in keys:
        v = row.get(key, "")
        if clean_value(v):
            return str(v).strip()
    return ""
