# Copyright (c) 2025 Hayato Yamamoto
# SPDX-License-Identifier: MIT
"""Inputs and recorder for the output snapshot of every public function.

The snapshot pins the behaviour of jaconv_domino so that a refactoring can be
checked to change nothing. ``record_outputs`` calls each public function on a
fixed corpus and returns a JSON-serialisable dictionary.
"""

from __future__ import annotations

import itertools
from typing import Any

import jaconv_domino

HIRAGANA_CHARACTERS = [chr(code_point) for code_point in range(0x3041, 0x3097)] + list(
    "゛゜ゝゞー"
)
KATAKANA_CHARACTERS = [chr(code_point) for code_point in range(0x30A1, 0x30FB)] + list(
    "ーヽヾ"
)
HALFWIDTH_CHARACTERS = [chr(code_point) for code_point in range(0xFF61, 0xFFA0)]
FULLWIDTH_CHARACTERS = [chr(code_point) for code_point in range(0xFF01, 0xFF5F)] + [
    "　"
]
ASCII_CHARACTERS = [chr(code_point) for code_point in range(0x20, 0x7F)]
DASH_CHARACTERS = list("〜−—―﹣－-")

SINGLE_CHARACTERS = (
    HIRAGANA_CHARACTERS
    + KATAKANA_CHARACTERS
    + HALFWIDTH_CHARACTERS
    + FULLWIDTH_CHARACTERS
    + ASCII_CHARACTERS
    + DASH_CHARACTERS
)

SENTENCES = [
    "",
    " ",
    "\n",
    "ありがとう",
    "ありがとう\nこんにちは",
    "あ\n\nい",
    "  てっぽう  ",
    "てんきすごくいいいいいい",
    "おとうさん",
    "ゔぁいおりん",
    "う゛ぁう゛ぃう゛ぇう゛ぉう゛ゅ",
    "かぁさん",
    "ぶゃぶゅぶょ",
    "ゃゅょ",
    "っ",
    "あっ",
    "っっか",
    "ともえまみ",
    "まどまぎ",
    "さくらきょうこ",
    "キュゥべえ",
    "巴マミ",
    "マミサン",
    "ティロフィナーレ",
    "ﾃｨﾛﾌｨﾅｰﾚ",
    "ﾃｨﾛ･フィナ〜レ",
    "ＡＢＣＤ１２３４",
    "abcd1234",
    "カタカナとひらがなとAlphabet",
    "らーめん、たべたい。",
    "でぃずにーらんど",
    "ふぁみりーまーと",
    "つぁつぃつぇつぉ",
    "てゃてゅてょとゃとゅとょ",
    "ずゃずゅずょ",
    "ゐゑを",
    "ヵヶ",
]

ROMAJI_WORDS = [
    "mamisan",
    "ohayou",
    "banana",
    "Itoh",
    "h",
    "KONNICHIWA",
    "n'a",
    "xn",
    "mm",
    "d'yu",
    "t'i",
    "tchi",
    "kka",
    "xtsu",
    "hwyu",
    "shinbun",
    "qwerty",
    "",
]

IGNORE_CHARACTERS = ["", "あ", "ア", "ｨ", "ィ", "a", "1"]
NORMALIZATION_MODES = ["NFC", "NFD", "NFKC", "NFKD"]

SINGLE_ARGUMENT_FUNCTION_NAMES = [
    "hira2kata",
    "hira2hkata",
    "kata2hira",
    "enlargesmallkana",
    "h2z",
    "z2h",
    "hankaku2zenkaku",
    "han2zen",
    "zenkaku2hankaku",
    "zen2han",
    "normalize",
    "kana2alphabet",
    "kata2alphabet",
    "hiragana2julius",
    "hiragana2domino",
    "hiragana2domino_with_mapping",
]

HIRAGANA_PAIR_FUNCTION_NAMES = [
    "kana2alphabet",
    "hiragana2julius",
    "hiragana2domino",
    "hiragana2domino_with_mapping",
]

CSV_TEXTS = [
    "",
    "phoneme,start,end",
    "phoneme,start,end\na,0.0,0.1\nry,0.1,0.2",
    "start,end,phoneme\n0.0,0.5,pau\n0.5,0.6,a\n0.6,0.7,pau\n0.7,0.8,i",
    (
        "start,end,phoneme\n0.000,0.620,pau\n0.620,0.680,a\n0.680,1.350,ry\n"
        "1.350,2.010,i\n2.010,2.100,pau\n2.100,3.260,a\n3.260,3.290,t\n"
        "3.290,3.510,o\n3.510,3.620,u\n3.620,3.739,pau"
    ),
    "end,phoneme,start\n0.1,k,0.0\n0.2,a,0.1\n\n0.3,N,0.2",
    "a,0.0,0.1\nry,0.1,0.2\nshort,line",
    "pau,0.0,0.1\npau,0.1,0.2",
]

HIRAGANA_CSV_TEXTS = [
    "",
    "あ,0.0,0.1\nり,0.1,0.2",
    "あ,0.0,0.1\nり,0.1,0.2\nが,0.2,0.3\nと,0.3,0.4\nう,0.4,0.5",
    "hiragana,start,end\nか,0.0,0.1\nぁ,0.1,0.2",
    "あ\nい\n\nう",
    ",0.0,0.1",
]


