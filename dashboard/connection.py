import os
import sys
import time
import shutil
import tempfile
import subprocess
import threading
import logging
import traceback
import platform
from dataclasses import dataclass
from typing import Optional

import config as _cfg
from config import Machine, Settings

# Log to the config directory so the log file is always writable.
os.makedirs(_cfg.CONFIG_DIR, exist_ok=True)
_log_path = os.path.join(_cfg.CONFIG_DIR, "machineportal.log")
logging.basicConfig(
    filename=_log_path,
    level=logging.DEBUG,
    format="%(asctime)s %(levelname)s %(message)s",
)


def _asset_path(filename: str) -> str:
    """Resolve path to a bundled asset, works both in dev and PyInstaller .exe."""
    if getattr(sys, "frozen", False):
        # PyInstaller extracts datas into _MEIPASS/<dest_dir>/filename
        base = os.path.join(sys._MEIPASS, "assets")  # type: ignore[attr-defined]
    else:
        base = os.path.join(os.path.dirname(__file__), "assets")
    return os.path.join(base, filename)


def _extract_to_temp(filename: str) -> str:
    """Copy a bundled .exe to a temp directory so it can be executed."""
    src = _asset_path(filename)
    tmp_dir = tempfile.mkdtemp(prefix="machineportal_")
    dst = os.path.join(tmp_dir, filename)
    shutil.copy2(src, dst)
    return dst, tmp_dir


@dataclass
class ActiveConnection:
    machine: Machine
    plink_proc: Optional[subprocess.Popen]
    vnc_proc: Optional[subprocess.Popen]
    tmp_dirs: list


_active: dict[str, ActiveConnection] = {}
_lock = threading.Lock()

# ── Ping state ────────────────────────────────────────────────────────────────
_ping_state: dict[str, bool | None] = {}   # None = not yet polled
_ping_lock  = threading.Lock()


def ping_host(ip: str) -> bool:
    """Send one ICMP ping; return True if host replies."""
    if platform.system() == "Windows":
        cmd = ["ping", "-n", "1", "-w", "500", ip]
    else:
        cmd = ["ping", "-c", "1", "-W", "1", ip]
    try:
        kwargs: dict = {"stdout": subprocess.DEVNULL,
                        "stderr": subprocess.DEVNULL,
                        "timeout": 3}
        if sys.platform == "win32":
            # Suppress the console window that ping would otherwise flash on screen
            kwargs["creationflags"] = subprocess.CREATE_NO_WINDOW
        r = subprocess.run(cmd, **kwargs)
        return r.returncode == 0
    except Exception:
        return False


def get_ping_state(machine_id: str) -> bool | None:
    """Return last known ping result for a machine (None if not yet polled)."""
    with _ping_lock:
        return _ping_state.get(machine_id)


def start_ping_loop(machines_getter, interval: int = 5):
    """Start a daemon thread that pings every machine every `interval` seconds."""
    def _loop():
        while True:
            for m in machines_getter():
                result = ping_host(m.ip)
                with _ping_lock:
                    _ping_state[m.id] = result
            time.sleep(interval)
    threading.Thread(target=_loop, daemon=True).start()


def connect(machine: Machine, settings: Settings, on_error=None, on_done=None):
    """Start a connection to a machine in a background thread."""
    t = threading.Thread(
        target=_connect_thread,
        args=(machine, settings, on_error, on_done),
        daemon=True,
    )
    t.start()


def _connect_thread(machine: Machine, settings: Settings, on_error, on_done):
    tmp_dirs = []
    plink_proc = None

    try:
        vnc_exe, vnc_tmp = _extract_to_temp("vncviewer.exe")
        tmp_dirs.append(vnc_tmp)

        if machine.ssh:
            plink_exe, plink_tmp = _extract_to_temp("plink.exe")
            tmp_dirs.append(plink_tmp)

            plink_proc = subprocess.Popen(
                [
                    plink_exe,
                    "-N", "-batch",
                    "-pw", machine.ssh_password,
                    f"{machine.ssh_user}@{machine.ip}",
                    "-L", f"{machine.port}:localhost:{settings.ssh_remote_port}",
                ],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0,
            )

            time.sleep(settings.tunnel_wait_seconds)

            if plink_proc.poll() is not None:
                raise RuntimeError(
                    f"SSH tunnel failed to start.\n"
                    f"Check IP ({machine.ip}), username and password."
                )

            vnc_target = f"localhost::{machine.port}"
        else:
            vnc_target = f"{machine.ip}::{settings.vnc_port}"

        vnc_proc = subprocess.Popen(
            [vnc_exe, vnc_target],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )

        with _lock:
            _active[machine.id] = ActiveConnection(machine, plink_proc, vnc_proc, tmp_dirs)

        vnc_proc.wait()

    except Exception as e:
        logging.error("Connection failed for %s: %s\n%s", machine.name, e, traceback.format_exc())
        if on_error:
            on_error(str(e))
        return
    finally:
        if plink_proc and plink_proc.poll() is None:
            plink_proc.terminate()
            try:
                plink_proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                plink_proc.kill()

        with _lock:
            _active.pop(machine.id, None)

        for d in tmp_dirs:
            shutil.rmtree(d, ignore_errors=True)

    if on_done:
        on_done()


def is_connected(machine_id: str) -> bool:
    with _lock:
        conn = _active.get(machine_id)
        if not conn:
            return False
        if conn.vnc_proc and conn.vnc_proc.poll() is not None:
            return False
        return True


def disconnect(machine_id: str):
    with _lock:
        conn = _active.get(machine_id)
    if conn:
        if conn.vnc_proc and conn.vnc_proc.poll() is None:
            conn.vnc_proc.terminate()
        if conn.plink_proc and conn.plink_proc.poll() is None:
            conn.plink_proc.terminate()
