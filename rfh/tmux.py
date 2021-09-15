"""Tmux helper."""
from dataclasses import dataclass
from functools import lru_cache
from typing import Iterable, List, NewType

import i3ipc
import sh

TMUX_WIN_NAME_PREFIX: str = "tmux"
TMUX_LIST_FORMAT: str = "#{session_name}:#{window_index}:#{window_name}"
TERMINAL_CMD: str = "alacritty -e sh -c "
PREFIX: str = "rfh - "

WinSpec = NewType("WinSpec", str)


@lru_cache(maxsize=1)
def _tmux_client() -> sh.Command:
    return getattr(sh, "tmux")


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
    def list_windows() -> Iterable[WinSpec]:
        cmd = _tmux_client()("list-windows", "-a", "-F", TMUX_LIST_FORMAT)
        try:
            return [WinSpec(_) for _ in cmd.wait().splitlines() if _]
        except sh.ErrorReturnCode:
            return []


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
    return [WinSpec(f"{PREFIX}{win}") for win in Tmux.list_windows()]


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
