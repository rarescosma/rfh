""" Rofi helpers. """
import os
import subprocess
import sys
from functools import wraps
from typing import Callable
from unittest.mock import patch

import click
import sh

from rfh import tmux, tuya
from rfh.version import __version__


def monkey_patch_pyi(thing: Callable, env_key: str = "env") -> Callable:
    """
    used to monkeypatch subprocess primitives for pyinstaller compatibility
    see https://github.com/pyinstaller/pyinstaller/tree/master/doc/runtime-information.rst
    """

    @wraps(thing)
    def inner(*args, **kwargs):  # type: ignore
        os_env = dict(os.environ)
        lp_key = "LD_LIBRARY_PATH"
        lp_orig = os_env.get(lp_key + "_ORIG")
        kwargs[env_key] = kwargs.get("env", os_env)
        if lp_orig is not None:
            kwargs[env_key][lp_key] = lp_orig
        else:
            kwargs[env_key].pop(lp_key, None)
        return thing(*args, **kwargs)

    return inner


@click.command()
@click.argument("spec", required=False, nargs=-1)
@click.version_option(__version__)
def main(spec: str = "") -> None:
    """Entrypoint."""
    patch(
        "subprocess.Popen", monkey_patch_pyi(subprocess.Popen), spec=True
    ).start()
    patch(
        "sh.Command.bake", monkey_patch_pyi(sh.Command.bake, env_key="_env")
    ).start()

    if not spec:
        for thing in [*tmux.list_windows(), *tuya.list_devices()]:
            print(thing)
        sys.exit(0)

    namespace, *spec_parts = " ".join(spec).split()
    spec = " ".join(spec_parts)

    if namespace == "tmux":
        tmux.switch_window(tmux.WinSpec(spec))
    elif namespace == "tuya":
        subprocess.Popen(
            ["nohup", "rfh", "tuya-flip", spec],
            stdout=open("/dev/null", "w", encoding="utf-8"),
            stderr=open("/dev/null", "w", encoding="utf-8"),
            preexec_fn=os.setpgrp,
        )
    elif namespace == "tuya-flip":
        tuya.flip_device(tuya.DevSpec(spec))


if __name__ == "__main__":
    main()
