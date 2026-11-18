# Copyright (c) 2025 Hayato Yamamoto
# SPDX-License-Identifier: MIT
"""Checks that the pydomino converters produce input that pydomino accepts."""

from __future__ import annotations

import itertools
from pathlib import Path

import pytest

import jaconv_domino
from jaconv_domino.tables.domino import (
    DOMINO_PHONEMES,
    DOMINO_TO_HIRAGANA_MAP,
    HIRAGANA_TO_DOMINO_MAP,
    PAUSE_PHONEME,
)

TRANSITIONS_PATH = (
    Path(__file__).resolve().parent / "data" / "pydomino_phoneme_transitions.txt"
)
ALLOWED_TRANSITIONS = frozenset(
    tuple(line.split())
    for line in TRANSITIONS_PATH.read_text(encoding="utf-8").splitlines()
    if line.strip()
)

HIRAGANA_CHARACTERS = [chr(code_point) for code_point in range(0x3041, 0x3097)] + list(
    "゛゜ゝゞー"
)
KATAKANA_CHARACTERS = [chr(code_point) for code_point in range(0x30A1, 0x30FB)] + list(
    "ーヽヾ"
)


def _find_invalid_transitions(phonemes: str) -> list[tuple[str, str]]:
    """Return adjacent phoneme pairs that pydomino does not accept."""
    phoneme_list = phonemes.split()
    return [
        (previous_phoneme, next_phoneme)
        for previous_phoneme, next_phoneme in zip(phoneme_list, phoneme_list[1:])
        if (previous_phoneme, next_phoneme) not in ALLOWED_TRANSITIONS
    ]


def test_transition_table_uses_the_39_phonemes() -> None:
    """The vendored transition table and ``DOMINO_PHONEMES`` agree."""
    used_phonemes = {phoneme for pair in ALLOWED_TRANSITIONS for phoneme in pair}
    assert used_phonemes == DOMINO_PHONEMES
    assert len(DOMINO_PHONEMES) == 39


# Copied from ``unvoice_i_and_u`` in pydomino's src/phoneme_transition.cpp.
DEVOICING_PREVIOUS_PHONEMES = frozenset(
    {"k", "ky", "ch", "ts", "sh", "s", "hy", "h", "f", "py", "p", "t"},
)
DEVOICING_NEXT_PHONEMES = DEVOICING_PREVIOUS_PHONEMES | {PAUSE_PHONEME}


def _devoice_like_pydomino(phoneme_list: list[str]) -> list[str]:
    """Turn ``i`` and ``u`` into ``I`` and ``U`` as pydomino does before alignment."""
    devoiced_list = list(phoneme_list)
    for position in range(1, len(phoneme_list) - 1):
        if (
            phoneme_list[position] in {"i", "u"}
            and phoneme_list[position - 1] in DEVOICING_PREVIOUS_PHONEMES
            and phoneme_list[position + 1] in DEVOICING_NEXT_PHONEMES
        ):
            devoiced_list[position] = phoneme_list[position].upper()
    return devoiced_list


def _find_problems(input_text: str) -> list[str]:
    """Describe why the output for ``input_text`` would be rejected."""
    phonemes = jaconv_domino.hiragana2domino(input_text)
    if not phonemes:
        return []
    phoneme_list = phonemes.split()
    problems = []
    if phoneme_list[0] != PAUSE_PHONEME or phoneme_list[-1] != PAUSE_PHONEME:
        problems.append("not wrapped with pau")
    unknown_phonemes = set(phoneme_list) - DOMINO_PHONEMES
    if unknown_phonemes:
        problems.append(f"unknown phonemes {sorted(unknown_phonemes)}")
    for checked_list in (phoneme_list, _devoice_like_pydomino(phoneme_list)):
        invalid_transitions = _find_invalid_transitions(" ".join(checked_list))
        if invalid_transitions:
            problems.append(f"invalid transitions {invalid_transitions}")
    return problems


def test_devoicing_follows_pydomino() -> None:
    """The copied devoicing rule gives the example from the README."""
    assert _devoice_like_pydomino(["pau", "k", "i", "k", "u", "pau"]) == [
        "pau",
        "k",
        "I",
        "k",
        "U",
        "pau",
    ]
    assert _devoice_like_pydomino(["pau", "k", "i", "N", "pau"]) == [
        "pau",
        "k",
        "i",
        "N",
        "pau",
    ]


