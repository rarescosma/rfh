""" Rofi helpers. """
import os
import subprocess
import sys

import click

from rfh import tmux, tuya
from rfh.version import __version__


@click.command()
@click.argument("spec", required=False, nargs=-1)
@click.version_option(__version__)
def main(spec: str = "") -> None:
    """Entrypoint."""
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
