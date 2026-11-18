# Copyright (c) 2025 Hayato Yamamoto
# SPDX-License-Identifier: MIT
"""Compatibility module for ``from jaconv_domino.phoneme import ...``.

The implementation moved to ``jaconv_domino.converters`` and
``jaconv_domino.tables``. New code should import from ``jaconv_domino``.
"""

from __future__ import annotations

from jaconv_domino.converters.kana import (
    domino2hiragana,
    domino2hiragana_with_timing,
    domino_csv2hiragana,
    domino_csv2hiragana_csv,
)
from jaconv_domino.converters.phoneme import (
    hiragana2domino,
    hiragana2domino_with_mapping,
    hiragana_csv2domino,
)
from jaconv_domino.tables.domino import (
    DOMINO_TO_HIRAGANA_MAP,
    HIRAGANA_TO_DOMINO_MAP,
)

__all__ = [
    "DOMINO_TO_HIRAGANA_MAP",
    "HIRAGANA_TO_DOMINO_MAP",
    "domino2hiragana",
    "domino2hiragana_with_timing",
    "domino_csv2hiragana",
    "domino_csv2hiragana_csv",
    "hiragana2domino",
    "hiragana2domino_with_mapping",
    "hiragana_csv2domino",
]
