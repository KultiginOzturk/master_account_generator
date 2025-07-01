# master_audit_generator/main.py
import os
from utils import get_master_first_name, get_master_last_name
from io_ops import read_customer_table, write_sheets
from matching import generate_pairwise
from aggregation import aggregate_groups

def generate_master_audit():
    project = os.getenv("BQ_PROJECT", "pco-qa")
    dataset = os.getenv("BQ_DATASET", "raw_layer")
    to_bq   = os.getenv("WRITE_TO_BQ", "False").lower() == "true"

    clients_env = os.getenv("CLIENT_IDS")
    clients = [c.strip() for c in clients_env.split(",") if c.strip()] if clients_env else None

    df = read_customer_table(project, dataset, clients)

    # clean out Baton/dummy rows here (could be a utils function)
    # … you can factor that out too …

    pw_df = generate_pairwise(df)
    agg_df, client_df = aggregate_groups(pw_df, df, (get_master_first_name, get_master_last_name))
    write_sheets(pw_df, agg_df, client_df, to_bq, project)

if __name__ == "__main__":
    generate_master_audit()
