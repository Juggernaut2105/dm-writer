import csv
import os

REQUIRED_HEADERS = ["company name", "lead name", "company website", "company linkedin"]
DM_HEADERS = ["dm 1", "dm 2", "dm 3"]


def _find_columns(headers: list[str]) -> dict[str, int]:
    """Map expected header names to their column indices (0-based)."""
    normalized = [h.strip().lower() for h in headers]
    col_map = {}

    for expected in REQUIRED_HEADERS + DM_HEADERS:
        try:
            col_map[expected] = normalized.index(expected)
        except ValueError:
            if expected in REQUIRED_HEADERS:
                raise ValueError(
                    f"Required column '{expected}' not found in CSV headers: {headers}"
                )
    return col_map


def read_leads(csv_path: str) -> tuple[list[dict], list[str], list[list[str]]]:
    """Read leads from CSV. Returns (leads, headers, all_rows) for later writing."""
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"CSV file not found: {csv_path}")

    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.reader(f)
        all_rows = list(reader)

    if not all_rows:
        return [], [], []

    headers = all_rows[0]
    col_map = _find_columns(headers)

    leads = []
    for row_idx, row in enumerate(all_rows[1:], start=1):  # 1-based index into all_rows
        if col_map["company name"] >= len(row):
            continue
        company_name = row[col_map["company name"]].strip()
        if not company_name:
            continue

        lead = {
            "row_idx": row_idx,
            "company_name": company_name,
            "lead_name": row[col_map["lead name"]].strip() if col_map["lead name"] < len(row) else "",
            "website": row[col_map["company website"]].strip() if col_map["company website"] < len(row) else "",
            "linkedin": row[col_map["company linkedin"]].strip() if col_map["company linkedin"] < len(row) else "",
        }

        dm1_col = col_map.get("dm 1")
        if dm1_col is not None and dm1_col < len(row) and row[dm1_col].strip():
            lead["has_dms"] = True
        else:
            lead["has_dms"] = False

        leads.append(lead)

    return leads, headers, all_rows


def write_dms(csv_path: str, headers: list[str], all_rows: list[list[str]], row_idx: int, dms: dict[str, str]):
    """Write personalized DMs into the row data and save the CSV."""
    col_map = _find_columns(headers)

    # Add DM columns to headers if missing
    for dm_header in DM_HEADERS:
        if dm_header not in col_map:
            headers.append(dm_header.upper())
            col_map[dm_header] = len(headers) - 1

    # Ensure the row is long enough
    row = all_rows[row_idx]
    while len(row) < len(headers):
        row.append("")

    # Write DM values
    for key, header in [("dm_1", "dm 1"), ("dm_2", "dm 2"), ("dm_3", "dm 3")]:
        row[col_map[header]] = dms.get(key, "")

    # Ensure all rows have consistent column count
    for r in all_rows:
        while len(r) < len(headers):
            r.append("")

    # Update headers row
    all_rows[0] = headers

    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerows(all_rows)
