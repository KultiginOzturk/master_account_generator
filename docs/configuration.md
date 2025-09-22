## Configuration

Set the following environment variables to control behavior. Defaults are shown in parentheses.

- `BQ_PROJECT` (default `pco-qa`): BigQuery project ID
- `BQ_DATASET` (default `raw_layer`): Dataset containing `FR_CUSTOMER`
- `WRITE_TO_BQ` (default `False`): When `True`, write outputs to BigQuery; otherwise write a local Excel file
- `CLIENT_IDS` (optional): Comma-separated list of `CLIENT` values to process; if omitted, all distinct clients are processed sequentially
- `DRIVE_FOLDER_ID` (optional): Google Drive folder ID to create per-client Sheets; if omitted, Google Sheets export is skipped
- `GOOGLE_APPLICATION_CREDENTIALS` (required for BigQuery/Drive/Sheets): Path to a Service Account JSON key

Example (PowerShell):

```powershell
$env:BQ_PROJECT = "my-gcp-project"
$env:BQ_DATASET = "raw_layer"
$env:WRITE_TO_BQ = "False"
$env:CLIENT_IDS = "123,456"
$env:DRIVE_FOLDER_ID = "1AbCDEFghij-KLMNOP_qrstu"
$env:GOOGLE_APPLICATION_CREDENTIALS = "C:\secrets\svc.json"
```


