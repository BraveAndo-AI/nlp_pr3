# ПР 3. Корпус, частотный анализ и разметка

| Файл | Задание |
|---|---|
| `collect.py` | 1 — сбор ≥ 5000 документов, фильтр мусора, дедупликация (SHA-1 + MinHash) → `corpus.jsonl` |
| `stats.py` | 2 — токены, типы, TTR, длины документов, доли kk/ru/en |
| `zipf_heaps.py` | 3 — законы Ципфа и Хипса, МНК, графики |
| `keywords.py` | 4 — ключевые слова против Википедии (log-likelihood G²) |
| `annotation/` | 5 — инструкция, конфиг Label Studio, выборка задач, κ и α |
| `datasheet.md` | 6 — описание корпуса (Datasheet for Datasets) |

## Установка

```powershell
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

## Запуск

```powershell
python collect.py --n 6000                       # 1: ~5-15 минут, corpus.jsonl + collect_log.json
python stats.py corpus.jsonl                     # 2: stats.json, doc_lengths.png
python zipf_heaps.py corpus.jsonl                # 3: zipf.png, heaps.png
python keywords.py corpus.jsonl ..\pr1\corpus_kk.txt   # 4: keywords_top200.csv
```




## Полезные ссылки
- FineWeb-2 (казахский подкорпус `kaz_Cyrl`, ODC-By): https://huggingface.co/datasets/HuggingFaceFW/fineweb-2
- MinHash и LSH, библиотека datasketch: https://ekzhu.com/datasketch/lsh.html
- Broder, «On the resemblance and containment of documents» (MinHash): https://ieeexplore.ieee.org/document/666900
- fastText language identification: https://fasttext.cc/docs/en/language-identification.html
- Jurafsky & Martin, SLP3, гл. 2 (Хипс, словарь корпуса): https://web.stanford.edu/~jurafsky/slp3/2.pdf
- Dunning, «Accurate Methods for the Statistics of Surprise and Coincidence» (log-likelihood): https://aclanthology.org/J93-1003/
- Label Studio, быстрый старт: https://labelstud.io/guide/quick_start
- Artstein & Poesio, «Inter-Coder Agreement for Computational Linguistics» (κ, α): https://aclanthology.org/J08-4004/
- Gebru et al., «Datasheets for Datasets»: https://arxiv.org/abs/1803.09010
- Bender & Friedman, «Data Statements for NLP»: https://aclanthology.org/Q18-1041/
