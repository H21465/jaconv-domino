# jaconv-domino

[![PyPI version](https://img.shields.io/pypi/v/jaconv-domino.svg)](https://pypi.org/project/jaconv-domino/)
[![Python versions](https://img.shields.io/pypi/pyversions/jaconv-domino.svg)](https://pypi.org/project/jaconv-domino/)
[![License](https://img.shields.io/pypi/l/jaconv-domino.svg)](https://pypi.org/project/jaconv-domino/)

jaconv-domino は，日本語の文字列と [pydomino](https://github.com/DwangoMediaVillage/pydomino)（ドワンゴメディアヴィレッジの日本語音素アラインメントツール）の音素列とを相互に変換するライブラリです．[jaconv](https://github.com/ikegami-yukino/jaconv) の関数も再公開しており，かな・全角半角・ローマ字の変換も同じパッケージから使えます．

[English README](README.md)

## インストール

```bash
pip install jaconv-domino
```

依存パッケージとして jaconv（0.5 系）も入ります．

## 使い方の例

```python
import jaconv_domino

jaconv_domino.hiragana2domino("ありがとう")
# => 'pau a r i g a t o u pau'

jaconv_domino.domino2hiragana("pau a r i g a t o u pau")
# => 'ありがとう'

jaconv_domino.hira2kata("ともえまみ")
# => 'トモエマミ'
```

## pydomino の音素列への変換

### pydomino が想定する入力

pydomino の `Aligner.align(waveform, phonemes, min_aligned_timeframe)` は，半角スペースで区切った音素列を受け取ります．jaconv-domino が出力する音素列は，以下の条件を満たします．

- pydomino の README に記載されている39個の音素だけを用います：`pau ry r my m ny n j z by b dy d gy g ky k ch ts sh s hy h v f py p t y w N a i u e o I U cl`．
- 先頭と末尾に `pau` を挿入します．
- 隣り合う 2 つの音素の組は，すべて pydomino の遷移表（`src/phoneme_transitions.txt`）に含まれます．それ以外の組（子音の後に子音や `pau` が続くなど）を渡すと，pydomino はエラーを出力します．

### 変換の規則

| 入力 | 出力 | 規則 |
|------|------|------|
| `ありがとう` | `pau a r i g a t o u pau` | 基本出力として両端に `pau` を付けます． |
| `あり\nがとう` | `pau a r i pau g a t o u pau` | 改行は `pau` になります．空行はスキップします． |
| `きく` | `pau k i k u pau` | 現行pydominoのモデルの学習ラベルでは，イ段の子音は口蓋化しません（`ky i` ではなく `k i`）． |
| `ぢ` | `pau j i pau` | `ぢ`・`づ` は `じ`・`ず` と同じ音として扱います． |
| `らーめん` | `pau r a a m e N pau` | 長音記号は直前の母音と同じものとして扱います． |
| `かぁさん` | `pau k a a s a N pau` | 前のかなと音節を作らない小さな母音は，母音として扱います． |
| `ゔぁいおりん` | `pau v a i o r i N pau` | `ゔ` には `v` を用います． |
| `てゅーば` | `pau ch u u b a pau` | pydomino には `ty` が無いので，`ch` として扱います． |
| `っっか` | `pau cl k a pau` | `っ` が続いても `cl` は 1つとして扱います． |
| `カタカナ`，`ﾃｨﾛﾌｨﾅｰﾚ` | `pau k a t a k a n a pau`，`pau t i r o f i n a a r e pau` | ひらがなだけでなくカタカナと半角カタカナも変換対象となります． |
| `Abc、。` | （空文字列） | かな以外の文字はスキップします． |

無声化した母音 `I`・`U` は変換では扱いません．これは，pydomino が入力の音素列を処理する際に，**無声子音 `k ky ch ts sh s hy h f py p t` の直後にあり，直後がそれらの子音か `pau` である `i`・`u`** を， `I`・`U` として扱うためです．たとえば `pau k i k u pau` は `pau k I k U pau` としてアラインメントされます．

### 関数

```python
import jaconv_domino

# かな → 音素列
jaconv_domino.hiragana2domino("ありがとう\nこんにちは")
# => 'pau a r i g a t o u pau k o N n i ch i h a pau'

# かな → 音素列（各音素の元になったかなも返す）
phonemes, mapping = jaconv_domino.hiragana2domino_with_mapping("らーめん")
# phonemes => 'pau r a a m e N pau'
# mapping  => [('ら', ['r', 'a']), ('ー', ['a']), ('め', ['m', 'e']), ('ん', ['N'])]

# ひらがなの CSV（1 列目）→ 音素列
jaconv_domino.hiragana_csv2domino("あ,0.0,0.1\nり,0.1,0.2")
# => 'pau a r i pau'
```

### ひらがなへの逆変換

pydomino のアラインメント結果は，時刻つきのひらがなに変換できます（`domino2hiragana_with_timing`）．`pau` はスキップし，`I`・`U` は `i`・`u` として扱います．逆変換は，`(ひらがな，開始時刻，終了時刻)`を出力します．

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

CSV を扱う関数は，見出し（`start,end,phoneme` または `phoneme,start,end`）から列の順序を判断します．

### pydomino と組み合わせる

```python
import jaconv_domino
import librosa
import numpy as np
import pydomino

aligner = pydomino.Aligner("onnx_model/phoneme_transition_model.onnx")
waveform = librosa.load("voice.wav", sr=16_000, mono=True, dtype=np.float32)[0]
phonemes = jaconv_domino.hiragana2domino("ありがとう")
alignment = aligner.align(waveform, phonemes, 3)  # [(開始秒, 終了秒, 音素), ...]
phoneme_timings = [(phoneme, start, end) for start, end, phoneme in alignment]
jaconv_domino.domino2hiragana_with_timing(phoneme_timings)
```

`align` は `(開始秒, 終了秒, 音素)` の順で返し，`domino2hiragana_with_timing` は `(音素, 開始秒, 終了秒)` の順で受け取ります．上のように並べ替えてから渡してください．

## jaconv 由来の変換

以下の関数は jaconv（0.5 系）の関数をそのまま再公開したものです．`enlargesmallkana` だけは，jaconv の非推奨の警告を出さない `enlarge_smallkana` の別名です．詳しくは [jaconv のリポジトリ](https://github.com/ikegami-yukino/jaconv)を参照してください．

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

## API 一覧

### pydomino の音素

| 関数 | 説明 |
|------|------|
| `hiragana2domino(text)` | かな → pydomino の音素列 |
| `hiragana2domino_with_mapping(text)` | かな → pydomino の音素列と（かな，音素）の組の一覧 |
| `hiragana_csv2domino(csv_text, has_header=False)` | ひらがなの CSV → pydomino の音素列 |
| `domino2hiragana(phonemes)` | pydomino の音素列 → ひらがな |
| `domino2hiragana_with_timing(phoneme_timings)` | 時刻つきの音素 → 時刻つきのひらがな |
| `domino_csv2hiragana(csv_text, has_header=True)` | 時刻つき音素の CSV → ひらがな（`pau` は改行） |
| `domino_csv2hiragana_csv(csv_text, has_header=True)` | 時刻つき音素の CSV → 時刻つきひらがなの CSV |
| `HIRAGANA_TO_DOMINO_MAP` | かな → 音素の表 |
| `DOMINO_TO_HIRAGANA_MAP` | 音素 → ひらがなの表 |

### jaconv 由来 （0.5 系のものをそのまま使います）

| 関数 | 説明 |
|------|------|
| `hira2kata(text, ignore="")` | ひらがな → 全角カタカナ |
| `hira2hkata(text, ignore="")` | ひらがな → 半角カタカナ |
| `kata2hira(text, ignore="")` | 全角カタカナ → ひらがな |
| `h2z(text, ignore="", kana=True, ascii=False, digit=False)` | 半角 → 全角 |
| `z2h(text, ignore="", kana=True, ascii=False, digit=False)` | 全角 → 半角 |
| `normalize(text, mode="NFKC")` | ダッシュや引用符を置き換えたあと Unicode 正規化 |
| `kana2alphabet(text)` | ひらがな → ローマ字 |
| `kata2alphabet(text)` | カタカナ → ローマ字 |
| `alphabet2kana(text)` | ローマ字 → ひらがな |
| `alphabet2kata(text)` | ローマ字 → カタカナ |
| `enlargesmallkana(text, ignore="")` | 小書きのかな → 通常の大きさ（別名：`enlarge_smallkana`） |
| `hiragana2julius(text)` | ひらがな → Julius の音素列 |

別名：`hankaku2zenkaku`・`han2zen` は `h2z`，`zenkaku2hankaku`・`zen2han` は `z2h` と同じです．

## パッケージの構成

```
jaconv_domino/
├── tables/
│   └── domino.py     かなと pydomino の音素の変換表
└── converters/   変換の関数（出力の種類で分類）
    ├── phoneme.py    かな → pydomino の音素
    └── kana.py       pydomino の音素 → ひらがな
```

すべての関数は `jaconv_domino` から import できます．0.1 向けに書かれたコードのために，`jaconv_domino.phoneme` も残しています．

## 0.2.0 での変更

- 依存する jaconv を `jaconv>=0.5.0,<0.6` にしました．`enlarge_smallkana` も使えます．
- pydomino の音素列の出力を変えました．
  - pydomino の 39 音素だけを出力します．`a:` などの長母音の記号，`ty`，`zy` は出力しません．
  - イ段の子音を口蓋化しません（`き` は `k i`）．
  - `ぢ` は `j i`，`ゔ` は `v` を使います．
  - 長音記号は直前の母音と同じものとして扱います．
  - カタカナ，半角カタカナも変換できます．その他の文字は，スキップします．
  - `hiragana2domino_with_mapping` も両端に `pau` を付け，`hiragana2domino` と同じ音素列を返します．
- `domino2hiragana` などが `I`・`U`・`k i`・`v` を読めるようになりました．


## ライセンス

MIT License
テスト用データ `tests/data/pydomino_phoneme_transitions.txt` は pydomino（Copyright (c) 2024 DWANGO Co.,Ltd.，MIT License）から取得したものです．詳しくは [LICENSE](LICENSE) と `tests/data/PYDOMINO_LICENSE` を参照してください．
