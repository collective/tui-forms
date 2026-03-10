from pathlib import Path

import json
import pytest


@pytest.fixture(scope="session")
def resources_folder():
    path = (Path(__file__).parent / "_resources").resolve()

    return path


@pytest.fixture(scope="session")
def load_schema(resources_folder):
    def _load_schema(name: str) -> dict:
        with open(resources_folder / name) as f:
            return json.load(f)

    return _load_schema
