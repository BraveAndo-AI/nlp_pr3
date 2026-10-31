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
Модель определения языка (1 МБ) — скачай [lid.176.ftz](https://dl.fbaipublicfiles.com/fasttext/supervised-models/lid.176.ftz) и положи в папку проекта.

## Запуск

```powershell
python collect.py --n 6000                       # 1: ~5-15 минут, corpus.jsonl + collect_log.json
python stats.py corpus.jsonl                     # 2: stats.json, doc_lengths.png
python zipf_heaps.py corpus.jsonl                # 3: zipf.png, heaps.png
python keywords.py corpus.jsonl ..\pr1\corpus_kk.txt   # 4: keywords_top200.csv
```
Для задания 4 эталон лучше побольше: в папке ПР 1 `python get_data.py --lang kk --words 1000000`.

## Разметка (задание 5) в Label Studio

Label Studio ставь **в отдельное окружение**, у него много своих зависимостей:
```powershell
python -m venv ls_env
ls_env\Scripts\activate
pip install label-studio
label-studio start          # откроется http://localhost:8080
```
1. `cd annotation` → `python make_tasks.py ..\corpus.jsonl` → появятся `tasks_round1.json` (200) и `tasks_round2.json` (100).
2. В Label Studio создай **два проекта** — `Round1_A` (ты) и `Round1_B` (второй докторант). В каждом: *Settings → Labeling Interface → Code* → вставь `labelstudio_config.xml`; *Import* → `tasks_round1.json`.
3. Каждый размечает свой проект **независимо**, не подглядывая. Инструкция — `annotation_guide.md`.
4. *Export → CSV* из обоих проектов → `A.csv`, `B.csv`.
5. `python agreement.py A.csv B.csv` → κ, α, матрица ошибок, `disagreements.csv`.
6. Вместе разберите расхождения, допишите раздел «Изменения в v2» в инструкции.
7. Повторите шаги 2–5 с `tasks_round2.json` (100 примеров) и сравните κ раунда 1 и 2.

---

## Что писать в отчёт

**Задание 1.** Источник, лицензия, период, язык — в `datasheet.md`. Сколько отсеяно фильтрами и дедупликацией — из `collect_log.json`.

**Задание 2.** Таблица из `stats.json`. Важно: **TTR зависит от размера корпуса** (чем больше текста, тем ниже TTR, потому что частые слова повторяются), поэтому TTR разных корпусов сравнивают только при одинаковом N.

**Задание 3.**
- Ципф: $f(r) = C/r^s$, после логарифмирования — прямая $\log f = \log C - s\log r$, $s$ находим МНК. Для естественных языков $s \approx 1$.
- Хипс: $V(n) = K n^{\beta}$, обычно $\beta \approx 0.4\text{–}0.6$. Для казахского ожидается **больше**, чем для русского и английского: из-за агглютинации (`бала, балалар, балаларға, балаларымызға…`) почти каждая новая форма — новый тип.
- Почему хвост отклоняется от прямой:
  1. **«Лестница» внизу**: частоты — целые числа, тысячи слов имеют одинаковую частоту 1, 2, 3 → горизонтальные ступеньки. Hapax legomena обычно ~40–60 % типов.
  2. **Конечная выборка**: редкие слова недооценены, хвост «обрезан» — реальная частота многих слов меньше 1 на этот объём текста.
  3. **Голова** (ранги 1–10): служебные слова (`және`, `бұл`, `мен`) — отдельный класс, они не подчиняются той же закономерности, поэтому МНК лучше считать по середине.
  4. **Мусор веб-текстов**: опечатки, имена, транслит раздувают хвост.

**Задание 4.** G² — это тест отношения правдоподобия: насколько частота слова в корпусе неслучайно отличается от эталона ($G^2 > 15.13 \Rightarrow p < 0.0001$). Из `keywords_top200.csv` вручную выбери 50 терминов предметной области в `terms_50.csv`, отбросив имена, опечатки и служебный мусор сайтов. Отдельно отметь, что одно слово дробится на формы (`жаңалық`, `жаңалықтар`, `жаңалықтары`) — можно объединить их стеммером из ПР 2.

**Задание 5.** Таблицы из `agreement.py` для раундов 1 и 2, 5–10 разобранных расхождений и какие правила добавлены в v2. κ и α близки, когда оба аннотатора ставят метки с похожими частотами; если один чаще ставит BAD, α будет немного выше κ — это нормально.

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
