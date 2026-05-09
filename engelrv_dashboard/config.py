import json
import os
import uuid
from dataclasses import dataclass, field, asdict
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
    id: str = field(default_factory=lambda: str(uuid.uuid4()))


@dataclass
class Settings:
    ssh_local_port: int = 10060
    ssh_remote_port: int = 5900
    vnc_port: int = 5900
    tunnel_wait_seconds: int = 3


def _default_config():
    return {"machines": [], "settings": asdict(Settings())}


def load() -> tuple[List[Machine], Settings]:
    if not os.path.exists(CONFIG_FILE):
        return [], Settings()
    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        machines = [Machine(**m) for m in data.get("machines", [])]
        settings = Settings(**data.get("settings", {}))
        return machines, settings
    except Exception:
        return [], Settings()


def save(machines: List[Machine], settings: Settings) -> None:
    os.makedirs(CONFIG_DIR, exist_ok=True)
    data = {
        "machines": [asdict(m) for m in machines],
        "settings": asdict(settings),
    }
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
