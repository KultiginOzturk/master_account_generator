## Outputs

### Local Excel (default)

Path: `master_audit.xlsx` (next to the Python modules). Sheets:

- `full masterAccount match`: Pairwise match records with reason and master id
- `masterAccount match aggregated`: Grouped view with `Group ID`, `Group Reasons`, `master account full name`
- `masterAccounts for client input`: Subset intended for manual review

### BigQuery (when `WRITE_TO_BQ=True`)

Project: `$BQ_PROJECT`. Tables (dataset `master_audit`):

- `master_audit.pairwise`
- `master_audit.aggregated`
- `master_audit.client_input`

Tables are written with `if_exists="replace"`.

### Per-client Google Sheets (optional)

When `DRIVE_FOLDER_ID` is set, for each `CLIENT` a Google Sheets file named:

```
<CLIENT> master audit
```

is created/replaced in that folder. Each file contains the three sheets listed above for that client only.


