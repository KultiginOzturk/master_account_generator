## Overview

The Master Account Generator produces a consolidated “master audit” by matching related customer records in the `FR_CUSTOMER` table. It can:

- Generate pairwise matches between records using email, company, phone, and bill-to relationships
- Aggregate records into connected groups representing a master account
- Produce outputs as an Excel workbook, upload tables to BigQuery, and optionally create per-client Google Sheets

### Architecture

- `main.py`: Orchestrates the end-to-end run (read → match → aggregate → write)
- `io_ops.py`:
  - Reads `FR_CUSTOMER` from BigQuery
  - Lists available clients
  - Writes results to Excel or BigQuery
  - Optionally writes per-client Google Sheets (when a Drive folder is provided)
- `matching.py`: Builds pairwise matches, normalizing key fields and ignoring obvious dummy values
- `aggregation.py`: Connects records into groups via union-find, and prepares the client review subset
- `utils.py`: Helpers for normalization, sampling, and name extraction for master account display
- `logger.py`: Simple structured logging wrapper
- `files.py`: Constants for local file outputs

### Data Flow

1. Load `FR_CUSTOMER` from BigQuery (optionally filtered to specific `CLIENT` values)
2. Generate pairwise matches using normalized fields and rules
3. Aggregate matches into groups; compute group-level reasons and representative name
4. Write outputs to Excel or BigQuery; optionally write per-client Google Sheets


