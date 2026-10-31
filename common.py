"""Общие функции: чтение корпуса и токенизация."""
import json
import re

TOKEN_RE = re.compile(r"[^\W\d_]+")   # только буквы (любой алфавит), без цифр и знаков


def tokenize(text):
    return TOKEN_RE.findall(text.lower())


def read_jsonl(path):
    with open(path, encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


def read_texts(path):
    """Корпус .jsonl (поле text) или обычный .txt (абзацы через пустую строку)."""
    if path.endswith(".jsonl"):
        return [d["text"] for d in read_jsonl(path)]
    return [p for p in open(path, encoding="utf-8").read().split("\n\n") if p.strip()]
