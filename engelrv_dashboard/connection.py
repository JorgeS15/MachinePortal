import os
import sys
import time
import shutil
import tempfile
import subprocess
import threading
import logging
import traceback
from dataclasses import dataclass
from typing import Optional

from config import Machine, Settings

# Log to a file next to the executable (or script) so errors survive windowless runs.
_log_path = os.path.join(os.path.dirname(sys.executable if getattr(sys, "frozen", False) else __file__), "engelrv.log")
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
    tmp_dir = tempfile.mkdtemp(prefix="engelrv_")
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
                    "-L", f"{settings.ssh_local_port}:localhost:{settings.ssh_remote_port}",
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

            vnc_target = f"localhost::{settings.ssh_local_port}"
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
