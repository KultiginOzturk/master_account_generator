# master_audit_generator/main.py
import os
import pandas as pd
from logger import DQLogger
from utils import get_master_first_name, get_master_last_name
from io_ops import (
    read_customer_table,
    write_sheets,
    write_client_google_sheets,
    list_clients,
)
from matching import generate_pairwise
from aggregation import aggregate_groups

logger = DQLogger(__name__)

def generate_master_audit():
    logger.info("Starting master audit generation")

    project = os.getenv("BQ_PROJECT", "pco-qa")
    dataset = os.getenv("BQ_DATASET", "raw_layer")
    to_bq   = os.getenv("WRITE_TO_BQ", "False").lower() == "true"

    folder_id = os.getenv("DRIVE_FOLDER_ID")

    clients_env = os.getenv("CLIENT_IDS")
    if clients_env:
        batches = [[c.strip() for c in clients_env.split(",") if c.strip()]]
    else:
        all_clients = list_clients(project, dataset)
        logger.info("No CLIENT_IDS provided; processing each client", count=len(all_clients))
        batches = [[c] for c in all_clients]

    pw_frames = []
    agg_frames = []
    ci_frames = []

    for batch in batches:
        logger.info("Processing clients", clients=batch)
        df = read_customer_table(project, dataset, batch)

        logger.info("Generating pairwise matches")
        pw_df = generate_pairwise(df)

        logger.info("Aggregating groups")
        agg_df, client_df = aggregate_groups(
            pw_df,
            df,
            (get_master_first_name, get_master_last_name),
        )

        pw_frames.append(pw_df)
        agg_frames.append(agg_df)
        ci_frames.append(client_df)

        write_client_google_sheets(pw_df, agg_df, client_df, folder_id)

    pairwise = pd.concat(pw_frames, ignore_index=True) if len(pw_frames) > 1 else pw_frames[0]
    aggregated = pd.concat(agg_frames, ignore_index=True) if len(agg_frames) > 1 else agg_frames[0]
    client_df_final = pd.concat(ci_frames, ignore_index=True) if len(ci_frames) > 1 else ci_frames[0]

    logger.info("Writing sheets", to_bigquery=to_bq)
    write_sheets(pairwise, aggregated, client_df_final, to_bq, project)

    logger.info("Master audit generation complete")

if __name__ == "__main__":
    generate_master_audit()
