"""Pengujian skema data: id unik, format id, tidak ada field kosong, nilai sah."""

from __future__ import annotations

import re

import pytest

from frdrill import dataio

ID_PATTERNS = {
    "vocab": re.compile(r"^v\d{3}$"),
    "grammar_topic": re.compile(r"^g\d{2}$"),
    "grammar_item": re.compile(r"^g\d{2}-\d{2}$"),
    "verb": re.compile(r"^c\d{2}$"),
    "verb_item": re.compile(r"^k-q\d{2}$"),
    "verb_group": re.compile(r"^gr\d$"),
    "phon_rule": re.compile(r"^p\d{2}$"),
    "phon_item": re.compile(r"^f-[lhgse]\d{2}$"),
    "phon_passage": re.compile(r"^fp\d{2}$"),
    "loan_entry": re.compile(r"^s\d{2}$"),
    "loan_item": re.compile(r"^s-q\d{2}$"),
}

#: Field yang boleh bernilai null. Field lain tidak boleh null MAUPUN kosong.
NULLABLE = {
    "genre", "article", "pluriel", "feminin", "morpho_note", "note", "verbe",
    "alt", "prompt_fr", "explain", "caveats", "ecart", "lafal_note", "ipa",
    "gloss", "liaison_type", "options", "options_ipa", "mots", "variants",
}


def _check_no_empty(obj, where: str, problems: list[str]) -> None:
    """Rekursif: tolak string kosong dan nilai null pada field wajib."""
    if isinstance(obj, dict):
        for k, v in obj.items():
            if v is None and k not in NULLABLE:
                problems.append(f"{where}.{k} bernilai null")
            elif isinstance(v, str) and not v.strip() and k not in NULLABLE:
                problems.append(f"{where}.{k} berupa teks kosong")
            else:
                _check_no_empty(v, f"{where}.{k}", problems)
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            if isinstance(v, str) and not v.strip():
                problems.append(f"{where}[{i}] berupa teks kosong")
            else:
                _check_no_empty(v, f"{where}[{i}]", problems)


def test_semua_id_unik_di_seluruh_modul():
    ids = dataio.all_card_ids()
    ids += [t["id"] for t in dataio.grammar_topics()]
    ids += [g["id"] for g in dataio.verb_groups()]
    ids += [r["id"] for r in dataio.phon_rules()]
    ids += [e["id"] for e in dataio.loan_entries()]
    duplikat = sorted({i for i in ids if ids.count(i) > 1})
    assert not duplikat, f"id ganda: {duplikat}"


@pytest.mark.parametrize(
    "kind,items",
    [
        ("vocab", dataio.vocab_entries()),
        ("grammar_topic", dataio.grammar_topics()),
        ("grammar_item", dataio.grammar_items()),
        ("verb", dataio.verbs()),
        ("verb_item", dataio.verb_items()),
        ("verb_group", dataio.verb_groups()),
        ("phon_rule", dataio.phon_rules()),
        ("phon_item", dataio.phon_items()),
        ("phon_passage", dataio.phon_passages()),
        ("loan_entry", dataio.loan_entries()),
        ("loan_item", dataio.loan_items()),
    ],
)
def test_format_id(kind, items):
    pola = ID_PATTERNS[kind]
    salah = [i["id"] for i in items if not pola.match(i["id"])]
    assert not salah, f"{kind}: id tidak sesuai pola {pola.pattern}: {salah}"


def test_tidak_ada_field_kosong():
    problems: list[str] = []
    for name in dataio.MODULE_FILES:
        _check_no_empty(dataio.load(name), name, problems)
    assert not problems, "\n".join(problems)


def test_kosakata_nilai_sah():
    problems: list[str] = []
    for e in dataio.vocab_entries():
        if e["pos"] not in dataio.POS_VALUES:
            problems.append(f"{e['id']}: pos tidak dikenal: {e['pos']}")
        if e["genre"] not in dataio.GENRE_VALUES:
            problems.append(f"{e['id']}: genre tidak dikenal: {e['genre']}")
        if e["cat"] not in dataio.CAT_LABELS:
            problems.append(f"{e['id']}: cat tidak dikenal: {e['cat']}")
        if not 1 <= e["stage"] <= dataio.MAX_STAGE:
            problems.append(f"{e['id']}: stage di luar 1-{dataio.MAX_STAGE}")
        if not isinstance(e["alt"], list):
            problems.append(f"{e['id']}: alt bukan daftar")
        for field in ("fr", "ipa", "gloss", "pos", "cat"):
            if not e.get(field):
                problems.append(f"{e['id']}: {field} wajib ada")
        if not e["example"].get("fr") or not e["example"].get("gloss"):
            problems.append(f"{e['id']}: contoh kalimat tidak lengkap")
    assert not problems, "\n".join(problems)


def test_kata_benda_wajib_bergender_berartikel_dan_berjamak():
    problems = []
    for e in dataio.nouns():
        if not e["genre"]:
            problems.append(f"{e['id']}: kata benda tanpa genre")
        if not e["article"]:
            problems.append(f"{e['id']}: kata benda tanpa article")
        if not e["pluriel"]:
            problems.append(f"{e['id']}: kata benda tanpa pluriel")
    assert not problems, "\n".join(problems)


