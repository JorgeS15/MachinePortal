import json
import os
import uuid
from dataclasses import dataclass, field, fields, asdict
from typing import List

CONFIG_DIR = os.path.join(os.environ.get("APPDATA", os.path.expanduser("~")), "EngelRV")
CONFIG_FILE = os.path.join(CONFIG_DIR, "machines.json")


@dataclass
class Machine:
    name: str
    ip: str
    ssh: bool = False
    ssh_user: str = "user"
    ssh_password: str = ""
    port: int = 10062      # unique SSH local-forwarding port per machine
    id: str = field(default_factory=lambda: str(uuid.uuid4()))


@dataclass
class Settings:
    ssh_port_start: int = 10062    # first port to assign to new machines
    ssh_remote_port: int = 5900    # VNC port on the remote host
    vnc_port: int = 5900           # VNC port for direct (non-SSH) connections
    tunnel_wait_seconds: int = 3
    default_ssh_user: str = ""
    default_ssh_password: str = ""


def _filter(dc_type, data: dict) -> dict:
    valid = {f.name for f in fields(dc_type)}
    return {k: v for k, v in data.items() if k in valid}


def load() -> tuple[List[Machine], Settings]:
    if not os.path.exists(CONFIG_FILE):
        return [], Settings()
    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        machines = [Machine(**_filter(Machine, m)) for m in data.get("machines", [])]
        settings = Settings(**_filter(Settings, data.get("settings", {})))
        return machines, settings
    except Exception:
        return [], Settings()


def load_from(path: str) -> tuple[List[Machine], Settings]:
    """Load config from an arbitrary file path (used for import/restore)."""
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    machines = [Machine(**_filter(Machine, m)) for m in data.get("machines", [])]
    settings = Settings(**_filter(Settings, data.get("settings", {})))
    return machines, settings


def save(machines: List[Machine], settings: Settings) -> None:
    os.makedirs(CONFIG_DIR, exist_ok=True)
    data = {
        "machines": [asdict(m) for m in machines],
        "settings": asdict(settings),
    }
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
