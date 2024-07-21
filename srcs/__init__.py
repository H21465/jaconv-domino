# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from . import myjaconv
"""myjaconv

This module provides Japanese and ASCII character interconverting between
Hiragana and full-/half-width Katakana/ASCII characters.

Author:
    Hayato Yamamoto

Lisence:
    MIT License

Usage:
    import myjaconv
    myjaconv.hira2kata(text, [ignore])  # ひらがなを全角カタカナに変換
    myjaconv.hira2hkata(text, [ignore])  # ひらがなを半角カタカナに変換
    myjaconv.kata2hira(text, [ignore])  # 全角カタカナをひらがなに変換
    myjaconv.enlargesmallkana(text, [ignore])  # 小文字かなを大文字かなに変換
    myjaconv.h2z(text, [ignore, kana, ascii, digit])  # 半角文字を全角文字に変換
    myjaconv.z2h(text, [ignore, kana, ascii, digit])  # 全角文字を半角文字に変換
    myjaconv.han2zen(text, [ignore, kana, ascii, digit])  # 半角文字を全角文字に変換
    myjaconv.zen2han(text, [ignore, kana, ascii, digit])  # 全角文字を半角文字に変換
    myjaconv.normalize(text, [nomalizemode])  # 半角カナを全角カナへ、全角英数字を半角英数字に変換
    myjaconv.kana2alphabet(text)  # かなをローマ字入力アルファベットに変換
    myjaconv.alphabet2kana(text)  # ローマ字入力アルファベットをかなに変換
    myjaconv.kata2alphabet(text)  # カタカナをローマ字入力アルファベットに変換
    myjaconv.alphabet2kata(text)  # ローマ字入力アルファベットをカタカナに変換
    myjaconv.hiragana2julius(text)  # ひらがなをJuliusの音素表現に変換
	myjaconv.hiragana2domino(text)  #ひらがなをpydominoの音素表現に変換
"""

VERSION = (0, 0, 1)
__version__ = '0.0.1'
__all__ = [
    'hira2kata', 'hira2hkata', 'kata2hira', 'h2z', 'z2h', 'hankaku2zenkaku',
    'zenkaku2hankaku', 'normalize', 'kana2alphabet', 'alphabet2kana',
    'kata2alphabet', 'alphabet2kata', 'hiragana2julius', 'enlargesmallkana', 'hiragana2domino'
]

hira2kata = myjaconv.hira2kata
hira2hkata = myjaconv.hira2hkata
kata2hira = myjaconv.kata2hira
h2z = myjaconv.h2z
z2h = myjaconv.z2h
han2zen = myjaconv.h2z  # an alias of h2z
zen2han = myjaconv.z2h  # an alias of z2h
hankaku2zenkaku = myjaconv.h2z  # an alias of h2z
zenkaku2hankaku = myjaconv.z2h  # an alias of z2h
normalize = myjaconv.normalize
kana2alphabet = myjaconv.kana2alphabet
alphabet2kana = myjaconv.alphabet2kana
kata2alphabet = lambda text: myjaconv.kana2alphabet(myjaconv.kata2hira(text))
alphabet2kata = lambda text: myjaconv.hira2kata(myjaconv.alphabet2kana(text))
hiragana2julius = myjaconv.hiragana2julius
hiragana2domino = myjaconv.hiragana2domino
enlargesmallkana = myjaconv.enlargesmallkana
