#!/usr/bin/env python3
"""DM Writer — Personalize DM sequences using company research and Gemini AI."""

import argparse
import sys
import os

from config import GEMINI_API_KEY
from csv_io import read_leads, write_dms
from scraper import research_company
from personalizer import personalize_dms


DEFAULT_TEMPLATES_PATH = os.path.join(os.path.dirname(__file__), "templates", "dm_templates.txt")


def load_templates(path: str) -> dict[str, str]:
    """Load DM templates from a text file with --- separators."""
    if not os.path.exists(path):
        print(f"Error: Templates file not found at '{path}'")
        sys.exit(1)

    with open(path) as f:
        content = f.read()

    sections = content.split("---")
    templates = {}
    for section in sections:
        section = section.strip()
        if not section:
            continue
        lines = section.split("\n", 1)
        header = lines[0].strip().lower().replace(" ", "_")
        body = lines[1].strip() if len(lines) > 1 else ""
        templates[header] = body

    required = ["dm_1", "dm_2", "dm_3"]
    for key in required:
        if key not in templates:
            print(f"Error: Template '{key}' not found in templates file. Expected headers: DM 1, DM 2, DM 3")
            sys.exit(1)

    return templates


def main():
    parser = argparse.ArgumentParser(description="Personalize DM sequences from a CSV file")
    parser.add_argument(
        "csv_file",
        help="Path to the CSV file with leads",
    )
    parser.add_argument(
        "--templates", "-t",
        default=DEFAULT_TEMPLATES_PATH,
        help="Path to DM templates file (default: templates/dm_templates.txt)",
    )
    parser.add_argument(
        "--skip-existing", "-s",
        action="store_true",
        help="Skip rows that already have DMs filled in",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print personalized DMs without writing to CSV",
    )
    args = parser.parse_args()

    # Validate config
    if not GEMINI_API_KEY:
        print("Error: GEMINI_API_KEY not set. Add it to your .env file.")
        sys.exit(1)

    # Load templates
    templates = load_templates(args.templates)
    print(f"✓ Loaded DM templates from {args.templates}")

    # Read leads from CSV
    print(f"Reading leads from {args.csv_file}...")
    try:
        leads, headers, all_rows = read_leads(args.csv_file)
    except (FileNotFoundError, ValueError) as e:
        print(f"Error: {e}")
        sys.exit(1)

    print(f"✓ Found {len(leads)} leads")

    if not leads:
        print("No leads to process. Make sure your CSV has data rows.")
        return

    # Process each lead
    processed = 0
    skipped = 0
    errors = 0

    for i, lead in enumerate(leads, 1):
        if args.skip_existing and lead["has_dms"]:
            skipped += 1
            print(f"[{i}/{len(leads)}] Skipping {lead['company_name']} (DMs already exist)")
            continue

        print(f"\n[{i}/{len(leads)}] Processing: {lead['lead_name']} at {lead['company_name']}")

        # Research
        print(f"  Researching {lead['company_name']}...")
        research = research_company(lead["website"], lead["linkedin"])

        # Personalize
        print(f"  Personalizing DMs with Gemini...")
        try:
            dms = personalize_dms(
                lead_name=lead["lead_name"],
                company_name=lead["company_name"],
                research=research,
                dm_templates=templates,
            )
        except Exception as e:
            print(f"  ✗ Error personalizing DMs: {e}")
            errors += 1
            continue

        if args.dry_run:
            print(f"\n  --- DM 1 ---\n  {dms['dm_1'][:200]}...")
            print(f"\n  --- DM 2 ---\n  {dms['dm_2'][:200]}...")
            print(f"\n  --- DM 3 ---\n  {dms['dm_3'][:200]}...")
        else:
            # Write to CSV
            print(f"  Writing DMs to CSV...")
            try:
                write_dms(args.csv_file, headers, all_rows, lead["row_idx"], dms)
                print(f"  ✓ Done")
            except Exception as e:
                print(f"  ✗ Error writing to CSV: {e}")
                errors += 1
                continue

        processed += 1

    print(f"\n{'='*50}")
    print(f"Complete! Processed: {processed}, Skipped: {skipped}, Errors: {errors}")


if __name__ == "__main__":
    main()
