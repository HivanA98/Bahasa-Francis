"""Pengujian fonetik: kesahihan IPA di seluruh data, dan ejaan bantu.

Yang diuji di sini bersifat BENTUK: titik kode yang dipakai, bentuk NFC, dan
cara IPA diubah menjadi ejaan bantu. Kebenaran ISI — apakah /pəti/ memang
lafal petit — tidak bisa diuji mesin dan perlu diperiksa dengan kamus.
"""

from __future__ import annotations

import pytest

from frdrill import dataio
from frdrill.phonetique import (
    APPROX,
    LETTRES,
    NOYAUX,
    PHONEMES,
    approx,
    commence_par_voyelle,
    elide,
    is_nfc,
    syllabes,
    tokenize,
    validate_french,
    validate_ipa,
)


def _ipa_fields():
    """(label, ipa, apakah boleh berupa satu fonem tunggal)."""
    for e in dataio.vocab_entries():
        yield f"kosakata {e['id']}", e["ipa"], False
    for v in dataio.verbs():
        yield f"konjugasi {v['id']}", v["ipa"], False
    for r in dataio.phon_rules():
        if r["ipa"]:
            yield f"regle {r['id']}", r["ipa"], True
        for x in r["exemples"]:
            yield f"regle {r['id']} contoh {x['fr']}", x["ipa"], False
    for i in dataio.phon_items():
        if i["ipa"]:
            yield f"pelafalan {i['id']}", i["ipa"], i["type"] == "graphie"
        for o in i["options_ipa"]:
            yield f"pelafalan {i['id']} options_ipa", o, False
        if i["options_lang"] == "ipa":
            for o in i["options"]:
                yield f"pelafalan {i['id']} pilihan", o, False
    for p in dataio.phon_passages():
        yield f"teks {p['id']}", p["ipa"], False
    for e in dataio.loan_entries():
        yield f"serapan {e['id']}", e["ipa"], False
    for s in dataio.phon_scheme():
        yield f"skema {s['ipa']}", s["ipa"], True


def _french_fields():
    for e in dataio.vocab_entries():
        yield f"kosakata {e['id']}.fr", e["fr"]
        yield f"kosakata {e['id']}.example", e["example"]["fr"]
        for field in ("pluriel", "feminin", "article"):
            if e.get(field):
                yield f"kosakata {e['id']}.{field}", e[field]
    for v in dataio.verbs():
        yield f"konjugasi {v['id']}.infinitif", v["infinitif"]
        yield f"konjugasi {v['id']}.pp", v["participe_passe"]
        yield f"konjugasi {v['id']}.example", v["example"]["fr"]
        for f in v["present"]:
            yield f"konjugasi {v['id']} bentuk", f
    for t in dataio.grammar_topics():
        for x in t["examples"]:
            yield f"tatabahasa {t['id']}.example", x["fr"]
    for p in dataio.phon_passages():
        yield f"teks {p['id']}.fr", p["fr"]
    for e in dataio.loan_entries():
        yield f"serapan {e['id']}.fr", e["fr"]
    for group in (dataio.grammar_items(), dataio.verb_items(), dataio.loan_items()):
        for item in group:
            if item.get("prompt_fr"):
                yield f"{item['id']}.prompt_fr", item["prompt_fr"]
            if item["options_lang"] == "fr":
                for o in item["options"]:
                    yield f"{item['id']} pilihan", o


def test_ipa_hanya_memakai_fonem_prancis():
    problems = []
    for label, ipa, phoneme_ok in _ipa_fields():
        for p in validate_ipa(ipa, require_vowel=not phoneme_ok):
            problems.append(f"{label}: {p}")
    assert not problems, "\n".join(problems)


def test_teks_prancis_hanya_memakai_huruf_prancis():
    problems = []
    for label, text in _french_fields():
        # Sebagian prompt memuat tempat kosong "___" yang harus diisi; garis
        # bawahnya bukan bagian dari ejaan Prancis, jadi dilepas dahulu.
        for p in validate_french(text.replace("_", "")):
            problems.append(f"{label}: {p}")
    assert not problems, "\n".join(problems)


def test_semua_teks_berbentuk_nfc():
    salah = [label for label, text in _french_fields() if not is_nfc(text)]
    salah += [label for label, ipa, _ in _ipa_fields() if not is_nfc(ipa)]
    assert not salah, f"teks belum NFC: {salah}"


def test_tidak_memakai_kutip_tipografis():
    """Jawaban yang ditaip memakai kutip ASCII, sehingga data pun harus begitu."""
    salah = [label for label, text in _french_fields() if "’" in text]
    assert not salah, f"memakai U+2019, bukan ': {salah}"


