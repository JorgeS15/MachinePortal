#!/usr/bin/env python3
"""
One-time tool to generate a new Ed25519 keypair for Machine Portal licensing.

Run this ONCE to set up a new installation. Store private.key securely and
never commit it to source control. Copy the printed public key hex into
dashboard/licensing.py as _PUBLIC_KEY_HEX.

Usage:
    python generate_keypair.py
"""
import os
import sys

try:
    from nacl.signing import SigningKey
except ImportError:
    sys.exit("ERROR: Install PyNaCl first:  pip install PyNaCl")


def main():
    sk = SigningKey.generate()
    seed_hex = bytes(sk).hex()
    pub_hex  = bytes(sk.verify_key).hex()

    key_path = os.path.join(os.path.dirname(__file__), "private.key")
    with open(key_path, "w") as f:
        f.write(seed_hex + "\n")

    print(f"\nPrivate key saved to: {key_path}")
    print("KEEP THIS SECRET AND OFFLINE. Never commit it to source control.\n")
    print("Paste this line into dashboard/licensing.py:")
    print(f'\n    _PUBLIC_KEY_HEX = "{pub_hex}"\n')


if __name__ == "__main__":
    main()
