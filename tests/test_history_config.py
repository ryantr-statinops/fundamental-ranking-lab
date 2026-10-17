from datetime import UTC, datetime

import pytest
from pydantic import ValidationError

from fundamental_ranking_lab.history_config import HistorySettings
from fundamental_ranking_lab.history_contracts import Evidence


def test_history_settings_are_strict_and_chronological() -> None:
    with pytest.raises(ValidationError):
        HistorySettings(bundle_path="bundle.json", unexpected=True)
    with pytest.raises(ValidationError):
        HistorySettings(bundle_path="bundle.json", signal_end="2000-01-01")


def test_evidence_requires_public_utc_time_and_interval() -> None:
    row = dict(
        evidence_id="a",
        revision_id="1",
        kind="industry",
        entity_id="e",
        source="fixture",
        source_record_id="a",
        raw_sha256="0" * 64,
        known_at=datetime(2009, 1, 1, tzinfo=UTC),
        valid_from="2009-01-01",
    )
    assert Evidence.model_validate(row).known_at.year == 2009
    with pytest.raises(ValidationError):
        Evidence.model_validate({**row, "known_at": "2009-01-01T00:00:00"})
    with pytest.raises(ValidationError):
        Evidence.model_validate({**row, "valid_to": "2008-01-01"})
