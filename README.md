# jaconv-domino

[![PyPI version](https://img.shields.io/pypi/v/jaconv-domino.svg)](https://pypi.org/project/jaconv-domino/)
[![Python versions](https://img.shields.io/pypi/pyversions/jaconv-domino.svg)](https://pypi.org/project/jaconv-domino/)
[![License](https://img.shields.io/pypi/l/jaconv-domino.svg)](https://pypi.org/project/jaconv-domino/)

jaconv-domino converts Japanese text to and from the phoneme sequences of
[pydomino](https://github.com/DwangoMediaVillage/pydomino), the Japanese
phoneme aligner by Dwango Media Village. It also re-exports the functions of
[jaconv](https://github.com/ikegami-yukino/jaconv), so the kana, full-width /
half-width and romaji conversions are available from the same package.

[日本語版 README](https://github.com/H21465/jaconv-domino/blob/main/README-ja.md)

## Installation

```bash
pip install jaconv-domino
```

jaconv (0.5 series) is installed as a dependency.

## Quick start

```python
import jaconv_domino

jaconv_domino.hiragana2domino("ありがとう")
# => 'pau a r i g a t o u pau'

jaconv_domino.domino2hiragana("pau a r i g a t o u pau")
# => 'ありがとう'

jaconv_domino.hira2kata("ともえまみ")
# => 'トモエマミ'
```

## Conversion to pydomino phonemes

### What pydomino expects

pydomino's `Aligner.align(waveform, phonemes, min_aligned_timeframe)` takes a
space-separated phoneme string. The phoneme strings produced by jaconv-domino
satisfy the following conditions.

- Only the 39 phonemes listed in the pydomino README are used:
  `pau ry r my m ny n j z by b dy d gy g ky k ch ts sh s hy h v f py p t y w N a i u e o I U cl`.
- `pau` is inserted at the start and the end.
- Every pair of adjacent phonemes is included in pydomino's transition table
  (`src/phoneme_transitions.txt`). For any other pair (for example a consonant
  followed by another consonant or by `pau`), pydomino reports an error.

### Rules

| Input | Output | Rule |
|-------|--------|------|
| `ありがとう` | `pau a r i g a t o u pau` | As the basic output, `pau` is added at both ends. |
| `あり\nがとう` | `pau a r i pau g a t o u pau` | A newline becomes `pau`. Empty lines are skipped. |
| `きく` | `pau k i k u pau` | In the training labels of the current pydomino model, consonants before `i` are not palatalized (`k i`, not `ky i`). |
| `ぢ` | `pau j i pau` | `ぢ` and `づ` are treated as the same sounds as `じ` and `ず`. |
| `らーめん` | `pau r a a m e N pau` | The long vowel mark is treated as the same vowel as the previous one. |
| `かぁさん` | `pau k a a s a N pau` | A small vowel that does not form a syllable with the previous kana is treated as a vowel. |
| `ゔぁいおりん` | `pau v a i o r i N pau` | `v` is used for `ゔ`. |
| `てゅーば` | `pau ch u u b a pau` | pydomino has no `ty`, so it is treated as `ch`. |
| `っっか` | `pau cl k a pau` | Consecutive `っ` are treated as a single `cl`. |
| `カタカナ`, `ﾃｨﾛﾌｨﾅｰﾚ` | `pau k a t a k a n a pau`, `pau t i r o f i n a a r e pau` | Not only hiragana but also katakana and half-width katakana are converted. |
| `Abc、。` | (empty string) | Characters other than kana are skipped. |

The devoiced vowels `I` and `U` are not handled in the conversion. This is
because, when pydomino processes the input phoneme sequence, it treats
**an `i` or `u` that follows one of the voiceless consonants
`k ky ch ts sh s hy h f py p t` and is followed by one of those consonants or
by `pau`** as `I` or `U`. For example, `pau k i k u pau` is aligned as
`pau k I k U pau`.

### Functions

```python
import jaconv_domino

# Kana to phonemes
jaconv_domino.hiragana2domino("ありがとう\nこんにちは")
# => 'pau a r i g a t o u pau k o N n i ch i h a pau'

# Kana to phonemes, also returning the kana each phoneme comes from
phonemes, mapping = jaconv_domino.hiragana2domino_with_mapping("らーめん")
# phonemes => 'pau r a a m e N pau'
# mapping  => [('ら', ['r', 'a']), ('ー', ['a']), ('め', ['m', 'e']), ('ん', ['N'])]

# CSV of hiragana (first column) to phonemes
jaconv_domino.hiragana_csv2domino("あ,0.0,0.1\nり,0.1,0.2")
# => 'pau a r i pau'
```

### Conversion back to hiragana

The alignment result of pydomino can be converted to hiragana with timing
(`domino2hiragana_with_timing`). `pau` is skipped, and `I` and `U` are treated
as `i` and `u`. The reverse conversion outputs `(hiragana, start time, end time)`.

```python
import jaconv_domino

jaconv_domino.domino2hiragana("pau k I k U pau")
# => 'きく'

phoneme_timings = [
    ("pau", 0.0, 0.1),
    ("k", 0.1, 0.15),
    ("I", 0.15, 0.2),
    ("k", 0.2, 0.25),
    ("U", 0.25, 0.3),
    ("pau", 0.3, 0.4),
]
jaconv_domino.domino2hiragana_with_timing(phoneme_timings)
# => [('き', 0.1, 0.2), ('く', 0.2, 0.3)]

csv_text = "start,end,phoneme\n0.0,0.5,pau\n0.5,0.6,a\n0.6,0.7,pau\n0.7,0.8,i"
jaconv_domino.domino_csv2hiragana(csv_text)
# => 'あ\nい'
jaconv_domino.domino_csv2hiragana_csv(csv_text)
# => 'hiragana,start,end\nあ,0.5,0.6\nい,0.7,0.8'
```

The functions that handle CSV determine the column order from the header
(`start,end,phoneme` or `phoneme,start,end`).

### Use with pydomino

```python
import jaconv_domino
import librosa
import numpy as np
import pydomino

aligner = pydomino.Aligner("onnx_model/phoneme_transition_model.onnx")
waveform = librosa.load("voice.wav", sr=16_000, mono=True, dtype=np.float32)[0]
phonemes = jaconv_domino.hiragana2domino("ありがとう")
alignment = aligner.align(waveform, phonemes, 3)  # [(start, end, phoneme), ...]
phoneme_timings = [(phoneme, start, end) for start, end, phoneme in alignment]
jaconv_domino.domino2hiragana_with_timing(phoneme_timings)
```

`align` returns tuples in the order `(start, end, phoneme)`, while
`domino2hiragana_with_timing` takes them in the order `(phoneme, start, end)`.
Reorder them as above before passing them.

## Conversions from jaconv

The following functions are those of jaconv (0.5 series), re-exported as they
are. Only `enlargesmallkana` is an alias of `enlarge_smallkana` that does not
emit jaconv's deprecation warning. For details, see the
[jaconv repository](https://github.com/ikegami-yukino/jaconv).

```python
import jaconv_domino

jaconv_domino.hira2kata("ともえまみ")  # => 'トモエマミ'
jaconv_domino.hira2hkata("ともえまみ")  # => 'ﾄﾓｴﾏﾐ'
jaconv_domino.kata2hira("マミサン")  # => 'まみさん'
jaconv_domino.h2z("ﾃｨﾛﾌｨﾅｰﾚ")  # => 'ティロフィナーレ'
jaconv_domino.z2h("ティロフィナーレ")  # => 'ﾃｨﾛﾌｨﾅｰﾚ'
jaconv_domino.normalize("ﾃｨﾛ･フィナ〜レ")  # => 'ティロ・フィナーレ'
jaconv_domino.kana2alphabet("ばなな")  # => 'banana'
jaconv_domino.alphabet2kana("ohayou")  # => 'おはよう'
jaconv_domino.kata2alphabet("バナナ")  # => 'banana'
jaconv_domino.alphabet2kata("ohayou")  # => 'オハヨウ'
jaconv_domino.enlargesmallkana("ぁぃぅぇぉ")  # => 'あいうえお'
jaconv_domino.hiragana2julius("てんきすごくいいいいいい")
# => 't e N k i s u g o k u i:'
```

## API reference

### pydomino phonemes

| Function | Description |
|----------|-------------|
| `hiragana2domino(text)` | Kana → pydomino phonemes |
| `hiragana2domino_with_mapping(text)` | Kana → pydomino phonemes and a list of (kana, phonemes) pairs |
| `hiragana_csv2domino(csv_text, has_header=False)` | CSV of hiragana → pydomino phonemes |
| `domino2hiragana(phonemes)` | pydomino phonemes → hiragana |
| `domino2hiragana_with_timing(phoneme_timings)` | Timed phonemes → timed hiragana |
| `domino_csv2hiragana(csv_text, has_header=True)` | CSV of timed phonemes → hiragana (`pau` becomes a newline) |
| `domino_csv2hiragana_csv(csv_text, has_header=True)` | CSV of timed phonemes → CSV of timed hiragana |
| `HIRAGANA_TO_DOMINO_MAP` | Table from kana to phonemes |
| `DOMINO_TO_HIRAGANA_MAP` | Table from phonemes to hiragana |

### From jaconv (0.5 series, re-exported as they are)

| Function | Description |
|----------|-------------|
| `hira2kata(text, ignore="")` | Hiragana → full-width katakana |
| `hira2hkata(text, ignore="")` | Hiragana → half-width katakana |
| `kata2hira(text, ignore="")` | Full-width katakana → hiragana |
| `h2z(text, ignore="", kana=True, ascii=False, digit=False)` | Half-width → full-width |
| `z2h(text, ignore="", kana=True, ascii=False, digit=False)` | Full-width → half-width |
| `normalize(text, mode="NFKC")` | Unicode normalization after replacing dashes and quotes |
| `kana2alphabet(text)` | Hiragana → romaji |
| `kata2alphabet(text)` | Katakana → romaji |
| `alphabet2kana(text)` | Romaji → hiragana |
| `alphabet2kata(text)` | Romaji → katakana |
| `enlargesmallkana(text, ignore="")` | Small kana → normal size (alias: `enlarge_smallkana`) |
| `hiragana2julius(text)` | Hiragana → Julius phonemes |

Aliases: `hankaku2zenkaku` and `han2zen` are the same as `h2z`;
`zenkaku2hankaku` and `zen2han` are the same as `z2h`.

## Package layout

```
jaconv_domino/
├── tables/
│   └── domino.py     tables between kana and pydomino phonemes
└── converters/   conversion functions (grouped by the kind of output)
    ├── phoneme.py    kana → pydomino phonemes
    └── kana.py       pydomino phonemes → hiragana
```

All functions can be imported from `jaconv_domino`. The module
`jaconv_domino.phoneme` is also kept for code written for 0.1.

## Changes in 0.2.0

- The jaconv requirement is now `jaconv>=0.5.0,<0.6`, and `enlarge_smallkana` is
  also exported.
- The pydomino phoneme output changed.
  - Only the 39 pydomino phonemes are output. Long vowel symbols such as `a:`,
    `ty` and `zy` are not output.
  - Consonants before `i` are not palatalized (`き` is `k i`).
  - `ぢ` is `j i`, and `v` is used for `ゔ`.
  - The long vowel mark is treated as the same vowel as the previous one.
  - Katakana and half-width katakana can also be converted. Other characters
    are skipped.
  - `hiragana2domino_with_mapping` also adds `pau` at both ends and returns the
    same phonemes as `hiragana2domino`.
- `domino2hiragana` and related functions can now read `I`, `U`, `k i` and `v`.

## License

MIT License.
The test data `tests/data/pydomino_phoneme_transitions.txt` is taken from
pydomino (Copyright (c) 2024 DWANGO Co.,Ltd., MIT License). For details, see
[LICENSE](https://github.com/H21465/jaconv-domino/blob/main/LICENSE) and
[`tests/data/PYDOMINO_LICENSE`](https://github.com/H21465/jaconv-domino/blob/main/tests/data/PYDOMINO_LICENSE).
