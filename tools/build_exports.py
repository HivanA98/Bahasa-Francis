#!/usr/bin/env python3
"""Buat ulang ekspor CSV dari data/*.json.

Hasilnya:
  data/csv/*.csv   tabel mentah untuk dibaca di penyunting lembar kerja
  anki/*.csv       berkas impor untuk Anki (tanpa baris judul)

Berkas JSON di data/ adalah satu-satunya sumber data. Jangan menyunting hasil
ekspor; sunting JSON-nya lalu jalankan ulang skrip ini.

    python tools/build_exports.py
"""

from __future__ import annotations

import csv
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from frdrill import conjugaison, dataio  # noqa: E402
from frdrill.phonetique import approx, elide  # noqa: E402
from frdrill.questions import vocab_detail, vocab_display  # noqa: E402

ROOT = dataio.ROOT
CSV_DIR = os.path.join(ROOT, "data", "csv")
ANKI_DIR = os.path.join(ROOT, "anki")

#: Baris pengarah untuk Anki 2.1.55 ke atas. Versi Anki yang lebih tua tidak
#: mengenalinya; hapus baris-baris ini bila impor gagal (lihat anki/README.md).
ANKI_DIRECTIVES = ["#separator:Comma", "#html:false"]


def _write_csv(path: str, header: list[str], rows: list[list[str]]) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f, lineterminator="\n", quoting=csv.QUOTE_MINIMAL)
        if header:
            w.writerow(header)
        w.writerows(rows)
    print(f"  {os.path.relpath(path, ROOT)}  ({len(rows)} baris)")


def _write_anki(path: str, rows: list[list[str]], tags_column: int) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="") as f:
        for line in ANKI_DIRECTIVES:
            f.write(line + "\n")
        f.write(f"#tags column:{tags_column}\n")
        w = csv.writer(f, lineterminator="\n", quoting=csv.QUOTE_ALL)
        w.writerows(rows)
    print(f"  {os.path.relpath(path, ROOT)}  ({len(rows)} kartu)")


def _s(value: object) -> str:
    """Ubah nilai menjadi teks; None dan daftar kosong menjadi string kosong."""
    if value is None:
        return ""
    if isinstance(value, list):
        return "; ".join(str(v) for v in value)
    return str(value)


def _lafal(ipa: str) -> str:
    return f"/{ipa}/ ({approx(ipa)})" if ipa else ""


# ---------------------------------------------------------------- data/csv ---

def export_kosakata_csv() -> None:
    header = [
        "id", "fr", "display", "ipa", "approx", "gloss", "alt", "pos", "genre",
        "article", "pluriel", "feminin", "morpho_note", "h_aspire",
        "example_fr", "example_gloss", "cat", "stage", "note",
    ]
    rows = [
        [
            e["id"], e["fr"], vocab_display(e), e["ipa"], approx(e["ipa"]), e["gloss"],
            _s(e.get("alt")), e["pos"], _s(e.get("genre")), _s(e.get("article")),
            _s(e.get("pluriel")), _s(e.get("feminin")), _s(e.get("morpho_note")),
            "oui" if e.get("h_aspire") else "non",
            e["example"]["fr"], e["example"]["gloss"], e["cat"], str(e["stage"]),
            _s(e.get("note")),
        ]
        for e in dataio.vocab_entries()
    ]
    _write_csv(os.path.join(CSV_DIR, "kosakata.csv"), header, rows)


def export_tatabahasa_csv() -> None:
    _write_csv(
        os.path.join(CSV_DIR, "tatabahasa_topics.csv"),
        ["id", "stage", "title", "explanation", "caveats", "examples"],
        [
            [t["id"], str(t["stage"]), t["title"], t["explanation"],
             " | ".join(t.get("caveats") or []),
             " | ".join(f"{x['fr']} = {x['gloss']}" for x in t["examples"])]
            for t in dataio.grammar_topics()
        ],
    )
    _write_csv(
        os.path.join(CSV_DIR, "tatabahasa_items.csv"),
        ["id", "topic_id", "stage", "type", "prompt", "prompt_fr", "options_lang",
         "options", "answer", "answer_text", "explain"],
        [
            [i["id"], i["topic_id"], str(i["stage"]), i["type"], i["prompt"],
             _s(i.get("prompt_fr")), i["options_lang"], " | ".join(i["options"]),
             str(i["answer"]), i["options"][i["answer"]], _s(i.get("explain"))]
            for i in dataio.grammar_items()
        ],
    )


