#!/usr/bin/env python3
"""Buat lembar kerja Markdown beserta kunci jawaban terpisah.

    python tools/build_worksheets.py

Hasilnya:
  worksheets/ws-NN.md                 lembar kerja (tanpa jawaban)
  worksheets/answers/ws-NN-kunci.md   kunci jawaban

Isi lembar kerja diambil langsung dari data/*.json dengan generator acak
ber-seed tetap, sehingga menjalankan ulang skrip ini menghasilkan lembar yang
sama persis. Kunci jawaban dibuat pada proses yang sama dengan soalnya,
sehingga tidak mungkin tidak sinkron.
"""

from __future__ import annotations

import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from frdrill import conjugaison, dataio  # noqa: E402
from frdrill.phonetique import approx, elide  # noqa: E402
from frdrill.questions import vocab_display  # noqa: E402

ROOT = dataio.ROOT
WS_DIR = os.path.join(ROOT, "worksheets")
KEY_DIR = os.path.join(WS_DIR, "answers")

#: (nomor lembar, tahap). Dua lembar per tahap, enam tahap.
PLAN = [(n, (n + 1) // 2) for n in range(1, 13)]

N_VOCAB_FR = 8
N_VOCAB_ID = 6
N_ARTICLE = 6
N_VERBS = 2
N_GRAMMAR = 5
N_PHON = 4
BLANK = " " * 20


class Picker:
    """Pengambil butir yang menghindari pengulangan antar lembar kerja."""

    def __init__(self, seed: int) -> None:
        self.rng = random.Random(seed)
        self.used: set[str] = set()

    def take(self, pool: list[dict], n: int, key: str = "id") -> list[dict]:
        fresh = [x for x in pool if x[key] not in self.used]
        self.rng.shuffle(fresh)
        chosen = fresh[:n]
        if len(chosen) < n:
            # Kolam sudah habis; ulangi butir lama agar lembar tetap penuh.
            rest = [x for x in pool if x[key] not in {c[key] for c in chosen}]
            self.rng.shuffle(rest)
            chosen += rest[: n - len(chosen)]
        for c in chosen:
            self.used.add(c[key])
        return chosen


def _mcq_block(lines: list[str], n: int, item: dict) -> None:
    lines.append(f"{n}. {item['prompt']}")
    if item.get("prompt_fr"):
        lines.append("")
        lines.append(f"   > {item['prompt_fr']}")
    lines.append("")
    for i, opt in enumerate(item["options"]):
        lines.append(f"   {chr(ord('a') + i)}. {opt}")
    lines.append("")
    lines.append("   Jawaban: ____")
    lines.append("")


def build_worksheet(number: int, stage: int, pickers: dict[str, Picker]) -> tuple[str, str]:
    vocab_pool = dataio.vocab_entries(stage)
    noun_pool = dataio.nouns(stage)
    verb_pool = dataio.verbs(stage)
    grammar_pool = dataio.grammar_items(stage) + dataio.loan_items(stage)
    phon_pool = [
        i for i in dataio.phon_items(stage)
        if i["type"] in ("lafal", "homophone", "elision")
    ]

    v_fr = pickers["vocab_fr"].take(vocab_pool, N_VOCAB_FR)
    v_id = pickers["vocab_id"].take(vocab_pool, N_VOCAB_ID)
    arts = pickers["article"].take(noun_pool, min(N_ARTICLE, len(noun_pool)))
    verbs = pickers["verbe"].take(verb_pool, min(N_VERBS, len(verb_pool)))
    gram = pickers["grammar"].take(grammar_pool, N_GRAMMAR)
    phon = pickers["phon"].take(phon_pool, min(N_PHON, len(phon_pool)))

    ws: list[str] = []
    key: list[str] = []
    tag = f"ws-{number:02d}"

    ws.append(f"# Lembar kerja {number:02d} · tahap {stage}")
    ws.append("")
    ws.append(
        "Kerjakan dengan tulisan tangan tanpa membuka data. Menulis sendiri aksen "
        "dan artikelnya adalah bagian dari latihannya. Perkiraan waktu 20-30 menit."
    )
    ws.append("")
    ws.append(f"Kunci jawaban: `worksheets/answers/{tag}-kunci.md`")
    ws.append("")

    key.append(f"# Kunci jawaban · lembar kerja {number:02d} · tahap {stage}")
    key.append("")
    key.append(f"Soal: `worksheets/{tag}.md`")
    key.append("")

    # --- A. Prancis ke Indonesia ------------------------------------------
    ws.append("## A. Tulis arti kata berikut dalam Bahasa Indonesia")
    ws.append("")
    ws.append("| No | Kata | Arti |")
    ws.append("|---:|:-----|:-----|")
    key.append("## A. Arti kata")
    key.append("")
    key.append("| No | Kata | Arti | Lafal | Keterangan |")
    key.append("|---:|:-----|:-----|:------|:-----------|")
    for i, e in enumerate(v_fr, 1):
        ws.append(f"| {i} | {vocab_display(e)} | {BLANK} |")
        extra = [dataio.POS_LABELS.get(e["pos"], e["pos"])]
        if e.get("genre"):
            extra.append(dataio.GENRE_LABELS[e["genre"]])
        if e.get("pluriel"):
            extra.append("jamak: " + e["pluriel"])
        key.append(
            f"| {i} | {vocab_display(e)} | {e['gloss']} | "
            f"/{e['ipa']}/ {approx(e['ipa'])} | {' · '.join(extra)} |"
        )
    ws.append("")
    key.append("")

    # --- B. Indonesia ke Prancis ------------------------------------------
    ws.append("## B. Tulis kata Prancis untuk arti berikut")
    ws.append("")
    ws.append("Sertakan artikelnya (le, la, l') bila kata itu kata benda.")
    ws.append("")
    ws.append("| No | Arti | Kata Prancis |")
    ws.append("|---:|:-----|:-------------|")
    key.append("## B. Kata Prancis")
    key.append("")
    key.append("| No | Arti | Kata Prancis | Contoh pemakaian |")
    key.append("|---:|:-----|:-------------|:-----------------|")
    for i, e in enumerate(v_id, 1):
        ws.append(f"| {i} | {e['gloss']} | {BLANK} |")
        key.append(
            f"| {i} | {e['gloss']} | {vocab_display(e)} | "
            f"{e['example']['fr']} = {e['example']['gloss']} |"
        )
    ws.append("")
    key.append("")

    # --- C. Artikel dan jamak ---------------------------------------------
    ws.append("## C. Artikel dan bentuk jamak")
    ws.append("")
    ws.append("Tulis artikel takrifnya (le, la, atau l') dan bentuk jamaknya.")
    ws.append("")
    ws.append("| No | Kata benda | Artikel | Bentuk jamak |")
    ws.append("|---:|:-----------|:--------|:-------------|")
    key.append("## C. Artikel dan bentuk jamak")
    key.append("")
    key.append("| No | Kata benda | Artikel | Bentuk jamak | Gender |")
    key.append("|---:|:-----------|:--------|:-------------|:-------|")
    for i, e in enumerate(arts, 1):
        ws.append(f"| {i} | {e['fr']} | ______ | {BLANK} |")
        key.append(
            f"| {i} | {e['fr']} | {e['article']} | les {e['pluriel']} | "
            f"{dataio.GENRE_LABELS[e['genre']]} |"
        )
    ws.append("")
    key.append("")

    # --- D. Konjugasi ------------------------------------------------------
    ws.append("## D. Lengkapi tabel konjugasi présent")
    ws.append("")
    key.append("## D. Tabel konjugasi")
    key.append("")
    for v in verbs:
        ws.append(f"**{v['infinitif']}** ({v['gloss']})")
        ws.append("")
        ws.append("| Kata ganti | Bentuk |")
        ws.append("|:-----------|:-------|")
        for pronom in conjugaison.PRONOMS_AFFICHES:
            ws.append(f"| {pronom} | {BLANK} |")
        ws.append("")
        key.append(f"**{v['infinitif']}** ({v['gloss']}) — model {v['modele']}")
        key.append("")
        key.append("| Kata ganti | Bentuk |")
        key.append("|:-----------|:-------|")
        for i, (pronom, forme) in enumerate(conjugaison.tableau(v)):
            key.append(f"| {pronom} | {conjugaison.forme_affichee(i, forme)} |")
        key.append("")
        if v.get("note"):
            key.append(f"Catatan: {v['note']}")
            key.append("")

    # --- E. Tata bahasa ----------------------------------------------------
    ws.append("## E. Tata bahasa: pilih satu jawaban")
    ws.append("")
    key.append("## E. Tata bahasa")
    key.append("")
    for i, item in enumerate(gram, 1):
        _mcq_block(ws, i, item)
        letter = chr(ord("a") + item["answer"])
        key.append(f"{i}. **{letter}** — {item['options'][item['answer']]}")
        if item.get("explain"):
            key.append(f"   {item['explain']}")
        topik = item.get("topic_title") or "Modul kata serapan"
        key.append(f"   (topik {item.get('topic_id', 'serapan')}: {topik})")
        key.append("")

    # --- F. Pelafalan ------------------------------------------------------
    ws.append("## F. Pelafalan")
    ws.append("")
    key.append("## F. Pelafalan")
    key.append("")
    for i, item in enumerate(phon, 1):
        if item["type"] == "lafal":
            ws.append(
                f"{i}. Bagaimana **{item['prompt_fr']}** dibunyikan? "
                "Tulis dengan ejaan bantu (mis. bong-zhur)."
            )
            ws.append("")
            ws.append("   Jawaban: " + BLANK)
            ws.append("")
            key.append(
                f"{i}. **{item['prompt_fr']}** = /{item['ipa']}/ "
                f"({approx(item['ipa'])}) — {item['gloss']}"
            )
        elif item["type"] == "homophone":
            ws.append(
                f"{i}. Semua kata berikut dibunyikan /{item['ipa']}/ "
                f"({approx(item['ipa'])}): {', '.join(item['options'])}. "
                f"Mana yang berarti ‘{item['gloss']}’?"
            )
            ws.append("")
            ws.append("   Jawaban: " + BLANK)
            ws.append("")
            key.append(
                f"{i}. **{item['options'][item['answer']]}** — "
                f"‘{item['gloss']}’, dibunyikan /{item['ipa']}/"
            )
        else:  # elision
            a, b = item["mots"]
            ws.append(f"{i}. Gabungkan « {a} » + « {b} » sebagaimana ditulis.")
            ws.append("")
            ws.append("   Jawaban: " + BLANK)
            ws.append("")
            key.append(f"{i}. **{elide(a, b)}** — {item['gloss']}")
        if item.get("explain"):
            key.append(f"   {item['explain']}")
        key.append("")

    return "\n".join(ws).rstrip() + "\n", "\n".join(key).rstrip() + "\n"


def build_index() -> str:
    lines = [
        "# Lembar kerja",
        "",
        "Latihan tertulis yang dibuat dari `data/*.json` oleh "
        "`tools/build_worksheets.py`. Jangan menyunting berkas di folder ini; "
        "sunting datanya lalu jalankan ulang skripnya.",
        "",
        "Setiap lembar memuat enam bagian: arti kata, menulis kata Prancis, "
        "artikel dan jamak, tabel konjugasi, tata bahasa, dan pelafalan.",
        "",
        "| Lembar | Tahap | Kunci |",
        "|:-------|------:|:------|",
    ]
    for number, stage in PLAN:
        tag = f"ws-{number:02d}"
        lines.append(
            f"| [{tag}.md]({tag}.md) | {stage} | "
            f"[answers/{tag}-kunci.md](answers/{tag}-kunci.md) |"
        )
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    os.makedirs(WS_DIR, exist_ok=True)
    os.makedirs(KEY_DIR, exist_ok=True)
    pickers = {
        name: Picker(seed)
        for name, seed in (
            ("vocab_fr", 11), ("vocab_id", 22), ("article", 33),
            ("verbe", 44), ("grammar", 55), ("phon", 66),
        )
    }
    print("Membuat lembar kerja dari data/*.json")
    for number, stage in PLAN:
        ws, key = build_worksheet(number, stage, pickers)
        tag = f"ws-{number:02d}"
        with open(os.path.join(WS_DIR, f"{tag}.md"), "w", encoding="utf-8",
                  newline="\n") as f:
            f.write(ws)
        with open(os.path.join(KEY_DIR, f"{tag}-kunci.md"), "w", encoding="utf-8",
                  newline="\n") as f:
            f.write(key)
        print(f"  worksheets/{tag}.md + kunci (tahap {stage})")
    with open(os.path.join(WS_DIR, "README.md"), "w", encoding="utf-8",
              newline="\n") as f:
        f.write(build_index())
    print("  worksheets/README.md")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