def test_kata_sifat_wajib_punya_bentuk_feminin():
    kurang = [e["id"] for e in dataio.adjectives() if not e["feminin"]]
    assert not kurang, f"kata sifat tanpa bentuk feminin: {kurang}"


def test_hanya_kata_benda_yang_punya_artikel():
    salah = [
        e["id"] for e in dataio.vocab_entries()
        if e["pos"] != "nom" and e["article"]
    ]
    assert not salah, f"artikel pada kelas kata bukan nom: {salah}"


def test_kata_kerja_menunjuk_entri_konjugasi_yang_ada():
    ids = {v["id"] for v in dataio.verbs()}
    problems = []
    for e in dataio.vocab_entries():
        if e["pos"] == "verbe" and not e["verbe"]:
            problems.append(f"{e['id']}: kata kerja tanpa rujukan ke data konjugasi")
        if e["verbe"] and e["verbe"] not in ids:
            problems.append(f"{e['id']}: verbe={e['verbe']} tidak ada di konjugasi.json")
    assert not problems, "\n".join(problems)


def test_tahap_terisi_merata():
    """Setiap tahap 1-6 harus punya materi kosakata, supaya jadwal tidak bolong."""
    per_stage = {s: 0 for s in range(1, dataio.MAX_STAGE + 1)}
    for e in dataio.vocab_entries():
        per_stage[e["stage"]] += 1
    kosong = [s for s, n in per_stage.items() if n == 0]
    assert not kosong, f"tahap tanpa kosakata: {kosong}"


def test_setiap_modul_punya_materi_di_tahap_awal():
    """Tahap 1 sampai 3 harus sudah menyentuh semua modul, supaya pemula tidak
    mengerjakan satu modul saja selama berminggu-minggu."""
    assert dataio.grammar_items(1), "tidak ada soal tata bahasa pada tahap 1"
    assert dataio.verbs(1), "tidak ada kata kerja pada tahap 1"
    assert dataio.phon_items(2), "tidak ada soal pelafalan pada tahap 1-2"
    assert dataio.loan_items(3), "tidak ada soal kata serapan pada tahap 1-3"


def test_tahap_topik_tata_bahasa_sah():
    salah = [t["id"] for t in dataio.grammar_topics()
             if not 1 <= t["stage"] <= dataio.MAX_STAGE]
    assert not salah, f"stage topik di luar jangkauan: {salah}"


def test_setiap_topik_punya_penjelasan_contoh_dan_catatan():
    problems = []
    for t in dataio.grammar_topics():
        if len(t["explanation"]) < 120:
            problems.append(f"{t['id']}: penjelasan terlalu pendek")
        if len(t["examples"]) < 3:
            problems.append(f"{t['id']}: contoh kurang dari tiga")
        if len(t["caveats"]) < 2:
            problems.append(f"{t['id']}: catatan pengecualian kurang dari dua")
        if len(t["items"]) < 5:
            problems.append(f"{t['id']}: soal kurang dari lima")
    assert not problems, "\n".join(problems)


def test_level_pelafalan_sah_dan_terisi():
    salah = [p["id"] for p in dataio.phon_passages() if p["level"] not in dataio.LEVELS]
    assert not salah, f"level di luar 1-3: {salah}"
    for level in dataio.LEVELS:
        assert dataio.phon_passages(level=level), f"tidak ada teks untuk level {level}"


def test_jenis_soal_pelafalan_dikenal():
    dikenal = {"lafal", "homophone", "graphie", "liaison", "elision"}
    salah = [i["id"] for i in dataio.phon_items() if i["type"] not in dikenal]
    assert not salah, f"jenis soal pelafalan tidak dikenal: {salah}"


def test_setiap_jenis_soal_pelafalan_ada_isinya():
    for kind in ("lafal", "homophone", "graphie", "liaison", "elision"):
        assert dataio.phon_items(kind=kind), f"tidak ada soal jenis {kind}"


def test_soal_pelafalan_menunjuk_aturan_yang_ada():
    ids = {r["id"] for r in dataio.phon_rules()}
    salah = [i["id"] for i in dataio.phon_items() if i["regle"] not in ids]
    assert not salah, f"soal menunjuk regle yang tidak ada: {salah}"


def test_serapan_nilai_sah():
    problems = []
    for e in dataio.loan_entries():
        if e["kind"] not in ("serapan", "faux-ami"):
            problems.append(f"{e['id']}: kind tidak dikenal: {e['kind']}")
        if e["kind"] == "faux-ami" and not (e.get("ecart") or "").strip():
            problems.append(f"{e['id']}: faux-ami wajib menjelaskan pergeserannya")
        if e["genre"] not in dataio.GENRE_VALUES:
            problems.append(f"{e['id']}: genre tidak dikenal")
    assert not problems, "\n".join(problems)


def test_kelompok_kata_kerja_punya_enam_akhiran():
    salah = [g["id"] for g in dataio.verb_groups() if len(g["terminaisons"]) != 6]
    assert not salah, f"kelompok dengan akhiran bukan enam: {salah}"