def export_konjugasi_csv() -> None:
    _write_csv(
        os.path.join(CSV_DIR, "konjugasi_verbes.csv"),
        ["id", "infinitif", "ipa", "approx", "gloss", "modele", "groupe", "stage",
         "je", "tu", "il", "nous", "vous", "ils", "participe_passe", "auxiliaire",
         "note", "lafal_note", "example_fr", "example_gloss"],
        [
            [v["id"], v["infinitif"], v["ipa"], approx(v["ipa"]), v["gloss"],
             v["modele"], str(v["groupe"]), str(v["stage"]), *v["present"],
             v["participe_passe"], v["auxiliaire"], _s(v.get("note")),
             _s(v.get("lafal_note")), v["example"]["fr"], v["example"]["gloss"]]
            for v in dataio.verbs()
        ],
    )
    _write_csv(
        os.path.join(CSV_DIR, "konjugasi_items.csv"),
        ["id", "stage", "prompt", "prompt_fr", "options_lang", "options", "answer",
         "answer_text", "explain"],
        [
            [i["id"], str(i["stage"]), i["prompt"], _s(i.get("prompt_fr")),
             i["options_lang"], " | ".join(i["options"]), str(i["answer"]),
             i["options"][i["answer"]], _s(i.get("explain"))]
            for i in dataio.verb_items()
        ],
    )


def export_pelafalan_csv() -> None:
    _write_csv(
        os.path.join(CSV_DIR, "pelafalan_regles.csv"),
        ["id", "stage", "titre", "graphies", "ipa", "explication", "exemples", "note"],
        [
            [r["id"], str(r["stage"]), r["titre"], _s(r["graphies"]), _s(r["ipa"]),
             r["explication"],
             " | ".join(f"{x['fr']} = /{x['ipa']}/ ({x['gloss']})" for x in r["exemples"]),
             _s(r.get("note"))]
            for r in dataio.phon_rules()
        ],
    )
    rows = []
    for i in dataio.phon_items():
        if i["type"] == "elision":
            kunci = elide(i["mots"][0], i["mots"][1])
        else:
            kunci = i["options"][i["answer"]]
        rows.append([
            i["id"], i["type"], str(i["stage"]), i["regle"], _s(i.get("prompt_fr")),
            _s(i.get("gloss")), i["ipa"], approx(i["ipa"]) if i["ipa"] else "",
            " | ".join(i["options"]), _s(i["options_ipa"]), str(i["answer"]), kunci,
            _s(i.get("liaison_type")), _s(i.get("mots")), _s(i.get("explain")),
        ])
    _write_csv(
        os.path.join(CSV_DIR, "pelafalan_items.csv"),
        ["id", "type", "stage", "regle", "prompt_fr", "gloss", "ipa", "approx",
         "options", "options_ipa", "answer", "answer_text", "liaison_type", "mots",
         "explain"],
        rows,
    )
    _write_csv(
        os.path.join(CSV_DIR, "pelafalan_passages.csv"),
        ["id", "stage", "level", "fr", "ipa", "approx", "gloss", "note"],
        [
            [p["id"], str(p["stage"]), str(p["level"]), p["fr"], p["ipa"],
             approx(p["ipa"]), p["gloss"], _s(p.get("note"))]
            for p in dataio.phon_passages()
        ],
    )


