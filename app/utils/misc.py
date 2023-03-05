from functools import lru_cache
from pathlib import Path

import toml

PYPROJECT_PATH = Path(__file__).parent.parent.parent / "pyproject.toml"


@lru_cache()
def get_version() -> str:
    with PYPROJECT_PATH.open() as f:
        pyproject = toml.load(f)
    return pyproject["tool"]["poetry"]["version"]  # type: ignore[no-any-return]