def test_output_is_accepted_by_pydomino() -> None:
    """Every output starts and ends with pau and uses allowed transitions."""
    input_texts = [
        first_character + second_character
        for first_character, second_character in itertools.product(
            HIRAGANA_CHARACTERS + KATAKANA_CHARACTERS,
            repeat=2,
        )
    ]
    input_texts += list(HIRAGANA_TO_DOMINO_MAP)
    problems_by_input = {
        input_text: problems
        for input_text in input_texts
        if (problems := _find_problems(input_text))
    }
    assert problems_by_input == {}


def test_reverse_table_uses_the_39_phonemes() -> None:
    """Keys of ``DOMINO_TO_HIRAGANA_MAP`` use only pydomino phonemes."""
    for phoneme_key in DOMINO_TO_HIRAGANA_MAP:
        assert set(phoneme_key) <= DOMINO_PHONEMES


@pytest.mark.parametrize(
    ("input_text", "expected_phonemes"),
    [
        ("ありがとう", "pau a r i g a t o u pau"),
        ("きく", "pau k i k u pau"),
        ("にひみりぎびぴ", "pau n i h i m i r i g i b i p i pau"),
        ("しちじぢ", "pau sh i ch i j i j i pau"),
        ("らーめん", "pau r a a m e N pau"),
        ("ーあ", "pau a pau"),
        ("んー", "pau N pau"),
        ("かぁさん", "pau k a a s a N pau"),
        ("ゔぁいおりん", "pau v a i o r i N pau"),
        ("う゛ぃ", "pau v i pau"),
        ("ぶゃ", "pau b u y a pau"),
        ("ずゃ", "pau j a pau"),
        ("てゅーば", "pau ch u u b a pau"),
        ("っっか", "pau cl k a pau"),
        ("カタカナ", "pau k a t a k a n a pau"),
        ("ﾃｨﾛﾌｨﾅｰﾚ", "pau t i r o f i n a a r e pau"),
        ("Abc、。", ""),
        ("あ\n\nい", "pau a pau i pau"),
    ],
)
def test_hiragana2domino_examples(input_text: str, expected_phonemes: str) -> None:
    """Representative conversions follow the agreed rules."""
    assert jaconv_domino.hiragana2domino(input_text) == expected_phonemes


def test_mapping_matches_phonemes() -> None:
    """The mapping lists the same phonemes as the string, without pau."""
    phonemes, mapping = jaconv_domino.hiragana2domino_with_mapping("らーめん\nっっか")
    assert phonemes == "pau r a a m e N pau cl k a pau"
    assert mapping == [
        ("ら", ["r", "a"]),
        ("ー", ["a"]),
        ("め", ["m", "e"]),
        ("ん", ["N"]),
        ("っ", ["cl"]),
        ("っ", []),
        ("か", ["k", "a"]),
    ]
    mapped_phonemes = [
        phoneme for _, phoneme_list in mapping for phoneme in phoneme_list
    ]
    assert [
        phoneme for phoneme in phonemes.split() if phoneme != PAUSE_PHONEME
    ] == mapped_phonemes


@pytest.mark.parametrize(
    ("phonemes", "expected_hiragana"),
    [
        ("pau k I k U pau", "きく"),
        ("pau ky i pau", "き"),
        ("pau k i pau", "き"),
        ("pau v u pau", "ゔ"),
        ("pau j i pau", "じ"),
    ],
)
def test_domino2hiragana_examples(phonemes: str, expected_hiragana: str) -> None:
    """Devoiced vowels and both palatalization styles are read back."""
    assert jaconv_domino.domino2hiragana(phonemes) == expected_hiragana


def test_timing_reads_devoiced_vowels() -> None:
    """Alignment output with ``I`` and ``U`` keeps every kana."""
    phoneme_timings = [
        ("pau", 0.0, 0.1),
        ("k", 0.1, 0.15),
        ("I", 0.15, 0.2),
        ("k", 0.2, 0.25),
        ("U", 0.25, 0.3),
        ("pau", 0.3, 0.4),
    ]
    assert jaconv_domino.domino2hiragana_with_timing(phoneme_timings) == [
        ("き", 0.1, 0.2),
        ("く", 0.2, 0.3),
    ]


@pytest.mark.parametrize("hiragana", sorted(HIRAGANA_TO_DOMINO_MAP))
def test_round_trip_keeps_phonemes(hiragana: str) -> None:
    """Converting back to hiragana and forward again gives the same phonemes."""
    phonemes = jaconv_domino.hiragana2domino(hiragana)
    assert jaconv_domino.hiragana2domino(jaconv_domino.domino2hiragana(phonemes)) == (
        phonemes
    )