def export_serapan_csv() -> None:
    _write_csv(
        os.path.join(CSV_DIR, "serapan_entries.csv"),
        ["id", "fr", "ipa", "approx", "genre", "kind", "indonesien", "sens_fr",
         "ecart", "note", "stage"],
        [
            [e["id"], e["fr"], e["ipa"], approx(e["ipa"]), _s(e.get("genre")),
             e["kind"], e["indonesien"], e["sens_fr"], _s(e.get("ecart")),
             _s(e.get("note")), str(e["stage"])]
            for e in dataio.loan_entries()
        ],
    )
    _write_csv(
        os.path.join(CSV_DIR, "serapan_items.csv"),
        ["id", "stage", "prompt", "prompt_fr", "options_lang", "options", "answer",
         "answer_text", "explain"],
        [
            [i["id"], str(i["stage"]), i["prompt"], _s(i.get("prompt_fr")),
             i["options_lang"], " | ".join(i["options"]), str(i["answer"]),
             i["options"][i["answer"]], _s(i.get("explain"))]
            for i in dataio.loan_items()
        ],
    )


# -------------------------------------------------------------------- anki ---

def export_anki_kosakata() -> None:
    rows = []
    for e in dataio.vocab_entries():
        rows.append([
            vocab_display(e),
            e["gloss"],
            _lafal(e["ipa"]),
            vocab_detail(e),
            e["example"]["fr"],
            e["example"]["gloss"],
            _s(e.get("note")),
            f"prancis::kosakata prancis::{e['cat']} prancis::tahap{e['stage']}",
        ])
    _write_anki(os.path.join(ANKI_DIR, "kosakata.csv"), rows, tags_column=8)


def export_anki_tatabahasa() -> None:
    rows = []
    for i in dataio.grammar_items():
        front = i["prompt"]
        if i.get("prompt_fr"):
            front += "<br>" + i["prompt_fr"]
        rows.append([
            front,
            i["options"][i["answer"]],
            _s(i.get("explain")),
            i["topic_title"],
            f"prancis::tatabahasa prancis::{i['topic_id']} prancis::tahap{i['stage']}",
        ])
    _write_anki(os.path.join(ANKI_DIR, "tatabahasa.csv"), rows, tags_column=5)


def export_anki_konjugasi() -> None:
    rows = []
    for v in dataio.verbs():
        tabel = "<br>".join(
            conjugaison.forme_affichee(i, f) for i, f in enumerate(v["present"])
        )
        rows.append([
            v["infinitif"],
            tabel,
            v["gloss"],
            _lafal(v["ipa"]),
            f"{v['auxiliaire']} + {v['participe_passe']}",
            _s(v.get("note")),
            f"prancis::konjugasi prancis::{v['modele']} prancis::tahap{v['stage']}",
        ])
    _write_anki(os.path.join(ANKI_DIR, "konjugasi.csv"), rows, tags_column=7)


def export_anki_pelafalan() -> None:
    rows = []
    for p in dataio.phon_passages():
        rows.append([
            p["fr"],
            _lafal(p["ipa"]),
            p["gloss"],
            _s(p.get("note")),
            f"prancis::pelafalan prancis::level{p['level']} prancis::tahap{p['stage']}",
        ])
    for r in dataio.phon_rules():
        rows.append([
            f"{_s(r['graphies'])} — {r['titre']}",
            r["explication"],
            " · ".join(f"{x['fr']} {_lafal(x['ipa'])}" for x in r["exemples"]),
            _s(r.get("note")),
            f"prancis::pelafalan prancis::{r['id']} prancis::tahap{r['stage']}",
        ])
    _write_anki(os.path.join(ANKI_DIR, "pelafalan.csv"), rows, tags_column=5)


def export_anki_serapan() -> None:
    rows = [
        [
            e["fr"],
            e["sens_fr"],
            _lafal(e["ipa"]),
            f"mirip: {e['indonesien']}",
            _s(e.get("ecart")) or "Artinya sama.",
            f"prancis::serapan prancis::{e['kind']} prancis::tahap{e['stage']}",
        ]
        for e in dataio.loan_entries()
    ]
    _write_anki(os.path.join(ANKI_DIR, "serapan.csv"), rows, tags_column=6)


def main() -> int:
    print("Membuat ekspor CSV dari data/*.json")
    print("data/csv/:")
    export_kosakata_csv()
    export_tatabahasa_csv()
    export_konjugasi_csv()
    export_pelafalan_csv()
    export_serapan_csv()
    print("anki/:")
    export_anki_kosakata()
    export_anki_tatabahasa()
    export_anki_konjugasi()
    export_anki_pelafalan()
    export_anki_serapan()
    print("Selesai.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
