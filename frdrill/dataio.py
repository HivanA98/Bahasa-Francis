"""Pemuat data dan daftar nilai yang sah.

Satu-satunya sumber data adalah berkas JSON di folder data/. Berkas CSV di
data/csv/ dan anki/, lembar kerja di worksheets/, serta webdata.js adalah
hasil ekspor yang dibuat ulang oleh tools/ — bukan sumber yang diedit langsung.
"""

from __future__ import annotations

import json
import os
from functools import lru_cache

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DATA_DIR = os.path.join(ROOT, "data")

MODULE_FILES = {
    "kosakata": "kosakata.json",
    "tatabahasa": "tatabahasa.json",
    "konjugasi": "konjugasi.json",
    "pelafalan": "pelafalan.json",
    "serapan": "serapan.json",
}

#: Kelas kata, memakai istilah Prancis seperti pada buku pelajaran.
POS_VALUES = {
    "nom", "verbe", "adjectif", "adverbe", "pronom", "préposition",
    "conjonction", "nombre", "expression",
}

GENRE_VALUES = {"m", "f", "m/f", None}

#: Kategori untuk saringan di aplikasi web, beserta labelnya.
CAT_LABELS = {
    "salutation": "Sapaan & kesantunan",
    "pronom": "Kata ganti",
    "nombre": "Angka",
    "famille": "Keluarga",
    "personne": "Orang",
    "objet": "Benda sehari-hari",
    "nourriture": "Makanan & minuman",
    "couleur": "Warna",
    "lieu": "Tempat & kendaraan",
    "temps": "Waktu",
    "verbe": "Kata kerja",
    "adjectif": "Kata sifat",
    "question": "Kata tanya",
    "mot-outil": "Kata tugas",
}

POS_LABELS = {
    "nom": "kata benda",
    "verbe": "kata kerja",
    "adjectif": "kata sifat",
    "adverbe": "kata keterangan",
    "pronom": "kata ganti",
    "préposition": "kata depan",
    "conjonction": "kata hubung",
    "nombre": "angka",
    "expression": "ungkapan",
}

GENRE_LABELS = {"m": "maskulin", "f": "feminin", "m/f": "maskulin/feminin"}

#: Label untuk jenis liaison; dipakai sebagai kunci jawaban soal liaison.
LIAISON_LABELS = {
    "obligatoire": "Wajib",
    "facultative": "Boleh, bergantung keresmian",
    "interdite": "Terlarang",
}

MAX_STAGE = 6
LEVELS = (1, 2, 3)


def _read_json(path: str) -> dict:
    with open(path, encoding="utf-8") as f:
        return json.load(f)


@lru_cache(maxsize=None)
def load(name: str) -> dict:
    """Muat satu modul data berdasarkan nama ('kosakata', 'tatabahasa', ...)."""
    if name not in MODULE_FILES:
        raise KeyError(f"modul tidak dikenal: {name}")
    return _read_json(os.path.join(DATA_DIR, MODULE_FILES[name]))


def load_all() -> dict[str, dict]:
    return {name: load(name) for name in MODULE_FILES}


def _until(items: list[dict], stage: int | None) -> list[dict]:
    if stage is None:
        return list(items)
    return [i for i in items if i["stage"] <= stage]


# -------------------------------------------------------------- kosakata ---

def vocab_entries(stage: int | None = None) -> list[dict]:
    return _until(load("kosakata")["entries"], stage)


def nouns(stage: int | None = None) -> list[dict]:
    """Kata benda saja; dipakai mode latihan gender dan artikel."""
    return [e for e in vocab_entries(stage) if e["pos"] == "nom"]


def adjectives(stage: int | None = None) -> list[dict]:
    return [e for e in vocab_entries(stage) if e["pos"] == "adjectif"]


# ------------------------------------------------------------ tata bahasa ---

def grammar_topics(stage: int | None = None) -> list[dict]:
    return _until(load("tatabahasa")["topics"], stage)


def grammar_items(stage: int | None = None) -> list[dict]:
    out: list[dict] = []
    for topic in load("tatabahasa")["topics"]:
        if stage is not None and topic["stage"] > stage:
            continue
        for item in topic["items"]:
            out.append({
                **item,
                "topic_id": topic["id"],
                "topic_title": topic["title"],
                "stage": topic["stage"],
            })
    return out


# -------------------------------------------------------------- konjugasi ---

def verb_groups(stage: int | None = None) -> list[dict]:
    return _until(load("konjugasi")["groupes"], stage)


def verbs(stage: int | None = None) -> list[dict]:
    return _until(load("konjugasi")["verbes"], stage)


def verb_items(stage: int | None = None) -> list[dict]:
    return _until(load("konjugasi")["items"], stage)


def verb_by_id(verb_id: str) -> dict | None:
    return next((v for v in load("konjugasi")["verbes"] if v["id"] == verb_id), None)


# -------------------------------------------------------------- pelafalan ---

def phon_rules(stage: int | None = None) -> list[dict]:
    return _until(load("pelafalan")["regles"], stage)


def phon_items(stage: int | None = None, kind: str | None = None) -> list[dict]:
    items = _until(load("pelafalan")["items"], stage)
    if kind is not None:
        items = [i for i in items if i["type"] == kind]
    return items


def phon_passages(stage: int | None = None, level: int | None = None) -> list[dict]:
    out = _until(load("pelafalan")["passages"], stage)
    if level is not None:
        out = [p for p in out if p["level"] == level]
    return out


def phon_scheme() -> list[dict]:
    return list(load("pelafalan")["skema_lafal"])


def rule_by_id(rule_id: str) -> dict | None:
    return next((r for r in load("pelafalan")["regles"] if r["id"] == rule_id), None)


# ---------------------------------------------------------------- serapan ---

def loan_entries(stage: int | None = None) -> list[dict]:
    return _until(load("serapan")["entries"], stage)


def loan_items(stage: int | None = None) -> list[dict]:
    return _until(load("serapan")["items"], stage)


# ------------------------------------------------------------------ kartu ---

def all_card_ids() -> list[str]:
    """Semua id yang dipakai sebagai kartu Leitner, dari seluruh modul."""
    ids: list[str] = [e["id"] for e in vocab_entries()]
    ids += [i["id"] for i in grammar_items()]
    ids += [v["id"] for v in verbs()]
    ids += [i["id"] for i in verb_items()]
    ids += [i["id"] for i in phon_items()]
    ids += [p["id"] for p in phon_passages()]
    ids += [i["id"] for i in loan_items()]
    return ids


__all__ = [
    "CAT_LABELS",
    "DATA_DIR",
    "GENRE_LABELS",
    "GENRE_VALUES",
    "LEVELS",
    "LIAISON_LABELS",
    "MAX_STAGE",
    "MODULE_FILES",
    "POS_LABELS",
    "POS_VALUES",
    "ROOT",
    "adjectives",
    "all_card_ids",
    "grammar_items",
    "grammar_topics",
    "load",
    "load_all",
    "loan_entries",
    "loan_items",
    "nouns",
    "phon_items",
    "phon_passages",
    "phon_rules",
    "phon_scheme",
    "rule_by_id",
    "verb_by_id",
    "verb_groups",
    "verb_items",
    "verbs",
    "vocab_entries",
]
