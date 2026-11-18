# Copyright (c) 2025 Hayato Yamamoto
# SPDX-License-Identifier: MIT
"""Check that every public function still returns the recorded outputs."""

from __future__ import annotations

import gzip
import json
from pathlib import Path

import pytest
from snapshot_corpus import record_outputs

SNAPSHOT_PATH = Path(__file__).resolve().parent / "snapshots" / "outputs.json.gz"
with gzip.open(SNAPSHOT_PATH, "rt", encoding="utf-8") as snapshot_file:
    EXPECTED_OUTPUTS = json.load(snapshot_file)
ACTUAL_OUTPUTS = json.loads(json.dumps(record_outputs(), ensure_ascii=False))


@pytest.mark.parametrize("section_name", sorted(EXPECTED_OUTPUTS))
def test_section_matches_snapshot(section_name: str) -> None:
    """Each section of the snapshot is reproduced exactly."""
    expected_section = EXPECTED_OUTPUTS[section_name]
    actual_section = ACTUAL_OUTPUTS.get(section_name)
    if isinstance(expected_section, dict):
        differing_inputs = [
            input_text
            for input_text, expected_value in expected_section.items()
            if actual_section.get(input_text) != expected_value
        ]
        assert not differing_inputs, differing_inputs[:20]
        assert set(actual_section) == set(expected_section)
    else:
        assert actual_section == expected_section
