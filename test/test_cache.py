from pathlib import Path
from unittest.mock import MagicMock

import pytest

from rfh._cache import cached_load
from rfh._json import load


@pytest.mark.parametrize(
    "cache_content, expected, called",
    [
        ('{"a": 1}', {"a": 1}, False),
        ('{}', {"a": 1}, True),
        ('[]', {"a": 1}, True),
        ('', {"a": 1}, True),
    ],
)
def test_json_cache(tmpdir, cache_content, expected, called):
    cache_file = Path(tmpdir.join("cache.json"))
    cache_file.write_text(cache_content)

    func = MagicMock()
    func.return_value = expected

    decorated = (cached_load(cache_file))(func)
    result = decorated()

    assert result == expected
    if not called:
        func.assert_not_called()
    elif called:
        func.assert_called_once()


def test_it_updates_the_cache(tmpdir):
    cache_file = Path(tmpdir.join("cache.json"))
    cache_file.write_text("[]")

    func = MagicMock()
    func.return_value = ["abc"]

    decorated = (cached_load(cache_file))(func)
    result1 = decorated()

    assert result1 == ["abc"]
    assert load(cache_file) == ["abc"]

    _ = decorated()
    func.assert_called_once()
