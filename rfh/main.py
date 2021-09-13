import os
import subprocess
import sys

import click

from rfh import tmux, tuya


@click.group()
def main():
    """Entrypoint."""


@main.command(name="tmux")
@click.argument("window_spec", default=None, required=False)
def _tmux(window_spec: str) -> None:
    if window_spec is None:
        for win in tmux.list_windows():
            print(win)
        sys.exit(0)

    tmux.switch_window(tmux.WinSpec(window_spec))


@main.command(name="tuya")
@click.argument("device_spec", default=None, required=False)
def _tuya(device_spec: str) -> None:
    if device_spec is None:
        for device in tuya.list_devices():
            print(device)
        sys.exit(0)

    subprocess.Popen(
        ["nohup", "rfh", "tuya-flip-real", device_spec],
        stdout=open("/dev/null", "w"),
        stderr=open("/dev/null", "w"),
        preexec_fn=os.setpgrp,
    )


@main.command()
@click.argument("device_spec", required=True)
def tuya_flip_real(device_spec: str) -> None:
    tuya.flip_device(tuya.DevSpec(device_spec))


if __name__ == '__main__':
    main()
