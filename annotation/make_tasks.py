"""Выборка документов для разметки в формате импорта Label Studio.

Раунд 1 — 200 документов, раунд 2 — другие 100 (после уточнения инструкции).
Текст обрезается до ~1500 символов, чтобы разметка шла быстро.

Запуск: python make_tasks.py ../corpus.jsonl
"""
import json
import random
import sys

sys.path.insert(0, "..")
from common import read_jsonl

docs = read_jsonl(sys.argv[1] if len(sys.argv) > 1 else "../corpus.jsonl")
random.Random(42).shuffle(docs)


def task(d):
    text = d["text"]
    if len(text) > 1500:
        text = text[:1500].rsplit(" ", 1)[0] + " …"
    return {"data": {"doc_id": d["id"], "text": text}}


for name, part in [("tasks_round1.json", docs[:200]), ("tasks_round2.json", docs[200:300])]:
    json.dump([task(d) for d in part], open(name, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(name, len(part))
