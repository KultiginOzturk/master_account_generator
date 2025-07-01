# master_audit_generator/matching.py
import pandas as pd
from utils import clean_value, sample_pairs

MAX_PAIRS_PER_GROUP = 1000

def unify_email(row: pd.Series) -> str | None:
    return clean_value(row.get("EMAIL"))

def unify_company(row: pd.Series) -> str | None:
    bc = clean_value(row.get("BILLING_COMPANY_NAME"))
    c  = clean_value(row.get("COMPANY_NAME"))
    return bc or c

def unify_phone(row: pd.Series) -> str | None:
    p1 = clean_value(row.get("PHONE1"))
    return p1 or clean_value(row.get("PHONE2"))

def unify_billto(row: pd.Series) -> str | None:
    return clean_value(row.get("BILL_TO_ACCOUNT_ID"))

def add_pairwise_matches(
    df: pd.DataFrame,
    field: str,
    reason_label: str,
    results: list[dict]
) -> None:
    sub = df[df[field].notnull()]
    for key, group in sub.groupby(field):
        idxs = group.index.tolist()
        if len(idxs) < 2:
            continue
        pairs = sample_pairs(idxs, MAX_PAIRS_PER_GROUP)
        for i, j in pairs:
            for idx in (i, j):
                rec = df.iloc[idx].to_dict()
                rec.update({
                    "Reason": reason_label,
                    "master account id": min(df.at[i, "CUSTOMER_ID"], df.at[j, "CUSTOMER_ID"]),
                    "Confidence": 1.0
                })
                results.append(rec)

def generate_pairwise(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy().reset_index(drop=True)
    df["any_email"]       = df.apply(unify_email, axis=1)
    df["any_company"]     = df.apply(unify_company, axis=1)
    df["norm_phone"]      = df.apply(unify_phone, axis=1)
    df["norm_bill_to_id"] = df.apply(unify_billto, axis=1)

    records = []
    for field, reason in [
        ("any_email", "email match"),
        ("any_company", "company match"),
        ("norm_phone", "phone match"),
        ("norm_bill_to_id", "bill to customer id match"),
    ]:
        add_pairwise_matches(df, field, reason, records)

    pw = pd.DataFrame(records)
    pw.drop_duplicates(subset=["CUSTOMER_ID", "Reason", "master account id", "Confidence"], inplace=True)
    cols = [c for c in pw.columns if c not in ("Reason","master account id","Confidence")] + ["Reason","master account id","Confidence"]
    return pw[cols].sort_values(["master account id","CUSTOMER_ID"]).reset_index(drop=True)
