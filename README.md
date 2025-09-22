# Master Account Generator

Generates a master account audit from `FR_CUSTOMER`, with outputs to Excel, BigQuery, and optional per-client Google Sheets.

Quick start:

```powershell
python main.py
```

Full documentation:

- docs: see `docs/README.md` or open the sections below
  - [Overview](docs/overview.md)
  - [Setup and Installation](docs/setup.md)
  - [Configuration](docs/configuration.md)
  - [Usage](docs/usage.md)
  - [Workflow](docs/workflow.md)
  - [Outputs](docs/outputs.md)
  - [Troubleshooting](docs/troubleshooting.md)

Environment variables at a glance:

- `BQ_PROJECT` (default `pco-qa`)
- `BQ_DATASET` (default `raw_layer`)
- `WRITE_TO_BQ` (`True` to write to BigQuery, else Excel)
- `CLIENT_IDS` (comma-separated, optional)
- `DRIVE_FOLDER_ID` (optional, for Google Sheets export)
- `GOOGLE_APPLICATION_CREDENTIALS` (Service Account JSON path)
