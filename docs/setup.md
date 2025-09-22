## Setup and Installation

### Prerequisites

- Python 3.10+
- Access to a Google Cloud project containing `FR_CUSTOMER` in BigQuery
- Service Account JSON key with permissions:
  - BigQuery Data Viewer and Job User (to read and run queries)
  - If using Google Sheets/Drive export: Drive and Sheets API enabled, and the service account granted access to the target Drive folder

### Install

1) Create and activate a virtual environment

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

2) Install dependencies

```powershell
pip install -r requirements.txt
```

3) Authenticate to Google Cloud using a Service Account key

```powershell
$env:GOOGLE_APPLICATION_CREDENTIALS = "C:\path\to\service-account.json"
```

If you will export per-client Google Sheets, ensure the Drive folder is shared with the service account and the Drive/Sheets APIs are enabled.


