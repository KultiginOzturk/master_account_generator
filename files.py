"""Path constants for local file inputs/outputs.

Defines:
- MASTER_AUDIT: Excel output path for consolidated sheets
- CUSTOMERS / LINKED_PROPERTIES: optional local sources (not used by default)
"""
"""Constants for output file paths."""
from pathlib import Path

# Default output Excel file for write_sheets
MASTER_AUDIT = Path(__file__).with_name("master_audit.xlsx")

# Input file paths when using local Excel sources
CUSTOMERS = Path(__file__).with_name("customers.xlsx")
LINKED_PROPERTIES = Path(__file__).with_name("linked_properties.xlsx")
