import base64
import hashlib
import os
from datetime import date, datetime

try:
    import winreg as _winreg
except ImportError:
    _winreg = None

try:
    from nacl.signing import VerifyKey
    from nacl.exceptions import BadSignatureError
    _NACL_OK = True
except ImportError:
    _NACL_OK = False

import config as _cfg

# Public key — safe to ship. Paired private key lives offline with the vendor.
_PUBLIC_KEY_HEX = "eed2d48fd27b92192483eff5bef36a7f2d35e39ca67736570bbf7abce16bdf88"

LICENSE_FILE = os.path.join(_cfg.CONFIG_DIR, "license.key")


# ── Hardware fingerprint ──────────────────────────────────────────────────────

_fingerprint_cache: str | None = None


def get_machine_fingerprint() -> str:
    """Stable SHA-256 fingerprint of this machine's hardware (uppercase hex).

    Uses Windows MachineGuid as the sole source — it is set once on Windows
    install and survives reboots, driver updates, and network adapter changes.
    Falls back to a secondary registry key, then a fixed string, so the value
    is always deterministic even on non-Windows platforms.
    """
    global _fingerprint_cache
    if _fingerprint_cache is not None:
        return _fingerprint_cache

    source = None

    # Primary: MachineGuid — stable across updates, only changes on reinstall
    if _winreg:
        for hive, path, value in [
            (_winreg.HKEY_LOCAL_MACHINE,
             r"SOFTWARE\Microsoft\Cryptography", "MachineGuid"),
            (_winreg.HKEY_LOCAL_MACHINE,
             r"SOFTWARE\Microsoft\Windows NT\CurrentVersion", "ProductId"),
        ]:
            try:
                k = _winreg.OpenKey(hive, path)
                source = _winreg.QueryValueEx(k, value)[0]
                break
            except Exception:
                pass

    if not source:
        source = "fallback"

    _fingerprint_cache = hashlib.sha256(source.encode()).hexdigest().upper()
    return _fingerprint_cache


def get_display_id() -> str:
    """User-friendly 19-char device ID shown in the activation dialog (XXXX-XXXX-XXXX-XXXX)."""
    fp = get_machine_fingerprint()[:16]
    return "-".join(fp[i:i + 4] for i in range(0, 16, 4))


# ── Key verification ──────────────────────────────────────────────────────────

def verify_key(key: str) -> tuple[bool, str]:
    """Verify a license key against the current machine. Returns (valid, message)."""
    if not _NACL_OK:
        return False, "Licensing library (PyNaCl) not installed."

    key = key.strip().replace(" ", "")
    # maxsplit=2 because the base64url signature can itself contain '-'
    parts = key.split("-", 2)

    if len(parts) != 3:
        return False, "Invalid key format."

    fp8, expiry, sig_b64 = parts[0].upper(), parts[1].upper(), parts[2]

    if len(fp8) != 8:
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

    try:
        # Restore base64 padding stripped during key generation
        padding = 4 - len(sig_b64) % 4
        sig_bytes = base64.urlsafe_b64decode(sig_b64 + "=" * (padding % 4))
        msg = f"{fp8}|{expiry}".encode()
        vk = VerifyKey(bytes.fromhex(_PUBLIC_KEY_HEX))
        vk.verify(msg, sig_bytes)
    except BadSignatureError:
        return False, "License key signature is invalid."
    except Exception:
        return False, "Invalid key format."

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
