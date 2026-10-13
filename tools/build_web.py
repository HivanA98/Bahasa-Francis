#!/usr/bin/env python3
"""Buat webdata.js untuk aplikasi kartu di browser.

    python tools/build_web.py

Data tetap bersumber dari data/*.json. Berkas hasilnya dimuat lewat tag
<script>, bukan fetch(), supaya aplikasi jalan baik di GitHub Pages maupun
saat index.html dibuka langsung dari berkas (file://) tanpa masalah CORS.

Teks ditulis sebagai escape \\uXXXX (ASCII murni) supaya tidak bergantung pada
charset yang dikirim peladen.

Semua ejaan bantu, bentuk berartikel, dan baris konjugasi dihitung DI SINI
memakai frdrill/, sehingga logikanya tidak perlu ditulis ulang dalam
JavaScript dan tetap satu sumber dengan yang dipakai quiz.py.
"""

from __future__ import annotations

import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from frdrill import conjugaison, dataio  # noqa: E402
from frdrill.phonetique import approx, elide  # noqa: E402
from frdrill.questions import vocab_detail, vocab_display  # noqa: E402

ROOT = dataio.ROOT
OUT = os.path.join(ROOT, "webdata.js")


def build_kosakata() -> list[dict]:
    out = []
    for e in dataio.vocab_entries():
        out.append({
            "id": e["id"],
            "fr": e["fr"],
            "display": vocab_display(e),
            "ipa": e["ipa"],
            "approx": approx(e["ipa"]),
            "gloss": e["gloss"],
            "alt": e.get("alt") or [],
            "detail": vocab_detail(e),
            "pos": e["pos"],
            "posLabel": dataio.POS_LABELS.get(e["pos"], e["pos"]),
            "genre": e.get("genre") or "",
            "genreLabel": dataio.GENRE_LABELS.get(e.get("genre") or "", ""),
            "article": e.get("article") or "",
            "pluriel": e.get("pluriel") or "",
            "feminin": e.get("feminin") or "",
            "morphoNote": e.get("morpho_note") or "",
            "exFr": e["example"]["fr"],
            "exGloss": e["example"]["gloss"],
            "cat": e["cat"],
            "catLabel": dataio.CAT_LABELS.get(e["cat"], e["cat"]),
            "stage": e["stage"],
            "note": e.get("note") or "",
            "verbe": e.get("verbe") or "",
        })
    return out


def build_tatabahasa() -> list[dict]:
    """Soal tata bahasa, ditambah soal modul kata serapan — sama seperti
    pembagian mode di quiz.py."""
    out = []
    for t in dataio.grammar_topics():
        for item in t["items"]:
            out.append({
                "id": item["id"],
                "cat": t["id"],
                "catLabel": t["title"],
                "stage": t["stage"],
                "prompt": item["prompt"],
                "promptFr": item.get("prompt_fr") or "",
                "optionsLang": item["options_lang"],
                "options": item["options"],
                "answer": item["answer"],
                "explain": item.get("explain") or "",
            })
    for item in dataio.loan_items():
        out.append({
            "id": item["id"],
            "cat": "serapan",
            "catLabel": "Serapan & faux-amis",
            "stage": item["stage"],
            "prompt": item["prompt"],
            "promptFr": item.get("prompt_fr") or "",
            "optionsLang": item["options_lang"],
            "options": item["options"],
            "answer": item["answer"],
            "explain": item.get("explain") or "",
        })
    return out


def build_topik() -> list[dict]:
    return [
        {
            "id": t["id"],
            "title": t["title"],
            "stage": t["stage"],
            "explanation": t["explanation"],
            "caveats": t["caveats"],
            "examples": [{"fr": x["fr"], "gloss": x["gloss"]} for x in t["examples"]],
        }
        for t in dataio.grammar_topics()
    ]


def build_konjugasi() -> list[dict]:
    """Kartu kata kerja (bolak-balik) dan soal konjugasi (pilihan ganda)."""
    out: list[dict] = []
    label = {g["modele"]: g["nom"] for g in dataio.verb_groups()}
    for v in dataio.verbs():
        out.append({
            "id": v["id"],
            "kind": "verbe",
            "infinitif": v["infinitif"],
            "ipa": v["ipa"],
            "approx": approx(v["ipa"]),
            "gloss": v["gloss"],
            "modele": v["modele"],
            "groupe": v["groupe"],
            "formes": [
                {"pronom": p, "forme": f, "affiche": conjugaison.forme_affichee(i, f)}
                for i, (p, f) in enumerate(conjugaison.tableau(v))
            ],
            "participePasse": v["participe_passe"],
            "auxiliaire": v["auxiliaire"],
            "note": v.get("note") or "",
            "lafalNote": v.get("lafal_note") or "",
            "exFr": v["example"]["fr"],
            "exGloss": v["example"]["gloss"],
            "cat": v["modele"],
            "catLabel": label.get(v["modele"], v["modele"]),
            "stage": v["stage"],
        })
    for item in dataio.verb_items():
        out.append({
            "id": item["id"],
            "kind": "soal",
            "stage": item["stage"],
            "prompt": item["prompt"],
            "promptFr": item.get("prompt_fr") or "",
            "optionsLang": item["options_lang"],
            "options": item["options"],
            "answer": item["answer"],
            "explain": item.get("explain") or "",
            "cat": "soal",
            "catLabel": "Soal konjugasi",
        })
    return out


