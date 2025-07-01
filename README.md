# Master Account Generator

This tool generates a master account audit by matching records from the
`FR_CUSTOMER` table. Records can optionally be uploaded to BigQuery or
saved locally as an Excel workbook.

## Usage

The script is executed via `main.py` and relies on a few environment
variables:

- `BQ_PROJECT` – BigQuery project ID (default `pco-qa`)
- `BQ_DATASET` – dataset containing `FR_CUSTOMER` (default `raw_layer`)
- `WRITE_TO_BQ` – set to `True` to upload the results to BigQuery
- `CLIENT_IDS` – comma separated list of client IDs to filter on (optional)

Run the tool:

```bash
python main.py
```

When `WRITE_TO_BQ` is not set to `True`, the output is written to
`master_audit.xlsx` in the project directory.

## Installation

Install dependencies using pip:

```bash
pip install -r requirements.txt
```

## Output

Three sheets are produced when writing to Excel:

1. **full masterAccount match** – pairwise record matches
2. **masterAccount match aggregated** – aggregated groups of matches
3. **masterAccounts for client input** – rows representing the master
   account for each group
