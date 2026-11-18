# Copyright (c) 2025 Hayato Yamamoto
# SPDX-License-Identifier: MIT
"""jaconv_domino: Japanese character conversion with pydomino phonemes.

The kana, width, alphabet and Julius conversions are re-exported from jaconv
(0.5 series). The pydomino phoneme conversions are specific to this package.

Package layout:

* ``jaconv_domino.tables.domino``: tables between kana and pydomino phonemes.
* ``jaconv_domino.converters``: ``phoneme`` (kana to phonemes) and ``kana``
  (phonemes to hiragana).

Examples:
    >>> import jaconv_domino
    >>> jaconv_domino.hira2kata("ひらがな")
    'ヒラガナ'
    >>> jaconv_domino.hiragana2domino("ありがとう")
    'pau a r i g a t o u pau'
    >>> jaconv_domino.domino2hiragana("pau a ry i g a t o u pau")
    'ありがとう'

"""

from __future__ import annotations

from jaconv import (
    alphabet2kana,
    alphabet2kata,
    enlarge_smallkana,
    h2z,
    han2zen,
    hankaku2zenkaku,
    hira2hkata,
    hira2kata,
    hiragana2julius,
    kana2alphabet,
    kata2alphabet,
    kata2hira,
    normalize,
    z2h,
    zen2han,
    zenkaku2hankaku,
)

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

VERSION = (0, 2, 0)
__version__ = "0.2.0"
# jaconv 0.5.0 warns when ``enlargesmallkana`` is called. The old name is kept
# here as a plain alias, without the warning, for code written for 0.1.
enlargesmallkana = enlarge_smallkana

__all__ = [
    "DOMINO_TO_HIRAGANA_MAP",
    "HIRAGANA_TO_DOMINO_MAP",
    "alphabet2kana",
    "alphabet2kata",
    "domino2hiragana",
    "domino2hiragana_with_timing",
    "domino_csv2hiragana",
    "domino_csv2hiragana_csv",
    "enlarge_smallkana",
    "enlargesmallkana",
    "h2z",
    "han2zen",
    "hankaku2zenkaku",
    "hira2hkata",
    "hira2kata",
    "hiragana2domino",
    "hiragana2domino_with_mapping",
    "hiragana2julius",
    "hiragana_csv2domino",
    "kana2alphabet",
    "kata2alphabet",
    "kata2hira",
    "normalize",
    "z2h",
    "zen2han",
    "zenkaku2hankaku",
]
