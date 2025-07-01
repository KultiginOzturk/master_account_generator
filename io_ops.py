# master_audit_generator/io_ops.py
import os
import pandas as pd
from google.cloud import bigquery
import files
from logger import DQLogger

logger = DQLogger(__name__)


def remove_timezones(df: pd.DataFrame) -> pd.DataFrame:
    """Remove timezone information from datetime columns."""
    tz_cols = df.select_dtypes(include=["datetimetz"]).columns
    if len(tz_cols) > 0:
        logger.info("Removing timezone info", columns=list(tz_cols))
    for col in tz_cols:
        df[col] = df[col].dt.tz_localize(None)
    return df


def list_clients(project: str, dataset: str) -> list[str]:
    """Return all distinct client IDs from ``FR_CUSTOMER``."""
    client = bigquery.Client(project=project)
    query = (
        f"SELECT DISTINCT CLIENT FROM `{project}.{dataset}.FR_CUSTOMER` "
        "WHERE CLIENT IS NOT NULL ORDER BY CLIENT"
    )
    logger.info("Fetching list of clients", query=query)
    df = client.query(query).to_dataframe()
    col = "CLIENT" if "CLIENT" in df.columns else "Client"
    return sorted(df[col].dropna().astype(str).tolist())

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

    logger.info("Executing customer query", query=query)
    df = client.query(query).to_dataframe()
    logger.info("Loaded customers", rows=len(df))
    return df

def write_sheets(pairwise, aggregated, client_input, to_bigquery: bool, project: str):
    if to_bigquery:
        logger.info("Writing results to BigQuery")
        pairwise.to_gbq("master_audit.pairwise", project_id=project, if_exists="replace")
        aggregated.to_gbq("master_audit.aggregated", project_id=project, if_exists="replace")
        client_input.to_gbq("master_audit.client_input", project_id=project, if_exists="replace")
    else:
        logger.info("Writing results locally", file=str(files.MASTER_AUDIT))
        pairwise = remove_timezones(pairwise.copy())
        aggregated = remove_timezones(aggregated.copy())
        client_input = remove_timezones(client_input.copy())

        with pd.ExcelWriter(files.MASTER_AUDIT, engine="openpyxl") as w:
            pairwise.to_excel(w, sheet_name="full masterAccount match", index=False)
            aggregated.to_excel(w, sheet_name="masterAccount match aggregated", index=False)
            client_input.to_excel(w, sheet_name="masterAccounts for client input", index=False)


def write_client_google_sheets(pairwise: pd.DataFrame,
                               aggregated: pd.DataFrame,
                               client_input: pd.DataFrame,
                               folder_id: str | None) -> None:
    """Write results to individual Google Sheets per client.

    If ``folder_id`` is ``None`` the function does nothing.  Each unique value
    from the ``CLIENT`` column in ``aggregated`` is written to a Google Sheets
    file inside the given Drive folder. Existing files are replaced while new
    ones are created when necessary.
    """

    if folder_id is None:
        logger.info("No Drive folder id provided; skipping Google Sheets output")
        return

    try:
        import gspread
        from gspread_dataframe import set_with_dataframe
        from googleapiclient.discovery import build
    except Exception:
        raise RuntimeError(
            "Google Sheets dependencies are not installed."
        )

    client_col = "CLIENT" if "CLIENT" in aggregated.columns else "Client"
    if client_col not in aggregated.columns:
        return

    drive = build("drive", "v3")
    # ——— Service Account auth instead of gspread.oauth() ———
    from oauth2client.service_account import ServiceAccountCredentials
    keyfile = os.environ["GOOGLE_APPLICATION_CREDENTIALS"]

    scopes = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive", ]
    creds = ServiceAccountCredentials.from_json_keyfile_name(keyfile, scopes)
    gc = gspread.authorize(creds)
    logger.info("Writing client Google Sheets", folder_id=folder_id)

    for client in aggregated[client_col].dropna().unique():
        logger.info("Processing client", client=client)
        pw_df = pairwise[pairwise[client_col] == client]
        agg_df = aggregated[aggregated[client_col] == client]
        ci_df = client_input[client_input[client_col] == client]
        file_name = f"{client} master audit"
        query = (
            f"name='{file_name}' and '{folder_id}' in parents "
            "and mimeType='application/vnd.google-apps.spreadsheet' "
            "and trashed=false"
        )
        resp = drive.files().list(q=query, fields="files(id)").execute()
        files = resp.get("files", [])

        if files:
            file_id = files[0]["id"]
            ss = gc.open_by_key(file_id)
            worksheets = ss.worksheets()

            # Google Sheets does not allow deleting the last remaining sheet in a
            # spreadsheet.  We therefore keep one sheet until the new sheets are
            # created and remove it afterwards.
            temp_ws = None
            if worksheets:
                temp_ws = worksheets[0]
                for ws in worksheets[1:]:
                    ss.del_worksheet(ws)
                temp_ws.clear()
                temp_ws.update_title("temp")
        else:
            metadata = {
                "name": file_name,
                "mimeType": "application/vnd.google-apps.spreadsheet",
                "parents": [folder_id],
            }
            created = drive.files().create(body=metadata, fields="id").execute()
            file_id = created["id"]
            ss = gc.open_by_key(file_id)
            temp_ws = None

        for df, title in [
            (pw_df, "full masterAccount match"),
            (agg_df, "masterAccount match aggregated"),
            (ci_df, "masterAccounts for client input"),
        ]:
            worksheet = ss.add_worksheet(title, rows=len(df) + 1, cols=len(df.columns) + 1)
            set_with_dataframe(worksheet, df, include_index=False)

        if temp_ws is not None:
            ss.del_worksheet(temp_ws)