def _phoneme_sequences() -> list[str]:
    """Return phoneme strings that exercise ``domino2hiragana``."""
    domino_values = [
        " ".join(phoneme_list)
        for phoneme_list in jaconv_domino.HIRAGANA_TO_DOMINO_MAP.values()
    ]
    single_phonemes = sorted(
        {
            phoneme
            for phoneme_list in jaconv_domino.HIRAGANA_TO_DOMINO_MAP.values()
            for phoneme in phoneme_list
        }
        | {"pau", "a:", "xx", "v", "I", "U"},
    )
    phoneme_pairs = [
        f"{first_phoneme} {second_phoneme}"
        for first_phoneme, second_phoneme in itertools.product(
            single_phonemes,
            repeat=2,
        )
    ]
    round_trips = [
        jaconv_domino.hiragana2domino(first_character + second_character)
        for first_character, second_character in itertools.product(
            HIRAGANA_CHARACTERS,
            repeat=2,
        )
    ]
    return ["", "pau", "pau pau", *domino_values, *phoneme_pairs, *round_trips]


def _to_timings(phoneme_string: str) -> list[tuple[str, float, float]]:
    """Attach deterministic start and end times to each phoneme."""
    step_seconds = 0.1
    return [
        (phoneme, index * step_seconds, (index + 1) * step_seconds)
        for index, phoneme in enumerate(phoneme_string.split())
    ]


def _to_json_value(value: object) -> Any:  # noqa: ANN401
    """Convert tuples to lists so that results compare equal after JSON."""
    if isinstance(value, (list, tuple)):
        return [_to_json_value(item) for item in value]
    return value


def _call_or_error_name(function: Any, *arguments: object) -> Any:  # noqa: ANN401
    """Return the result, or the exception class name if the call raises."""
    try:
        return function(*arguments)
    except Exception as error:  # noqa: BLE001
        return f"!{type(error).__name__}"


def record_outputs() -> dict[str, Any]:
    """Call every public function on the corpus and collect the results."""
    outputs: dict[str, Any] = {}

    for function_name in SINGLE_ARGUMENT_FUNCTION_NAMES:
        function = getattr(jaconv_domino, function_name)
        outputs[function_name] = {
            text: _to_json_value(function(text))
            for text in SINGLE_CHARACTERS + SENTENCES
        }

    for function_name in HIRAGANA_PAIR_FUNCTION_NAMES:
        function = getattr(jaconv_domino, function_name)
        outputs[f"{function_name}:pairs"] = {
            first_character + second_character: _to_json_value(
                function(first_character + second_character),
            )
            for first_character, second_character in itertools.product(
                HIRAGANA_CHARACTERS,
                repeat=2,
            )
        }

    for function_name in ["hira2kata", "hira2hkata", "kata2hira", "enlargesmallkana"]:
        function = getattr(jaconv_domino, function_name)
        outputs[f"{function_name}:ignore"] = {
            f"{ignore}|{text}": _call_or_error_name(function, text, ignore)
            for ignore in IGNORE_CHARACTERS
            for text in SENTENCES
        }

    for function_name in ["h2z", "z2h"]:
        function = getattr(jaconv_domino, function_name)
        outputs[f"{function_name}:options"] = {
            f"{ignore}|{kana}|{ascii_flag}|{digit}|{text}": _call_or_error_name(
                function,
                text,
                ignore,
                kana,
                ascii_flag,
                digit,
            )
            for ignore in IGNORE_CHARACTERS
            for kana, ascii_flag, digit in itertools.product([True, False], repeat=3)
            for text in [*SENTENCES, "".join(SINGLE_CHARACTERS)]
        }

    outputs["normalize:modes"] = {
        f"{mode}|{text}": jaconv_domino.normalize(text, mode)
        for mode in NORMALIZATION_MODES
        for text in SINGLE_CHARACTERS + SENTENCES
    }

    romaji_corpus = sorted(
        set(ROMAJI_WORDS)
        | set(ASCII_CHARACTERS)
        | set(outputs["kana2alphabet:pairs"].values()),
    )
    for function_name in ["alphabet2kana", "alphabet2kata"]:
        function = getattr(jaconv_domino, function_name)
        outputs[function_name] = {text: function(text) for text in romaji_corpus}

    phoneme_sequences = _phoneme_sequences()
    outputs["domino2hiragana"] = {
        phonemes: jaconv_domino.domino2hiragana(phonemes)
        for phonemes in phoneme_sequences
    }
    outputs["domino2hiragana_with_timing"] = {
        phonemes: _to_json_value(
            jaconv_domino.domino2hiragana_with_timing(_to_timings(phonemes)),
        )
        for phonemes in phoneme_sequences
    }

    for function_name in ["domino_csv2hiragana", "domino_csv2hiragana_csv"]:
        function = getattr(jaconv_domino, function_name)
        outputs[function_name] = {
            f"{has_header}|{csv_text}": _call_or_error_name(
                function,
                csv_text,
                has_header,
            )
            for has_header in [True, False]
            for csv_text in CSV_TEXTS
        }
    outputs["hiragana_csv2domino"] = {
        f"{has_header}|{csv_text}": _call_or_error_name(
            jaconv_domino.hiragana_csv2domino,
            csv_text,
            has_header,
        )
        for has_header in [True, False]
        for csv_text in HIRAGANA_CSV_TEXTS
    }

    outputs["HIRAGANA_TO_DOMINO_MAP"] = _to_json_value(
        dict(jaconv_domino.HIRAGANA_TO_DOMINO_MAP),
    )
    outputs["DOMINO_TO_HIRAGANA_MAP"] = {
        " ".join(phoneme_key): hiragana
        for phoneme_key, hiragana in jaconv_domino.DOMINO_TO_HIRAGANA_MAP.items()
    }
    outputs["__all__"] = sorted(jaconv_domino.__all__)
    return outputs
