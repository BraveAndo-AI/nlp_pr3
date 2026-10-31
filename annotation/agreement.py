"""Согласованность двух аннотаторов: Cohen's κ и Krippendorff's α (номинальная шкала).

Вход: два CSV-экспорта из Label Studio (по одному на аннотатора) с колонками doc_id и quality.

Cohen's κ:
  p_o = доля совпавших меток
  p_e = Σ_k p_A(k)·p_B(k)                 (совпадение «случайно», по частотам каждого)
  κ   = (p_o − p_e) / (1 − p_e)

Krippendorff's α (2 аннотатора, без пропусков):
  каждая пара меток (a, b) даёт в матрицу совпадений o[a][b] и o[b][a];
  n_c — сумма строки c, n = 2·N — всего меток
  α = 1 − (n − 1)·Σ_{c≠k} o[c][k] / Σ_{c≠k} n_c·n_k
Отличие от κ: ожидаемое совпадение считается по ОБЩЕМУ распределению меток обоих аннотаторов.

Шкала Landis & Koch для κ: <0.2 слабая, 0.21–0.4 удовлетворительная, 0.41–0.6 умеренная,
0.61–0.8 существенная, >0.8 почти полная.

Запуск: python agreement.py annotator_A.csv annotator_B.csv
"""
import sys
from collections import Counter

import pandas as pd


def cohen_kappa(a, b):
    n = len(a)
    p_o = sum(x == y for x, y in zip(a, b)) / n
    ca, cb = Counter(a), Counter(b)
    p_e = sum(ca[k] * cb[k] for k in set(a) | set(b)) / n ** 2
    return (p_o - p_e) / (1 - p_e) if p_e < 1 else 1.0


def krippendorff_alpha(a, b):
    o = Counter()
    for x, y in zip(a, b):
        o[(x, y)] += 1
        o[(y, x)] += 1
    n_c = Counter()
    for (x, _), v in o.items():
        n_c[x] += v
    n = sum(n_c.values())
    disagree = sum(v for (x, y), v in o.items() if x != y)
    expected = sum(n_c[x] * n_c[y] for x in n_c for y in n_c if x != y)
    return 1 - (n - 1) * disagree / expected if expected else 1.0


def load(path, col):
    df = pd.read_csv(path)
    return df[["doc_id", col] + (["comment"] if "comment" in df else [])]


if __name__ == "__main__":
    col = "quality"
    A, B = load(sys.argv[1], col), load(sys.argv[2], col)
    m = A.merge(B, on="doc_id", suffixes=("_A", "_B")).dropna(subset=[f"{col}_A", f"{col}_B"])
    a, b = m[f"{col}_A"].tolist(), m[f"{col}_B"].tolist()

    res = {"примеров": len(m),
           "совпадение, %": round(100 * sum(x == y for x, y in zip(a, b)) / len(m), 1),
           "Cohen's κ": round(cohen_kappa(a, b), 3),
           "Krippendorff's α": round(krippendorff_alpha(a, b), 3)}
    print(pd.Series(res).to_markdown())

    print("\nМатрица ошибок (строки — A, столбцы — B):")
    print(pd.crosstab(m[f"{col}_A"], m[f"{col}_B"], margins=True).to_markdown())

    dis = m[m[f"{col}_A"] != m[f"{col}_B"]]
    dis.to_csv("disagreements.csv", index=False)
    print(f"\nРасхождений: {len(dis)} -> disagreements.csv (разобрать и уточнить инструкцию)")
