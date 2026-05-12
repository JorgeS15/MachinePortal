#!/usr/bin/env python3
"""
Vendor-side tool to generate Machine Portal license keys.

Usage:
    python generate_license.py <DEVICE_ID> [YYYYMMDD|LIFETIME]

    DEVICE_ID   The 19-char device ID shown in the activation dialog
                (format: XXXX-XXXX-XXXX-XXXX — dashes are optional)
    Expiry      LIFETIME (default) or an expiry date as YYYYMMDD

Examples:
    python generate_license.py A3F2-B1C9-4A8D-2C1E
    python generate_license.py A3F2B1C94A8D2C1E 20271231
"""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "engelrv_dashboard"))

from licensing import generate_key, _SECRET  # noqa: E402 (path inserted above)


def main() -> None:
    if len(sys.argv) < 2 or sys.argv[1] in ("-h", "--help"):
        print(__doc__)
        sys.exit(0)

    raw_id = sys.argv[1].replace("-", "").upper()
    if len(raw_id) < 8:
        print("ERROR: Device ID is too short (need at least 8 hex chars).")
        sys.exit(1)

    expiry = sys.argv[2].upper() if len(sys.argv) > 2 else "LIFETIME"

    if expiry != "LIFETIME":
        try:
            from datetime import datetime
            datetime.strptime(expiry, "%Y%m%d")
        except ValueError:
            print(f"ERROR: Invalid expiry date '{expiry}'. Use YYYYMMDD or LIFETIME.")
            sys.exit(1)

    key = generate_key(raw_id, expiry)
    exp_label = "never expires" if expiry == "LIFETIME" else f"expires {expiry[:4]}-{expiry[4:6]}-{expiry[6:]}"
    display_id = "-".join(raw_id[:16][i:i+4] for i in range(0, min(len(raw_id), 16), 4))

    print(f"\n  Device ID : {display_id}")
    print(f"  Expiry    : {exp_label}")
    print(f"\n  License key:\n\n    {key}\n")


if __name__ == "__main__":
    main()