def test_setiap_fonem_yang_dipakai_ada_di_skema_lafal():
    """Skema ejaan bantu harus menjelaskan setiap bunyi yang muncul di materi.

    Tanpa pengujian ini, sebuah fonem bisa masuk ke data tanpa pernah
    dijelaskan kepada pembelajar.
    """
    dipakai: set[str] = set()
    for _label, ipa, _ in _ipa_fields():
        dipakai |= {t for t in tokenize(ipa) if t != " "}
    dijelaskan = {s["ipa"] for s in dataio.phon_scheme()}
    kurang = sorted(dipakai - dijelaskan)
    assert not kurang, f"fonem dipakai tetapi tidak dijelaskan di skema_lafal: {kurang}"


def test_skema_lafal_tidak_memuat_fonem_asing():
    salah = [s["ipa"] for s in dataio.phon_scheme() if s["ipa"] not in PHONEMES]
    assert not salah, f"skema memuat lambang di luar daftar fonem: {salah}"


def test_setiap_bunyi_di_skema_punya_ejaan_bantu():
    kurang = [s["ipa"] for s in dataio.phon_scheme() if s["ipa"] not in APPROX]
    assert not kurang, f"fonem tanpa padanan ejaan bantu: {kurang}"


# ------------------------------------------------- pengujian fungsi bantu ---

@pytest.mark.parametrize(
    "ipa,hasil",
    [
        ("bɔ̃ʒuʁ", "bong-zhur"),
        ("mɛʁsi", "mèr-si"),
        ("tʁavaj", "tra-vay"),
        ("ekɔl", "é-kol"),
        ("livʁ", "livr"),
        ("ty", "tü"),
        ("dø", "dö"),
        ("ʒə", "zhë"),
        ("ɥit", "üit"),
        ("ʃjɛ̃", "syeng"),
        ("sil vu plɛ", "sil vu plè"),
        ("ynivɛʁsite", "ü-ni-vèr-si-té"),
    ],
)
def test_ejaan_bantu_kasus_patokan(ipa, hasil):
    assert approx(ipa) == hasil


def test_ejaan_bantu_tidak_menyisakan_lambang_ipa():
    """Setiap lambang IPA harus punya padanan; kalau tidak, ia bocor apa adanya."""
    asing = set()
    for _label, ipa, _ in _ipa_fields():
        for ch in approx(ipa):
            if ch not in LETTRES and ch not in " -":
                asing.add(ch)
    assert not asing, f"lambang tidak diterjemahkan ke ejaan bantu: {sorted(asing)}"


def test_setiap_suku_kata_memuat_vokal():
    """Pemenggalan suku kata tidak boleh menghasilkan suku tanpa vokal, kecuali
    gugus konsonan penutup yang memang menempel pada suku sebelumnya."""
    problems = []
    for _label, ipa, phoneme_ok in _ipa_fields():
        if phoneme_ok:
            continue
        for mot in ipa.split(" "):
            syls = syllabes(mot)
            for s in syls:
                if not (set(s) & NOYAUX):
                    problems.append(f"{mot}: suku {''.join(s)} tanpa vokal")
    assert not problems, "\n".join(problems)


def test_pemenggalan_mempertahankan_semua_fonem():
    for _label, ipa, _ in _ipa_fields():
        for mot in ipa.split(" "):
            utuh = [t for t in tokenize(mot) if t != " "]
            dipenggal = [t for s in syllabes(mot) for t in s]
            assert utuh == dipenggal, f"{mot}: fonem hilang saat dipenggal"


def test_tokenize_tidak_memecah_vokal_sengau():
    assert tokenize("ɑ̃fɑ̃") == ["ɑ̃", "f", "ɑ̃"]
    assert tokenize("bɔ̃ʒuʁ") == ["b", "ɔ̃", "ʒ", "u", "ʁ"]


def test_validator_menolak_ipa_bergaris_miring():
    assert validate_ipa("/bɔ̃ʒuʁ/")


def test_validator_menolak_huruf_latin_di_ipa():
    assert validate_ipa("bonjour")


def test_validator_menerima_frasa_berspasi():
    assert not validate_ipa("le zami")


def test_commence_par_voyelle():
    assert commence_par_voyelle("ekɔl")
    assert commence_par_voyelle("o")
    assert not commence_par_voyelle("livʁ")
    # Semivokal tidak memicu elisi: le yaourt, bukan l'yaourt.
    assert not commence_par_voyelle("jauʁt")


@pytest.mark.parametrize(
    "a,b,hasil",
    [
        ("je", "ai", "j'ai"),
        ("je", "habite", "j'habite"),
        ("je", "parle", "je parle"),
        ("le", "hôtel", "l'hôtel"),
        ("la", "école", "l'école"),
        ("la", "table", "la table"),
        ("ne", "est", "n'est"),
        ("de", "eau", "d'eau"),
    ],
)
def test_elide_kasus_patokan(a, b, hasil):
    assert elide(a, b) == hasil


def test_elide_menghormati_h_aspire():
    assert elide("le", "héros", h_aspire=True) == "le héros"
    assert elide("le", "héros") == "l'héros"  # tanpa penanda, aturan ejaan saja
