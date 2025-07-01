# master_audit_generator/io_ops.py
import os
import pandas as pd
from google.cloud import bigquery
from . import files

def read_customer_table(project: str, dataset: str) -> pd.DataFrame:
    client = bigquery.Client(project=project)
    query = f"SELECT * FROM `{project}.{dataset}.FR_CUSTOMER`"
    return client.query(query).to_dataframe()

def write_sheets(pairwise, aggregated, client_input, to_bigquery: bool, project: str):
    if to_bigquery:
        pairwise.to_gbq("master_audit.pairwise", project_id=project, if_exists="replace")
        aggregated.to_gbq("master_audit.aggregated", project_id=project, if_exists="replace")
        client_input.to_gbq("master_audit.client_input", project_id=project, if_exists="replace")
    else:
        with pd.ExcelWriter(files.MASTER_AUDIT, engine="openpyxl") as w:
            pairwise.to_excel(w, sheet_name="full masterAccount match", index=False)
            aggregated.to_excel(w, sheet_name="masterAccount match aggregated", index=False)
            client_input.to_excel(w, sheet_name="masterAccounts for client input", index=False)
