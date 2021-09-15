import os
import subprocess
import sys

import click

from rfh import tmux, tuya


@click.command()
@click.argument("spec", required=False, nargs=-1)
def main(spec: str):
    """Entrypoint."""
    if not spec:
        for thing in [*tmux.list_windows(), *tuya.list_devices()]:
            print(thing)
        sys.exit(0)

    namespace, spec, *_ = " ".join(spec).split()

    if namespace == "tmux":
        tmux.switch_window(tmux.WinSpec(spec))
    elif namespace == "tuya":
        subprocess.Popen(
            ["nohup", "rfh", "tuya-flip", spec],
            stdout=open("/dev/null", "w"),
            stderr=open("/dev/null", "w"),
            preexec_fn=os.setpgrp,
        )
    elif namespace == "tuya-flip":
        tuya.flip_device(tuya.DevSpec(spec))


if __name__ == "__main__":
    main()
