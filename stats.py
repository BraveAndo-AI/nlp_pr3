"""Задание 2. Статистики корпуса: токены, типы, TTR, длины документов, доли языков.

Язык определяется по абзацам моделью fastText lid.176 (знает kk, ru, en),
доля языка = доля символов корпуса в абзацах этого языка.
Модель (1 МБ): https://dl.fbaipublicfiles.com/fasttext/supervised-models/lid.176.ftz
Если fastText не установлен — простое правило по буквам (менее точно).

Запуск: python stats.py corpus.jsonl
"""
import json
import re
import sys
from collections import Counter

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from common import read_jsonl, tokenize

KZ_SPECIFIC = set("әғқңөұүһі")


def load_lang_detector(path="lid.176.ftz"):
    try:
        import fasttext
        model = fasttext.load_model(path)
        return lambda t: model.predict(t.replace("\n", " "))[0][0].replace("__label__", "")
    except Exception as e:
        print(f"fastText недоступен ({e}) — используем правило по буквам")

        def rule(t):
            t = t.lower()
            if any(c in KZ_SPECIFIC for c in t):
                return "kk"
            cyr = len(re.findall(r"[а-яё]", t))
            lat = len(re.findall(r"[a-z]", t))
            return "ru" if cyr > lat else ("en" if lat > 0 else "other")
        return rule


if __name__ == "__main__":
    docs = read_jsonl(sys.argv[1] if len(sys.argv) > 1 else "corpus.jsonl")
    detect = load_lang_detector()

    counts, lens, lang_chars = Counter(), [], Counter()
    for d in docs:
        toks = tokenize(d["text"])
        counts.update(toks)
        lens.append(len(toks))
        for para in d["text"].split("\n"):
            if len(para.strip()) >= 20:
                lang = detect(para)
                lang_chars[lang if lang in ("kk", "ru", "en") else "other"] += len(para)

    N, V = sum(counts.values()), len(counts)
    lens = np.array(lens)
    total = sum(lang_chars.values())
    stats = {
        "документов": len(docs),
        "токенов N": N,
        "типов V": V,
        "TTR = V/N": round(V / N, 4),
        "hapax (частота 1)": sum(1 for c in counts.values() if c == 1),
        "длина док.: среднее": round(lens.mean(), 1),
        "длина док.: медиана": int(np.median(lens)),
        "длина док.: min / max": f"{lens.min()} / {lens.max()}",
        "длина док.: 90-й перцентиль": int(np.percentile(lens, 90)),
        **{f"доля языка {k}": f"{100 * lang_chars[k] / total:.1f}%" for k in ("kk", "ru", "en", "other")},
    }
    print(pd.Series(stats).to_markdown())
    json.dump(stats, open("stats.json", "w", encoding="utf-8"), ensure_ascii=False, indent=2, default=str)

    plt.figure(figsize=(7, 4))
    plt.hist(lens, bins=np.logspace(np.log10(max(lens.min(), 1)), np.log10(lens.max()), 40))
    plt.xscale("log")
    plt.xlabel("Длина документа, токенов (log)")
    plt.ylabel("Число документов")
    plt.title("Распределение длин документов")
    plt.tight_layout()
    plt.savefig("doc_lengths.png", dpi=150)
    print("\nГрафик: doc_lengths.png, числа: stats.json")
