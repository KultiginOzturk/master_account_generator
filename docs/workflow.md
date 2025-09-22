## Workflow

### Matching (pairwise)

Implemented in `matching.py`:

1) Pre-cleaning
   - Skip rows where name/company fields contain the token "baton"
   - Normalize and blank out dummy phone/email values (e.g., `0`, `no@email.com`)
   - Build helper columns:
     - `any_email`: unified email across possible columns
     - `any_company`: prefers billing company, then company
     - `norm_phone`: unified phone across possible columns
     - `norm_bill_to_id`: bill-to ID if present

2) Forced links for child/linked rows
   - When `IsChild` and `LinkedMasterID` exist, add high-confidence links to the master

3) Pairwise generation per field
   - For each non-null value of `any_email`, `any_company`, `norm_phone`, `norm_bill_to_id`, sample pairs within the group (bounded by `MAX_PAIRS_PER_GROUP`)
   - Emit a record for each side of a match with:
     - `Reason`: match type (email/company/phone/bill-to/linked)
     - `master account id`: min of the two customer IDs in the pair
     - `Confidence`: currently 1.0

The result is the "full masterAccount match" sheet.

### Aggregation (groups and client input)

Implemented in `aggregation.py` using a union-find structure:

1) Build the set of all IDs seen in pairwise matches and map them to indices
2) Union records connected by any pairwise match and accumulate reasons on the root
3) For each group (size ≥ 2):
   - Choose `Group ID` as the minimum customer ID in the group
   - Compute `Group Reasons` as a comma-joined set of reasons
   - Derive `master account full name` from representative data using `utils.get_master_first_name/last_name`
4) Produce the aggregated view and a filtered "client input" subset:
   - Exclude groups with strong auto-link reasons (linked property or bill-to) or where there are multiple non-linked reasons (≥2)

Outputs correspond to Excel sheet names and BigQuery table names described in Outputs.


