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
import base64
from datetime import datetime

try:
    from nacl.signing import SigningKey
except ImportError:
    sys.exit("ERROR: Install PyNaCl first:  pip install PyNaCl")

_PRIVATE_KEY_PATH = os.path.join(os.path.dirname(__file__), "private.key")


def _load_signing_key() -> SigningKey:
    if not os.path.exists(_PRIVATE_KEY_PATH):
        sys.exit(
            f"ERROR: Private key not found at {_PRIVATE_KEY_PATH}\n"
            "Run generate_keypair.py first to create a keypair."
        )
    with open(_PRIVATE_KEY_PATH) as f:
        seed_hex = f.read().strip()
    return SigningKey(bytes.fromhex(seed_hex))


def generate_key(device_id: str, expiry: str = "LIFETIME") -> str:
    fp8 = device_id.replace("-", "").upper().replace("O", "0")[:8]
    expiry = expiry.upper()
    msg = f"{fp8}|{expiry}".encode()
    sk = _load_signing_key()
    sig_bytes = sk.sign(msg).signature  # 64 bytes
    sig = base64.urlsafe_b64encode(sig_bytes).rstrip(b"=").decode()
    return f"{fp8}-{expiry}-{sig}"


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
