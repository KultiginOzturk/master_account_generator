# master_audit_generator/main.py
import os
from logger import DQLogger
from utils import get_master_first_name, get_master_last_name
from io_ops import (
    read_customer_table,
    write_sheets,
    write_client_google_sheets,
)
from matching import generate_pairwise
from aggregation import aggregate_groups

logger = DQLogger(__name__)

def generate_master_audit():
    logger.info("Starting master audit generation")

    project = os.getenv("BQ_PROJECT", "pco-qa")
    dataset = os.getenv("BQ_DATASET", "raw_layer")
    to_bq   = os.getenv("WRITE_TO_BQ", "False").lower() == "true"

    clients_env = os.getenv("CLIENT_IDS")
    clients = [c.strip() for c in clients_env.split(",") if c.strip()] if clients_env else None

    logger.info(
        "Reading customer table",
        project=project,
        dataset=dataset,
        clients=clients,
    )
    df = read_customer_table(project, dataset, clients)
    folder_id = os.getenv("DRIVE_FOLDER_ID")

    # clean out Baton/dummy rows here (could be a utils function)
    # … you can factor that out too …

    logger.info("Generating pairwise matches")
    pw_df = generate_pairwise(df)
    logger.info("Aggregating groups")
    agg_df, client_df = aggregate_groups(
        pw_df,
        df,
        (get_master_first_name, get_master_last_name),
    )
    logger.info("Writing sheets", to_bigquery=to_bq)
    write_sheets(pw_df, agg_df, client_df, to_bq, project)
    write_client_google_sheets(pw_df, agg_df, client_df, folder_id)
    logger.info("Master audit generation complete")

if __name__ == "__main__":
    generate_master_audit()
