## Troubleshooting

### BigQuery authentication errors

- Ensure `$GOOGLE_APPLICATION_CREDENTIALS` points to a valid Service Account key JSON
- Verify the service account has BigQuery permissions and the project/dataset names are correct

### Google Sheets or Drive errors

- Install optional deps: `gspread`, `gspread_dataframe`, `google-api-python-client`
- Set `$DRIVE_FOLDER_ID` to a folder the service account can access
- Enable the Drive and Sheets APIs in the GCP project

### Empty or missing sheets

- Confirm `FR_CUSTOMER` contains rows for the selected `CLIENT`
- If `CLIENT_IDS` is set, verify values match those in the `CLIENT` column

### Unexpected groupings

- Inspect `full masterAccount match` for the exact `Reason` values
- Check for dummy data: emails like `no@email.com` or phone `0` are blanked by design
- Linked-property and bill-to links may auto-group; see Workflow for filter rules

### Local Excel write issues on Windows

- Ensure no process has `master_audit.xlsx` open while writing
- Confirm `openpyxl` is installed


