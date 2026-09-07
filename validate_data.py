import json
import os
import sys

MIN_ROWS_DEFAULT = 100
PATH = "public/data.json"


def main():
    min_rows = int(os.environ.get("MIN_DATA_ROWS", MIN_ROWS_DEFAULT))
    if not os.path.exists(PATH):
        print(f"::error::File missing: {PATH}")
        sys.exit(1)
    try:
        with open(PATH, "r") as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        print(f"::error::Invalid JSON in {PATH}: {e}")
        sys.exit(1)
    except OSError as e:
        print(f"::error::Cannot read {PATH}: {e}")
        sys.exit(1)

    if not isinstance(data, list):
        print(f"::error::{PATH} top-level type is {type(data).__name__}, expected list")
        sys.exit(1)

    print(f"Rows in {PATH}: {len(data)} (minimum required: {min_rows})")

    if len(data) < min_rows:
        print(
            f"::error::Only {len(data)} rows found (need >= {min_rows}). "
            "Aborting to avoid deploying an empty/partial member directory."
        )
        sys.exit(1)

    required = {"id", "name", "type", "address"}
    bad_rows = []
    for i, row in enumerate(data):
        if not isinstance(row, dict):
            bad_rows.append((i, f"not a dict: {type(row).__name__}"))
            continue
        missing = required - set(row.keys())
        if missing:
            bad_rows.append((i, f"missing keys: {sorted(missing)}"))
        if len(bad_rows) >= 5:
            break

    if bad_rows:
        print("::error::Some rows failed schema check:")
        for idx, reason in bad_rows:
            print(f"  - row {idx}: {reason}")
        sys.exit(1)

    ids = sorted([m.get("id") for m in data if isinstance(m, dict) and m.get("id")], reverse=True)
    print(f"Highest member IDs present: {ids[:15]}")
    print("Validation PASSED. Safe to deploy.")


if __name__ == "__main__":
    main()
