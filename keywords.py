"""Задание 4. Ключевые слова корпуса относительно эталона (Википедия) по log-likelihood (G², Даннинг).

Для слова w:  a — частота в корпусе, b — в эталоне, c и d — размеры корпуса и эталона.
  E1 = c·(a+b)/(c+d),  E2 = d·(a+b)/(c+d)          (ожидаемые частоты, если разницы нет)
  G² = 2·( a·ln(a/E1) + b·ln(b/E2) )               (при b = 0 второе слагаемое = 0)
G² > 3.84 -> p < 0.05, G² > 15.13 -> p < 0.0001. Берём только слова, которые в корпусе ЧАЩЕ.

Эталон: corpus_kk.txt из ПР 1 (казахская Википедия). Для надёжности лучше ≥ 1 млн слов:
  python get_data.py --lang kk --words 1000000     (в папке ПР 1)

Запуск: python keywords.py corpus.jsonl corpus_kk.txt
"""
import math
import sys
from collections import Counter

import pandas as pd

from common import read_texts, tokenize

MIN_FREQ = 10


def g2(a, b, c, d):
    e1, e2 = c * (a + b) / (c + d), d * (a + b) / (c + d)
    return 2 * (a * math.log(a / e1) + (b * math.log(b / e2) if b else 0))


if __name__ == "__main__":
    corpus = Counter(t for x in read_texts(sys.argv[1]) for t in tokenize(x))
    ref = Counter(t for x in read_texts(sys.argv[2]) for t in tokenize(x))
    c, d = sum(corpus.values()), sum(ref.values())

    rows = []
    for w, a in corpus.items():
        b = ref.get(w, 0)
        if a < MIN_FREQ or a / c <= b / d:
            continue
        rows.append({"слово": w, "f_корпус": a, "f_эталон": b,
                     "на млн (корпус)": round(a / c * 1e6, 1),
                     "на млн (эталон)": round(b / d * 1e6, 1),
                     "G2": round(g2(a, b, c, d), 1),
                     "log2 ratio": round(math.log2((a / c) / ((b + 0.5) / d)), 2)})

    df = pd.DataFrame(rows).sort_values("G2", ascending=False).head(200)
    df.to_csv("keywords_top200.csv", index=False)
    print(f"Корпус: {c} токенов, эталон: {d} токенов\n")
    print(df.head(50).to_markdown(index=False))
    print("\nТоп-200: keywords_top200.csv -> выбери вручную 50 терминов в terms_50.csv")
