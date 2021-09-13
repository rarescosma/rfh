"""Tuya helper."""
from functools import lru_cache
from pathlib import Path
from typing import Callable, List, NewType

from lenses import lens
from lenses.ui import BaseUiLens
from tuyapy import TuyaApi
from tuyapy.devices.factory import get_tuya_device
from tuyapy.tuyaapi import SESSION as TuyaSession

from rfh._cache import cached_load
from rfh._json import load, save

from xdg import xdg_config_home

DevSpec = NewType("DevSpec", str)

PREFIX: str = "rfh - "
_REPO: Path = xdg_config_home() / "rfh" / "tuya"

CONFIG_FILE: Path = _REPO / "config.json"
AUTH_FILE: Path = _REPO / "auth.json"
DEVICES_FILE: Path = _REPO / "devices.json"


@lru_cache(maxsize=1)
def _tuya_client() -> TuyaApi:
    config = {**load(CONFIG_FILE), **load(AUTH_FILE)}
    auth_keys = ["accessToken", "refreshToken", "expireTime"]

    for conf_key in config:
        setattr(TuyaSession, conf_key, config[conf_key])

    api = TuyaApi()
    api.check_access_token()

    if (
        TuyaSession.accessToken is not None
        and TuyaSession.accessToken != config.get("accessToken")
    ):
        save(AUTH_FILE, {k: getattr(TuyaSession, k) for k in auth_keys})

    return api


@cached_load(DEVICES_FILE)
def _discover_devices() -> list[dict]:
    return _tuya_client().discover_devices()


def _make_spec(dev: dict) -> str:
    return PREFIX + ":".join(
        [dev["name"].lower(), "off" if dev["data"]["state"] else "on"]
    )


def _dev_by_name(dev_name: str) -> BaseUiLens:
    return lens.Each().Filter(
        lambda x: x.get("name", "").lower() == dev_name.lower()
    )


def _flip_cache(dev_filter: BaseUiLens) -> Callable:
    focus_state = lens.Get("data", {}).Get("state")
    return (dev_filter & focus_state).modify(lambda x: not x)


def _flip_device(dev: dict) -> None:
    instance = get_tuya_device(dev, _tuya_client())[0]
    if instance.state():
        instance.turn_off()
    else:
        instance.turn_on()


def list_devices() -> List[DevSpec]:
    switch_filter = lens.Each().Filter(lambda x: x["dev_type"] == "switch")
    return (switch_filter & lens.F(_make_spec)).collect()(_discover_devices())


def flip_device(dev_spec: DevSpec) -> None:
    name, *_ = dev_spec.removeprefix(PREFIX).split(":")

    devices, dev_filter = _discover_devices(), _dev_by_name(name)

    if matching := dev_filter.collect()(devices):
        _flip_device(matching[0])
        save(DEVICES_FILE, _flip_cache(dev_filter)(devices))
