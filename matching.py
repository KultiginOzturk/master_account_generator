"""Pairwise matching logic.

Builds pairwise match records by:
- Cleaning dummy phones/emails and skipping `baton` rows
- Unifying key fields (email, company, phone, bill-to)
- Emitting sampled pairs per key with a reason and master id

Output feeds aggregation and Excel/BigQuery sheets.
"""
# master_audit_generator/matching.py
import pandas as pd
import numpy as np
from utils import clean_value, sample_pairs, is_baton, DUMMY_EMAILS, DUMMY_PHONES
from logger import DQLogger

logger = DQLogger(__name__)

MAX_PAIRS_PER_GROUP = 1000

def add_linked_lines(
    child_row: dict,
    master_id: int,
    rec_list: list[dict],
    df: pd.DataFrame,
) -> None:
    child_copy = child_row.copy()
    child_copy["Reason"] = "linked_property"
    child_copy["master account id"] = master_id
    child_copy["Confidence"] = 1.0
    rec_list.append(child_copy)

    if "Customer ID" in df.columns:
        master_match = df[df["Customer ID"] == master_id]
    else:
        master_match = df[df["CUSTOMER_ID"] == master_id]
    if not master_match.empty:
        m_copy = master_match.iloc[0].to_dict()
        m_copy["Reason"] = "linked_property"
        m_copy["master account id"] = master_id
        m_copy["Confidence"] = 1.0
        rec_list.append(m_copy)

def unify_email(row: pd.Series) -> str | None:
    for key in [
        "Billing Email Address",
        "Email Address",
        "BILLING_EMAIL_ADDRESS",
        "EMAIL",
    ]:
        val = clean_value(row.get(key))
        if val:
            return val
    return None

def unify_company(row: pd.Series) -> str | None:
    for bc_key in ["Billing Company Name", "BILLING_COMPANY_NAME"]:
        bc = clean_value(row.get(bc_key))
        if bc:
            break
    else:
        bc = None
    for c_key in ["Company Name", "COMPANY_NAME", "Company"]:
        c = clean_value(row.get(c_key))
        if c:
            break
    else:
        c = None
    return bc or c

def unify_phone(row: pd.Series) -> str | None:
    for key in ["Phone 1", "PHONE1", "Phone"]:
        p = clean_value(row.get(key))
        if p:
            return p
    return clean_value(row.get("PHONE2"))

def unify_billto(row: pd.Series) -> str | None:
    for key in ["Bill To Customer ID", "BILL_TO_ACCOUNT_ID"]:
        val = clean_value(row.get(key))
        if val:
            return val
    return None

def add_pairwise_matches(
    df: pd.DataFrame,
    field: str,
    reason_label: str,
    results: list[dict],
    cid_col: str,
) -> None:
    logger.info("Matching by field", field=field)
    sub = df[df[field].notnull()]
    before = len(results)
    for key, group in sub.groupby(field):
        idxs = group.index.tolist()
        if len(idxs) < 2:
            continue
        pairs = sample_pairs(idxs, MAX_PAIRS_PER_GROUP)
        for i, j in pairs:
            for idx in (i, j):
                rec = df.iloc[idx].to_dict()
                rec.update(
                    {
                        "Reason": reason_label,
                        "master account id": min(df.at[i, cid_col], df.at[j, cid_col]),
                        "Confidence": 1.0,
                    }
                )
                results.append(rec)
    logger.info("Pairs added", reason=reason_label, count=len(results) - before)

def generate_pairwise(df: pd.DataFrame) -> pd.DataFrame:
    logger.info("Generating pairwise matches", rows=len(df))
    df = df.copy().reset_index(drop=True)

    # remove rows with Baton in key fields and clean dummy emails/phones
    skip_mask = []
    for idx, row in df.iterrows():
        if is_baton(row):
            skip_mask.append(True)
            continue
        phone_val = str(row.get("Phone 1", row.get("PHONE1", ""))).strip().lower()
        if phone_val in DUMMY_PHONES:
            df.at[idx, "Phone 1" if "Phone 1" in df.columns else "PHONE1"] = np.nan
        for col_email in ["Email Address", "Billing Email Address", "EMAIL", "BILLING_EMAIL_ADDRESS"]:
            if col_email in df.columns:
                e_val = str(row.get(col_email, "")).strip().lower()
                if e_val in DUMMY_EMAILS:
                    df.at[idx, col_email] = np.nan
        skip_mask.append(False)
    if skip_mask:
        df["skip"] = skip_mask
        removed = len(df) - df[~df["skip"]].shape[0]
        logger.info("Skipping rows", removed=removed)
        df = df[~df["skip"]].copy().reset_index(drop=True)

    df["any_email"] = df.apply(unify_email, axis=1)
    df["any_company"] = df.apply(unify_company, axis=1)
    df["norm_phone"] = df.apply(unify_phone, axis=1)
    df["norm_bill_to_id"] = df.apply(unify_billto, axis=1)

    records = []

    # linked property forced matches
    if "IsChild" in df.columns and "LinkedMasterID" in df.columns:
        for _, row in df[df["IsChild"]].iterrows():
            add_linked_lines(row.to_dict(), row["LinkedMasterID"], records, df)

    masters_df = df
    if "IsChild" in df.columns:
        masters_df = df[df["IsChild"] == False].copy()

    cid_col = "Customer ID" if "Customer ID" in df.columns else "CUSTOMER_ID"

    for field, reason in [
        ("any_email", "email match"),
        ("any_company", "company match"),
        ("norm_phone", "phone match"),
        ("norm_bill_to_id", "bill to customer id match"),
    ]:
        add_pairwise_matches(masters_df, field, reason, records, cid_col)

    pw = pd.DataFrame(records)
    pw.drop_duplicates(subset=[cid_col, "Reason", "master account id", "Confidence"], inplace=True)
    cols = [c for c in pw.columns if c not in ("Reason", "master account id", "Confidence")] + ["Reason", "master account id", "Confidence"]
    result = pw[cols].sort_values(["master account id", cid_col]).reset_index(drop=True)
    logger.info("Pairwise generation complete", pairs=len(result))
    return result
