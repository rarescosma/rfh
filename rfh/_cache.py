"""Idiotic JSON cache."""
from contextlib import suppress
from functools import update_wrapper
from pathlib import Path
from typing import Any, Callable, Union

from rfh._json import load, save


def cached_load(cache_file: Path) -> Callable:
    """Cache decorated function operation to a JSON file."""

    def decorating_function(user_fn: Callable) -> Callable:
        wrapper = _cached_load_wrapper(user_fn, cache_file)
        return update_wrapper(wrapper, user_fn)

    return decorating_function


def _cached_load_wrapper(user_fn: Callable, cache_file: Path) -> Callable:
    def wrapper(*args: Any, **kwargs: Any) -> Union[dict, list]:
        with suppress(Exception):
            cached_data = load(cache_file)
            if cached_data:
                return cached_data

        live_data = user_fn(*args, **kwargs)
        if live_data:
            save(cache_file, live_data)
        return live_data

    return wrapper
