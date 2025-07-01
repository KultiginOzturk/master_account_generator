# master_audit_generator/io_ops.py
import os
import pandas as pd
from google.cloud import bigquery
import files


def remove_timezones(df: pd.DataFrame) -> pd.DataFrame:
    """Remove timezone information from datetime columns."""
    tz_cols = df.select_dtypes(include=["datetimetz"]).columns
    for col in tz_cols:
        df[col] = df[col].dt.tz_localize(None)
    return df

def read_customer_table(
    project: str,
    dataset: str,
    clients: list[str] | None = None,
) -> pd.DataFrame:
    """Load the ``FR_CUSTOMER`` table from BigQuery.

    Parameters
    ----------
    project : str
        BigQuery project ID.
    dataset : str
        Dataset containing ``FR_CUSTOMER``.
    clients : list[str] | None, optional
        Optional list of client IDs to limit the query to.

    Returns
    -------
    pd.DataFrame
        Customer table as a DataFrame.
    """

    client = bigquery.Client(project=project)

    query = f"SELECT * FROM `{project}.{dataset}.FR_CUSTOMER`"
    if clients:
        formatted = ",".join(f"'{c}'" for c in clients)
        query += f" WHERE CLIENT IN ({formatted})"

    return client.query(query).to_dataframe()

def write_sheets(pairwise, aggregated, client_input, to_bigquery: bool, project: str):
    if to_bigquery:
        pairwise.to_gbq("master_audit.pairwise", project_id=project, if_exists="replace")
        aggregated.to_gbq("master_audit.aggregated", project_id=project, if_exists="replace")
        client_input.to_gbq("master_audit.client_input", project_id=project, if_exists="replace")
    else:
        pairwise = remove_timezones(pairwise.copy())
        aggregated = remove_timezones(aggregated.copy())
        client_input = remove_timezones(client_input.copy())

        with pd.ExcelWriter(files.MASTER_AUDIT, engine="openpyxl") as w:
            pairwise.to_excel(w, sheet_name="full masterAccount match", index=False)
            aggregated.to_excel(w, sheet_name="masterAccount match aggregated", index=False)
            client_input.to_excel(w, sheet_name="masterAccounts for client input", index=False)
