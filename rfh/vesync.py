"""VeSync helper."""
from functools import lru_cache
from pathlib import Path
import sys
from typing import Dict, List, cast

from pyvesync import VeSync
from xdg import xdg_config_home

from rfh._json import load, save

PREFIX: str = "vesync "
_REPO: Path = xdg_config_home() / "rfh" / "vesync"

CONFIG_FILE: Path = _REPO / "config.json"
AUTH_FILE: Path = _REPO / "auth.json"
DEVICES_FILE: Path = _REPO / "devices.json"

SPEEDS: Dict[str, int] = {
    "sleep": 0,
    "low": 1,
    "medium": 2,
    "high": 3,
}


@lru_cache(maxsize=1)
def _vesync_client() -> VeSync:
    config = {**cast(dict, load(CONFIG_FILE)), **cast(dict, load(AUTH_FILE))}
    auth_keys = ["token", "account_id", "country_code", "enabled"]

    vs = VeSync(config["username"], config["password"], time_zone=config["time_zone"])
    for auth_key in auth_keys:
        if auth_key in config:
            setattr(vs, auth_key, config[auth_key])

    if not vs.get_devices():
        vs.login()
        save(AUTH_FILE, {k: getattr(vs, k) for k in auth_keys})

    return vs


def set_speed(speed_spec: str) -> None:
    """Set device speed."""
    speed, *_ = speed_spec.removeprefix(PREFIX).split(":")

    if speed not in SPEEDS:
        print(f"vesync: unknown speed: {speed}", file=sys.stderr, flush=True)
        return

    vs = _vesync_client()
    vs.update()
    if not vs.fans:
        print("vesync: device not found", file=sys.stderr, flush=True)
        return

    dev = vs.fans[0]
    if speed == "sleep":
        dev.sleep_mode()
    else:
        dev.change_fan_speed(SPEEDS[speed])


def list_speeds() -> List[str]:
    """Return a static list of speeds."""
    return [f"{PREFIX}{k}" for k in SPEEDS]
