# Copyright (c) 2025 Hayato Yamamoto
# SPDX-License-Identifier: MIT
"""Converters from pydomino phonemes to hiragana.

``domino2hiragana``, ``domino2hiragana_with_timing``, ``domino_csv2hiragana``
and ``domino_csv2hiragana_csv``. Conversions between kana are provided by
jaconv and re-exported from ``jaconv_domino``.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from jaconv_domino.converters._csv import (
    TIMING_ROW_FIELD_COUNT,
    find_column_index,
    iterate_row_fields,
    read_header_columns,
    split_csv_lines,
)
from jaconv_domino.tables.domino import (
    DEVOICED_TO_VOICED_VOWEL,
    DOMINO_TO_HIRAGANA_MAP,
    PAUSE_PHONEME,
)

if TYPE_CHECKING:
    from collections.abc import Sequence

HIRAGANA_CSV_HEADER = "hiragana,start,end"

# Phoneme keys tried from the longest, so that "ky a" wins over "ky".
_PHONEME_KEYS_LONGEST_FIRST = sorted(DOMINO_TO_HIRAGANA_MAP, key=len, reverse=True)


def _find_longest_phoneme_key(
    phonemes: Sequence[str],
    start_position: int,
) -> tuple[str, ...] | None:
    """Return the longest key of ``DOMINO_TO_HIRAGANA_MAP`` found at a position.

    Args:
        phonemes: Phoneme sequence.
        start_position: Position where the key must start.

    Returns:
        The matched key, or ``None`` if no key matches.

    """
    for phoneme_key in _PHONEME_KEYS_LONGEST_FIRST:
        end_position = start_position + len(phoneme_key)
        if (
            end_position <= len(phonemes)
            and tuple(phonemes[start_position:end_position]) == phoneme_key
        ):
            return phoneme_key
    return None


def domino2hiragana(phonemes: str) -> str:
    """Convert a pydomino phoneme sequence to hiragana.

    ``pau`` is ignored and the devoiced vowels ``I`` and ``U`` are read as
    ``i`` and ``u``. Phonemes that match no hiragana are skipped.

    Args:
        phonemes: Space-separated phoneme sequence.

    Returns:
        Hiragana string.

    Examples:
        >>> domino2hiragana("pau a r i g a t o u pau")
        'ありがとう'
        >>> domino2hiragana("k o N n i ch i h a")
        'こんにちは'
        >>> domino2hiragana("pau k I k U pau")
        'きく'

    """
    if not phonemes:
        return ""
    phoneme_list = [
        DEVOICED_TO_VOICED_VOWEL.get(phoneme, phoneme)
        for phoneme in phonemes.split()
        if phoneme != PAUSE_PHONEME
    ]
    hiragana_parts: list[str] = []
    position = 0
    while position < len(phoneme_list):
        phoneme_key = _find_longest_phoneme_key(phoneme_list, position)
        if phoneme_key is None:
            position += 1
            continue
        hiragana_parts.append(DOMINO_TO_HIRAGANA_MAP[phoneme_key])
        position += len(phoneme_key)
    return "".join(hiragana_parts)


def domino2hiragana_with_timing(
    phoneme_timings: list[tuple[str, float, float]],
) -> list[tuple[str, float, float]]:
    """Convert timed pydomino phonemes to timed hiragana.

    ``pau`` is ignored and ``I`` and ``U`` are read as ``i`` and ``u``.
    When several phonemes form one hiragana, the start time of the first
    phoneme and the end time of the last phoneme are used.

    Args:
        phoneme_timings: List of (phoneme, start time, end time). pydomino's
            ``align`` returns (start time, end time, phoneme); reorder it first.

    Returns:
        List of (hiragana, start time, end time).

    Examples:
        >>> domino2hiragana_with_timing(
        ...     [("a", 0.0, 0.1), ("r", 0.1, 0.15), ("i", 0.15, 0.2)]
        ... )
        [('あ', 0.0, 0.1), ('り', 0.1, 0.2)]

    """
    if not phoneme_timings:
        return []
    non_pause_timings = [
        phoneme_timing
        for phoneme_timing in phoneme_timings
        if phoneme_timing[0] != PAUSE_PHONEME
    ]
    phoneme_list = [
        DEVOICED_TO_VOICED_VOWEL.get(phoneme, phoneme)
        for phoneme, _, _ in non_pause_timings
    ]
    hiragana_timings: list[tuple[str, float, float]] = []
    position = 0
    while position < len(phoneme_list):
        phoneme_key = _find_longest_phoneme_key(phoneme_list, position)
        if phoneme_key is None:
            position += 1
            continue
        last_position = position + len(phoneme_key) - 1
        start_seconds = non_pause_timings[position][1]
        end_seconds = non_pause_timings[last_position][2]
        hiragana_timings.append(
            (DOMINO_TO_HIRAGANA_MAP[phoneme_key], start_seconds, end_seconds),
        )
        position = last_position + 1
    return hiragana_timings


def _split_by_pause(phonemes: list[str]) -> list[list[str]]:
    """Split phonemes at ``pau`` and drop empty groups.

    Args:
        phonemes: Phoneme list that may contain ``pau``.

    Returns:
        Non-empty groups of phonemes between pauses.

    """
    phoneme_groups: list[list[str]] = []
    current_group: list[str] = []
    for phoneme in phonemes:
        if phoneme == PAUSE_PHONEME:
            if current_group:
                phoneme_groups.append(current_group)
            current_group = []
        else:
            current_group.append(phoneme)
    if current_group:
        phoneme_groups.append(current_group)
    return phoneme_groups


def domino_csv2hiragana(csv_text: str, has_header: bool = True) -> str:
    r"""Convert CSV phoneme timing data to a hiragana string.

    The phoneme column is found from the header (``phoneme``); without a
    header the first column is used. Rows with fewer than three fields are
    skipped. ``pau`` inside the data becomes a newline.

    Args:
        csv_text: Rows of ``phoneme,start,end`` or ``start,end,phoneme``.
        has_header: Whether the first line is a header.

    Returns:
        Hiragana string.

    Examples:
        >>> domino_csv2hiragana("start,end,phoneme\n0.0,0.5,pau\n0.5,0.6,a\n"
        ...                     "0.6,0.7,pau\n0.7,0.8,i")
        'あ\nい'

    """
    if not csv_text or not csv_text.strip():
        return ""
    lines = split_csv_lines(csv_text)
    phoneme_column = 0
    if has_header:
        header_columns = read_header_columns(lines[0])
        phoneme_column = find_column_index(header_columns, "phoneme", 0)
    data_lines = lines[1:] if has_header else lines
    phonemes = [
        row_fields[phoneme_column].strip()
        for row_fields in iterate_row_fields(data_lines)
        if len(row_fields) >= TIMING_ROW_FIELD_COUNT
    ]
    hiragana_lines = [
        domino2hiragana(" ".join(phoneme_group))
        for phoneme_group in _split_by_pause(phonemes)
    ]
    return "\n".join(hiragana_line for hiragana_line in hiragana_lines if hiragana_line)


def domino_csv2hiragana_csv(csv_text: str, has_header: bool = True) -> str:
    r"""Convert CSV phoneme timing data to CSV hiragana timing data.

    The column order is found from the header when it has three or more
    columns. ``pau`` rows are dropped.

    Args:
        csv_text: Rows of ``phoneme,start,end`` or ``start,end,phoneme``.
        has_header: Whether the first line is a header.

    Returns:
        CSV text whose header is ``hiragana,start,end``.

    Raises:
        ValueError: A start or end field is not a number.

    Examples:
        >>> domino_csv2hiragana_csv("phoneme,start,end\na,0.0,0.1")
        'hiragana,start,end\nあ,0.0,0.1'

    """
    if not csv_text or not csv_text.strip():
        return HIRAGANA_CSV_HEADER
    lines = split_csv_lines(csv_text)
    phoneme_column, start_column, end_column = 0, 1, 2
    if has_header:
        header_columns = read_header_columns(lines[0])
        if len(header_columns) >= TIMING_ROW_FIELD_COUNT:
            phoneme_column = find_column_index(header_columns, "phoneme", 0)
            start_column = find_column_index(header_columns, "start", 1)
            end_column = find_column_index(header_columns, "end", 2)
    data_lines = lines[1:] if has_header else lines
    phoneme_timings = [
        (
            row_fields[phoneme_column].strip(),
            float(row_fields[start_column].strip()),
            float(row_fields[end_column].strip()),
        )
        for row_fields in iterate_row_fields(data_lines)
        if len(row_fields) >= TIMING_ROW_FIELD_COUNT
    ]
    csv_lines = [HIRAGANA_CSV_HEADER]
    csv_lines.extend(
        f"{hiragana},{start_seconds},{end_seconds}"
        for hiragana, start_seconds, end_seconds in domino2hiragana_with_timing(
            phoneme_timings,
        )
    )
    return "\n".join(csv_lines)
