# Copyright (c) 2025 Hayato Yamamoto
# SPDX-License-Identifier: MIT
"""Checks on the package structure that the snapshot does not cover."""

from __future__ import annotations

import jaconv

import jaconv_domino
import jaconv_domino.phoneme


def test_phoneme_module_keeps_old_import_path() -> None:
    """``jaconv_domino.phoneme`` re-exports the same objects as the package."""
    for exported_name in jaconv_domino.phoneme.__all__:
        assert getattr(jaconv_domino.phoneme, exported_name) is getattr(
            jaconv_domino,
            exported_name,
        )


def test_every_name_in_all_exists() -> None:
    """Every name listed in ``__all__`` is defined."""
    for exported_name in jaconv_domino.__all__:
        assert hasattr(jaconv_domino, exported_name)


JACONV_0_5_0_PUBLIC_NAMES = [
    "hira2kata",
    "hira2hkata",
    "kata2hira",
    "h2z",
    "z2h",
    "hankaku2zenkaku",
    "zenkaku2hankaku",
    "han2zen",
    "zen2han",
    "normalize",
    "kana2alphabet",
    "alphabet2kana",
    "kata2alphabet",
    "alphabet2kata",
    "hiragana2julius",
    "enlarge_smallkana",
    "enlargesmallkana",
]


def test_every_jaconv_function_is_available() -> None:
    """All names in ``jaconv.__all__`` of jaconv 0.5.0 are exported."""
    assert set(JACONV_0_5_0_PUBLIC_NAMES) <= set(jaconv_domino.__all__)


def test_jaconv_functions_are_re_exported() -> None:
    """The jaconv functions are re-exported as they are, except the alias."""
    for public_name in JACONV_0_5_0_PUBLIC_NAMES:
        if public_name == "enlargesmallkana":
            continue
        assert getattr(jaconv_domino, public_name) is getattr(jaconv, public_name)
    assert jaconv_domino.enlargesmallkana is jaconv.enlarge_smallkana
