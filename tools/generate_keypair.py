#!/usr/bin/env python3
"""
One-time tool to generate a new Ed25519 keypair for Machine Portal licensing.

Run this ONCE to set up a new installation. It saves private.key and
automatically updates the public key in dashboard/licensing.py.
Then rebuild the exe — the new keypair is live.

Usage:
    python generate_keypair.py
"""
import os
import re
import sys

try:
    from nacl.signing import SigningKey
except ImportError:
    sys.exit("ERROR: Install PyNaCl first:  pip install PyNaCl")

_TOOLS_DIR     = os.path.dirname(__file__)
_REPO_ROOT     = os.path.join(_TOOLS_DIR, "..")
_PRIVATE_KEY_PATH  = os.path.join(_TOOLS_DIR, "private.key")
_LICENSING_PATH    = os.path.join(_REPO_ROOT, "dashboard", "licensing.py")


def main():
    sk = SigningKey.generate()
    seed_hex = bytes(sk).hex()
    pub_hex  = bytes(sk.verify_key).hex()

    # Save private key
    with open(_PRIVATE_KEY_PATH, "w") as f:
        f.write(seed_hex + "\n")
    print(f"Private key saved to: {_PRIVATE_KEY_PATH}")
    print("KEEP THIS SECRET AND OFFLINE. Never commit it to source control.\n")

    # Patch public key directly into licensing.py
    with open(_LICENSING_PATH, "r", encoding="utf-8") as f:
        src = f.read()

    new_src, n = re.subn(
        r'(_PUBLIC_KEY_HEX\s*=\s*")[0-9a-fA-F]+"',
        rf'\g<1>{pub_hex}"',
        src,
    )
    if n == 0:
        print("WARNING: Could not find _PUBLIC_KEY_HEX in licensing.py.")
        print(f"Manually set it to: {pub_hex}")
    else:
        with open(_LICENSING_PATH, "w", encoding="utf-8") as f:
            f.write(new_src)
        print(f"Public key written to dashboard/licensing.py.")
        print("Rebuild the exe to activate the new keypair.\n")


if __name__ == "__main__":
    main()