def build_groupes() -> list[dict]:
    return [
        {
            "id": g["id"],
            "nom": g["nom"],
            "modele": g["modele"],
            "terminaisons": g["terminaisons"],
            "explication": g["explication"],
            "note": g.get("note") or "",
            "stage": g["stage"],
        }
        for g in dataio.verb_groups()
    ]


def build_pelafalan() -> list[dict]:
    """Soal pelafalan dan teks untuk dibaca sendiri."""
    out: list[dict] = []
    for i in dataio.phon_items():
        out.append({
            "id": i["id"],
            "kind": "soal",
            "type": i["type"],
            "stage": i["stage"],
            "regle": i["regle"],
            "promptFr": i.get("prompt_fr") or "",
            "gloss": i.get("gloss") or "",
            "ipa": i["ipa"],
            "approx": approx(i["ipa"]) if i["ipa"] else "",
            "optionsLang": i["options_lang"],
            "options": i["options"],
            "optionsApprox": (
                [approx(o) for o in i["options"]] if i["options_lang"] == "ipa" else []
            ),
            "answer": i["answer"],
            "mots": i.get("mots") or [],
            # Kunci soal elisi dihitung mesin, bukan diambil dari data, sama
            # seperti di quiz.py. Dipakai sebagai sisi belakang kartu.
            "reponse": (
                elide(i["mots"][0], i["mots"][1]) if i["type"] == "elision" else ""
            ),
            "liaisonType": i.get("liaison_type") or "",
            "explain": i.get("explain") or "",
            "cat": i["type"],
            "catLabel": TYPE_LABELS[i["type"]],
        })
    for p in dataio.phon_passages():
        out.append({
            "id": p["id"],
            "kind": "teks",
            "type": "texte",
            "stage": p["stage"],
            "level": p["level"],
            "fr": p["fr"],
            "ipa": p["ipa"],
            "approx": approx(p["ipa"]),
            "gloss": p["gloss"],
            "explain": p.get("note") or "",
            "cat": "texte",
            "catLabel": TYPE_LABELS["texte"],
        })
    return out


TYPE_LABELS = {
    "lafal": "Pilih lafal",
    "homophone": "Berbunyi sama",
    "graphie": "Ejaan ke bunyi",
    "liaison": "Liaison",
    "elision": "Elisi",
    "texte": "Teks untuk dibaca",
}


def build_regles() -> list[dict]:
    return [
        {
            "id": r["id"],
            "titre": r["titre"],
            "graphies": r["graphies"],
            "ipa": r["ipa"],
            "stage": r["stage"],
            "explication": r["explication"],
            "exemples": [
                {"fr": x["fr"], "ipa": x["ipa"], "approx": approx(x["ipa"]),
                 "gloss": x["gloss"]}
                for x in r["exemples"]
            ],
            "note": r.get("note") or "",
        }
        for r in dataio.phon_rules()
    ]


def build_skema() -> list[dict]:
    """Skema ejaan bantu. Kolom ejaan bantunya dihitung dari IPA, bukan
    ditulis di data, sehingga tabel ini tidak bisa menyimpang dari mesin."""
    return [
        {
            "ipa": s["ipa"],
            "approx": approx(s["ipa"]),
            "deskripsi": s["deskripsi"],
            "contoh": s["contoh"],
        }
        for s in dataio.phon_scheme()
    ]


def build_serapan() -> list[dict]:
    return [
        {
            "id": e["id"],
            "fr": e["fr"],
            "ipa": e["ipa"],
            "approx": approx(e["ipa"]),
            "genre": e.get("genre") or "",
            "genreLabel": dataio.GENRE_LABELS.get(e.get("genre") or "", ""),
            "kind": e["kind"],
            "indonesien": e["indonesien"],
            "sensFr": e["sens_fr"],
            "ecart": e.get("ecart") or "",
            "note": e.get("note") or "",
            "cat": e["kind"],
            "catLabel": "Kata serapan" if e["kind"] == "serapan" else "Faux-ami",
            "stage": e["stage"],
        }
        for e in dataio.loan_entries()
    ]


def build_catatan() -> dict:
    return {
        "serapan": dataio.load("serapan")["catatan_penting"],
        "pelafalan": dataio.load("pelafalan")["catatan_penting"],
        "kosakata": dataio.load("kosakata")["catatan_lafal"],
    }


def main() -> int:
    data = {
        "kosakata": build_kosakata(),
        "tatabahasa": build_tatabahasa(),
        "topik": build_topik(),
        "konjugasi": build_konjugasi(),
        "groupes": build_groupes(),
        "pelafalan": build_pelafalan(),
        "regles": build_regles(),
        "skema": build_skema(),
        "serapan": build_serapan(),
        "catatan": build_catatan(),
    }
    data["meta"] = {k: len(v) for k, v in data.items() if isinstance(v, list)}

    body = json.dumps(data, ensure_ascii=True, separators=(",", ":"), sort_keys=False)
    teks = (
        "/* Dibuat otomatis oleh tools/build_web.py dari data/*.json.\n"
        "   JANGAN disunting langsung; sunting datanya lalu jalankan ulang skripnya. */\n"
        '"use strict";\n'
        "const FR_DATA = " + body + ";\n"
    )
    with open(OUT, "w", encoding="utf-8", newline="\n") as f:
        f.write(teks)
    kb = len(teks.encode("utf-8")) / 1024
    print(f"  webdata.js  ({kb:.0f} KB)")
    for k, n in data["meta"].items():
        print(f"    {k:12s} {n:4d}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
