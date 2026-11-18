# Copyright (c) 2025 Hayato Yamamoto
# SPDX-License-Identifier: MIT
"""Converters from kana to pydomino phonemes.

``hiragana2domino``, ``hiragana2domino_with_mapping`` and
``hiragana_csv2domino``. The tables are in ``jaconv_domino.tables.domino``.
Conversion to Julius phonemes is provided by jaconv (``hiragana2julius``).
"""

from __future__ import annotations

from jaconv import h2z, kata2hira

from jaconv_domino.converters._csv import iterate_row_fields, split_csv_lines
from jaconv_domino.tables.domino import (
    HIRAGANA_TO_DOMINO_MAP,
    LONG_VOWEL_MARK,
    PAUSE_PHONEME,
    SOKUON_PHONEME,
    VOWEL_PHONEMES,
)

# Kana keys tried from the longest, so that "きゃ" wins over "き".
_KANA_KEYS_LONGEST_FIRST = sorted(HIRAGANA_TO_DOMINO_MAP, key=len, reverse=True)


def _find_longest_kana_key(text: str, start_position: int) -> str | None:
    """Return the longest key of ``HIRAGANA_TO_DOMINO_MAP`` found at a position.

    Args:
        text: Hiragana string.
        start_position: Position where the key must start.

    Returns:
        The matched key, or ``None`` if no key matches.

    """
    for kana_key in _KANA_KEYS_LONGEST_FIRST:
        if text.startswith(kana_key, start_position):
            return kana_key
    return None


def _convert_line_with_mapping(line: str) -> list[tuple[str, list[str]]]:
    """Convert one line of hiragana to pairs of (kana, phoneme list).

    * The long vowel mark repeats the previous vowel. It is dropped after a
      non-vowel or at the start of the line.
    * A sokuon right after another sokuon gives no phoneme, because pydomino
      does not allow ``cl`` to follow ``cl``.
    * Characters that match no entry are skipped.

    Args:
        line: Hiragana string without newlines.

    Returns:
        Pairs of the matched kana and its phonemes, in order.

    """
    kana_phoneme_pairs: list[tuple[str, list[str]]] = []
    previous_phoneme: str | None = None
    position = 0
    while position < len(line):
        if line[position] == LONG_VOWEL_MARK:
            if previous_phoneme in VOWEL_PHONEMES:
                kana_phoneme_pairs.append((LONG_VOWEL_MARK, [previous_phoneme]))
            position += 1
            continue
        kana_key = _find_longest_kana_key(line, position)
        if kana_key is None:
            position += 1
            continue
        phoneme_list = HIRAGANA_TO_DOMINO_MAP[kana_key]
        if phoneme_list == [SOKUON_PHONEME] and previous_phoneme == SOKUON_PHONEME:
            phoneme_list = []
        kana_phoneme_pairs.append((kana_key, phoneme_list))
        if phoneme_list:
            previous_phoneme = phoneme_list[-1]
        position += len(kana_key)
    return kana_phoneme_pairs


def hiragana2domino_with_mapping(
    text: str,
) -> tuple[str, list[tuple[str, list[str]]]]:
    r"""Convert kana to pydomino phonemes together with the kana they come from.

    Katakana and half-width katakana are converted to hiragana first. Each
    line is converted separately and lines are joined with ``pau``; the whole
    sequence starts and ends with ``pau``. Characters that are not kana are
    skipped.

    Args:
        text: Hiragana or katakana string. Newlines are allowed.

    Returns:
        A pair of the space-separated phonemes and a list of
        (hiragana, phoneme list). The list does not contain ``pau``.
        Both are empty when nothing can be converted.

    Examples:
        >>> phonemes, mapping = hiragana2domino_with_mapping("ありがとう")
        >>> phonemes
        'pau a r i g a t o u pau'
        >>> mapping[:2]
        [('あ', ['a']), ('り', ['r', 'i'])]
        >>> hiragana2domino_with_mapping("らーめん\nカタカナ")[0]
        'pau r a a m e N pau k a t a k a n a pau'

    """
    if not text:
        return "", []
    hiragana_text = kata2hira(h2z(text))
    kana_phoneme_pairs: list[tuple[str, list[str]]] = []
    phoneme_lines: list[str] = []
    for line in hiragana_text.split("\n"):
        line_pairs = _convert_line_with_mapping(line)
        line_phonemes = [
            phoneme for _, phoneme_list in line_pairs for phoneme in phoneme_list
        ]
        if line_phonemes:
            kana_phoneme_pairs.extend(line_pairs)
            phoneme_lines.append(" ".join(line_phonemes))
    if not phoneme_lines:
        return "", []
    pause_separator = f" {PAUSE_PHONEME} "
    phonemes = f"{PAUSE_PHONEME} {pause_separator.join(phoneme_lines)} {PAUSE_PHONEME}"
    return phonemes, kana_phoneme_pairs


def hiragana2domino(text: str) -> str:
    r"""Convert kana to a pydomino phoneme sequence wrapped with ``pau``.

    The rules are those of ``hiragana2domino_with_mapping``.

    Args:
        text: Hiragana or katakana string. Newlines are allowed.

    Returns:
        Space-separated phonemes that start and end with ``pau``, or an empty
        string when nothing can be converted.

    Examples:
        >>> hiragana2domino("てっぽう")
        'pau t e cl p o u pau'
        >>> hiragana2domino("あり\nがとう")
        'pau a r i pau g a t o u pau'
        >>> hiragana2domino("きく")
        'pau k i k u pau'

    """
    phonemes, _ = hiragana2domino_with_mapping(text)
    return phonemes


def hiragana_csv2domino(csv_text: str, has_header: bool = False) -> str:
    r"""Convert CSV hiragana data to a pydomino phoneme sequence.

    Only the first column is read; timing columns are ignored. All hiragana
    are joined into one line, so ``pau`` appears only at both ends.

    Args:
        csv_text: Rows of ``hiragana,start,end`` or ``hiragana``.
        has_header: Whether the first line is a header.

    Returns:
        Space-separated phonemes wrapped with ``pau``.

    Examples:
        >>> hiragana_csv2domino("あ,0.0,0.1\nり,0.1,0.2")
        'pau a r i pau'

    """
    if not csv_text or not csv_text.strip():
        return ""
    lines = split_csv_lines(csv_text)
    data_lines = lines[1:] if has_header else lines
    hiragana_text = "".join(
        row_fields[0].strip() for row_fields in iterate_row_fields(data_lines)
    )
    return hiragana2domino(hiragana_text)
