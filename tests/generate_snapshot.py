# Copyright (c) 2025 Hayato Yamamoto
# SPDX-License-Identifier: MIT
"""Write the output snapshot that ``test_snapshot.py`` compares against.

Run this only when a change of output is intended:

    python tests/generate_snapshot.py
"""

from __future__ import annotations

import gzip
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from snapshot_corpus import record_outputs

SNAPSHOT_PATH = Path(__file__).resolve().parent / "snapshots" / "outputs.json.gz"


def main() -> None:
    """Record the current outputs and save them as JSON."""
    outputs = record_outputs()
    serialized = json.dumps(outputs, ensure_ascii=False, indent=1, sort_keys=True)
    with gzip.open(SNAPSHOT_PATH, "wt", encoding="utf-8") as snapshot_file:
        snapshot_file.write(serialized + "\n")
    print(f"wrote {SNAPSHOT_PATH}")


if __name__ == "__main__":
    main()
