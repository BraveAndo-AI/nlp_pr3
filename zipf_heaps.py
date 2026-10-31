"""Задание 3. Законы Ципфа и Хипса.

Ципф:  f(r) = C / r^s        ->  log f = log C - s·log r      (МНК по точкам (log r, log f))
Хипс:  V(n) = K · n^β        ->  log V = log K + β·log n      (МНК по точкам (log n, log V))

МНК для прямой y = a + b·x:  b = Σ(x-x̄)(y-ȳ) / Σ(x-x̄)²,  a = ȳ - b·x̄  (np.polyfit делает то же самое).
Ципфа оцениваем дважды: по всем рангам и по «середине» (ранги 10..10⁴), т.к. голова и хвост отклоняются.

Запуск: python zipf_heaps.py corpus.jsonl
"""
import sys
from collections import Counter

import matplotlib.pyplot as plt
import numpy as np

from common import read_texts, tokenize


def ols(x, y):
    b, a = np.polyfit(x, y, 1)
    r2 = 1 - np.sum((y - (a + b * x)) ** 2) / np.sum((y - y.mean()) ** 2)
    return a, b, r2


if __name__ == "__main__":
    tokens = [t for text in read_texts(sys.argv[1] if len(sys.argv) > 1 else "corpus.jsonl")
              for t in tokenize(text)]

    # ---------- Ципф ----------
    freqs = np.array(sorted(Counter(tokens).values(), reverse=True), dtype=float)
    ranks = np.arange(1, len(freqs) + 1)
    lr, lf = np.log10(ranks), np.log10(freqs)

    a_all, b_all, r2_all = ols(lr, lf)
    mid = (ranks >= 10) & (ranks <= 10_000)
    a_mid, b_mid, r2_mid = ols(lr[mid], lf[mid])
    print(f"Ципф, все ранги:      s = {-b_all:.3f}, R² = {r2_all:.3f}")
    print(f"Ципф, ранги 10..10⁴:  s = {-b_mid:.3f}, R² = {r2_mid:.3f}")
    print(f"Hapax legomena (f=1): {np.sum(freqs == 1)} из {len(freqs)} типов "
          f"({100 * np.mean(freqs == 1):.1f}%)")

    plt.figure(figsize=(7, 5))
    plt.loglog(ranks, freqs, ".", ms=2, alpha=0.5, label="корпус")
    plt.loglog(ranks, 10 ** (a_mid + b_mid * lr), "r-", label=f"МНК (10..10⁴): s = {-b_mid:.2f}")
    plt.loglog(ranks, freqs[0] / ranks, "k--", lw=1, label="идеальный Ципф, s = 1")
    plt.xlabel("Ранг r (log)")
    plt.ylabel("Частота f (log)")
    plt.title("Закон Ципфа")
    plt.legend()
    plt.tight_layout()
    plt.savefig("zipf.png", dpi=150)

    # ---------- Хипс ----------
    checkpoints = np.unique(np.logspace(2, np.log10(len(tokens)), 60).astype(int))
    seen, V, j = set(), [], 0
    for i, t in enumerate(tokens, 1):
        seen.add(t)
        if j < len(checkpoints) and i == checkpoints[j]:
            V.append(len(seen))
            j += 1
    n, V = checkpoints[:len(V)], np.array(V)
    a_h, beta, r2_h = ols(np.log10(n), np.log10(V))
    print(f"Хипс: V = {10 ** a_h:.2f} · n^{beta:.3f}, R² = {r2_h:.3f}")

    plt.figure(figsize=(7, 5))
    plt.loglog(n, V, "o", ms=3, label="корпус")
    plt.loglog(n, 10 ** a_h * n ** beta, "r-", label=f"V = {10 ** a_h:.1f}·n^{beta:.2f}")
    plt.xlabel("Число токенов n (log)")
    plt.ylabel("Размер словаря V (log)")
    plt.title("Закон Хипса")
    plt.legend()
    plt.tight_layout()
    plt.savefig("heaps.png", dpi=150)
    print("Графики: zipf.png, heaps.png")
