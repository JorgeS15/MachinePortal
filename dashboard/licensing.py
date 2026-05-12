import hashlib
import hmac
import os
import subprocess
import uuid
from datetime import date, datetime

try:
    import winreg as _winreg
except ImportError:
    _winreg = None

import config as _cfg

# ── Signing secret ────────────────────────────────────────────────────────────
# Change this to a long random string before distributing. Never share it.
_SECRET = b"g1wAv940gtgvEaMU4QEv6YViQSPHJj26rKvs7HiV64EB0wK24U8l1TtMl84MzYWE"

LICENSE_FILE = os.path.join(_cfg.CONFIG_DIR, "license.key")


# ── Hardware fingerprint ──────────────────────────────────────────────────────

_fingerprint_cache: str | None = None


def get_machine_fingerprint() -> str:
    """Stable SHA-256 fingerprint of this machine's hardware (uppercase hex)."""
    global _fingerprint_cache
    if _fingerprint_cache is not None:
        return _fingerprint_cache

    parts = []

    if _winreg:
        try:
            key = _winreg.OpenKey(
                _winreg.HKEY_LOCAL_MACHINE,
                r"SOFTWARE\Microsoft\Cryptography",
            )
            parts.append(_winreg.QueryValueEx(key, "MachineGuid")[0])
        except Exception:
            pass

    try:
        out = subprocess.check_output(
            ["wmic", "baseboard", "get", "SerialNumber"],
            text=True,
            timeout=5,
            creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
        )
        serial = out.strip().splitlines()[-1].strip()
        if serial and serial.lower() not in ("serialnumber", "to be filled by o.e.m.", ""):
            parts.append(serial)
    except Exception:
        pass

    parts.append(str(uuid.getnode()))

    combined = "|".join(parts) if parts else "fallback"
    _fingerprint_cache = hashlib.sha256(combined.encode()).hexdigest().upper()
    return _fingerprint_cache


def get_display_id() -> str:
    """User-friendly 19-char device ID shown in the activation dialog (XXXX-XXXX-XXXX-XXXX)."""
    fp = get_machine_fingerprint()[:16]
    return "-".join(fp[i:i + 4] for i in range(0, 16, 4))


# ── Key generation & verification ────────────────────────────────────────────

def _sign(fp8: str, expiry: str) -> str:
    msg = f"{fp8}|{expiry}".encode()
    return hmac.new(_SECRET, msg, hashlib.sha256).hexdigest().upper()[:16]


def generate_key(fingerprint: str, expiry: str = "LIFETIME") -> str:
    """Generate a license key for a given fingerprint (or display ID)."""
    fp8 = fingerprint.replace("-", "").upper().replace("O", "0")[:8]
    expiry = expiry.upper()
    return f"{fp8}-{expiry}-{_sign(fp8, expiry)}"


def verify_key(key: str) -> tuple[bool, str]:
    """Verify a license key against the current machine. Returns (valid, message)."""
    key = key.strip().upper().replace(" ", "")
    parts = key.split("-")

    if len(parts) != 3:
        return False, "Invalid key format (expected XXXXXXXX-EXPIRY-XXXXXXXXXXXXXXXX)."

    fp8, expiry, sig = parts

    if len(fp8) != 8 or len(sig) != 16:
        return False, "Invalid key format."

    my_fp8 = get_machine_fingerprint()[:8].upper()
    if fp8 != my_fp8:
        return False, "This license key is not valid for this machine."

    if expiry != "LIFETIME":
        try:
            exp_date = datetime.strptime(expiry, "%Y%m%d").date()
            if date.today() > exp_date:
                return False, f"License expired on {exp_date.strftime('%Y-%m-%d')}."
        except ValueError:
            return False, "Invalid expiry date in key."

    if not hmac.compare_digest(sig, _sign(fp8, expiry)):
        return False, "License key signature is invalid."

    return True, "OK"


# ── Persistence ───────────────────────────────────────────────────────────────

def load_license() -> str:
    try:
        with open(LICENSE_FILE, "r", encoding="utf-8") as f:
            return f.read().strip()
    except FileNotFoundError:
        return ""


def save_license(key: str) -> None:
    os.makedirs(_cfg.CONFIG_DIR, exist_ok=True)
    with open(LICENSE_FILE, "w", encoding="utf-8") as f:
        f.write(key.strip())


def check_license() -> tuple[bool, str]:
    """Return (valid, message) for the saved license on this machine."""
    key = load_license()
    if not key:
        return False, "No license found."
    return verify_key(key)
