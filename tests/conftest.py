from __future__ import annotations

from pathlib import Path

import pytest


@pytest.fixture
def sample_config_path() -> Path:
    return Path(__file__).parents[1] / "configs" / "sample.toml"
