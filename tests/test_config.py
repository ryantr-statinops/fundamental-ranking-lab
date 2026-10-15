from __future__ import annotations

from pathlib import Path

import pytest
from pydantic import ValidationError

from fundamental_ranking_lab.config import AppConfig, load_config


def test_load_sample_config_and_fingerprint(sample_config_path: Path) -> None:
    config = load_config(sample_config_path)
    assert config.research.sector_cap == 0.20
    assert len(config.research_fingerprint()) == 64
    assert len(config.execution_fingerprint()) == 64


def test_operational_paths_do_not_change_research_fingerprint() -> None:
    base = AppConfig()
    changed = AppConfig.model_validate(
        {
            "paths": {"data_dir": "D:/elsewhere", "artifact_dir": "E:/artifacts"},
            "research": base.research.model_dump(),
        }
    )
    assert changed.research_fingerprint() == base.research_fingerprint()
    assert changed.execution_fingerprint() != base.execution_fingerprint()


def test_unknown_config_keys_are_rejected() -> None:
    with pytest.raises(ValidationError):
        AppConfig.model_validate({"research": {"unknown_switch": True}})


def test_invalid_caps_are_rejected() -> None:
    with pytest.raises(ValidationError):
        AppConfig.model_validate({"research": {"company_cap": 1.1}})
