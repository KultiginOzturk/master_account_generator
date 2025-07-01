"""Constants for output file paths."""
from pathlib import Path

# Default output Excel file for write_sheets
MASTER_AUDIT = Path(__file__).with_name("master_audit.xlsx")
