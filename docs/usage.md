## Usage

From the repository root, run:

```powershell
python main.py
```

The script will:

- Resolve configuration from environment variables
- Discover clients automatically when `CLIENT_IDS` is not set
- Process each client batch, generate matches, aggregate groups
- Write outputs to Excel or BigQuery
- Optionally create per-client Google Sheets when `DRIVE_FOLDER_ID` is set

### Examples

Run for all clients, write Excel locally:

```powershell
$env:BQ_PROJECT = "pco-qa"
$env:BQ_DATASET = "raw_layer"
$env:WRITE_TO_BQ = "False"
python main.py
```

Run for a subset of clients and upload to BigQuery:

```powershell
$env:CLIENT_IDS = "123, 456"
$env:WRITE_TO_BQ = "True"
python main.py
```

Also export per-client Google Sheets:

```powershell
$env:DRIVE_FOLDER_ID = "<drive-folder-id>"
python main.py
```


