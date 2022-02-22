""" JSON primitives. """
import json
from pathlib import Path
from typing import Union


def load(file: Path) -> Union[dict, list]:
    """Attempt to load a JSON file."""
    if file.exists():
        return json.loads(file.read_text())
    return {}


def save(file: Path, data: Union[dict, list]) -> None:
    """Save to a JSON file."""
    content = json.dumps(data, sort_keys=True, indent=2)
    file.parent.mkdir(parents=True, exist_ok=True)
    file.write_text(content)
