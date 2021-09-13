"""Tmux helper."""
from dataclasses import dataclass
from functools import lru_cache
from typing import Iterable, List, NewType, Optional

import i3ipc
import libtmux
from libtmux.exc import LibTmuxException

TMUX_WIN_NAME_PREFIX: str = "tmux"
TERMINAL_CMD: str = "alacritty -e sh -c "
PREFIX: str = "rfh - "

WinSpec = NewType("WinSpec", str)


@lru_cache(maxsize=1)
def _tmux_client() -> libtmux.Server:
    return libtmux.Server()


@lru_cache(maxsize=1)
def _i3_client() -> i3ipc.Connection:
    return i3ipc.Connection()


class _I3:
    @staticmethod
    def list_tmux_windows() -> List[i3ipc.con.Con]:
        return _i3_client().get_tree().find_named(rf"^{TMUX_WIN_NAME_PREFIX}\s")

    @staticmethod
    def exec(cmd: str) -> List[i3ipc.CommandReply]:
        return _i3_client().command(f"exec {cmd}")


class Tmux:
    @staticmethod
    def list_windows() -> Iterable[libtmux.Window]:
        try:
            for session in _tmux_client().list_sessions():
                yield from session.list_windows()
        except LibTmuxException:
            return []

    @staticmethod
    def window_fqn(win: libtmux.Window) -> str:
        return f"{win.session.name}:{win.index}:{win.name}"


@dataclass(frozen=True)
class _Window:
    session: str
    window_index: int

    @classmethod
    def from_spec(cls, win_spec: WinSpec) -> "_Window":
        session, window_index, *_ = win_spec.removeprefix(PREFIX).split(":")
        return cls(
            session=session,
            window_index=int(window_index),
        )

    @property
    def attach_id(self) -> str:
        return f"{self.session}:{self.window_index}"


def list_windows() -> List[WinSpec]:
    return [
        WinSpec(f"{PREFIX}{Tmux.window_fqn(win)}")
        for win in Tmux.list_windows()
    ]


def switch_window(win_spec: WinSpec) -> None:
    """Switch to target tmux window / session."""
    window = _Window.from_spec(win_spec)

    i3_tmux_wins = _I3.list_tmux_windows()
    matching_wins = [
        _
        for _ in i3_tmux_wins
        if _.window_title.startswith(f"{TMUX_WIN_NAME_PREFIX} {window.session}")
    ]

    # check if there is an terminal matching our tmux session and focus it
    # then select the desired tmux window
    if matching_wins:
        matching_wins[0].command("focus")
        _I3.exec(f"tmux select-window -t {window.attach_id}")
    # check if there's ANY terminal running tmux and focus it
    # then switch its client to the desired tmux session + window
    elif i3_tmux_wins:
        i3_tmux_wins[0].command("focus")
        _I3.exec(f"tmux switch-client -t {window.attach_id}")
    # spawn a new tmux terminal
    else:
        _I3.exec(
            f"{TERMINAL_CMD}'tmux attach-session -d -t {window.attach_id}'"
        )
