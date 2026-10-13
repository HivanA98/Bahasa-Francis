"""Pengujian konjugasi: tabel di data vs mesin pembentuk.

Setiap kata kerja bermodel beraturan (er, ir-iss, re) dibandingkan dengan
hasil frdrill/conjugaison.py. Kata kerja tak beraturan tidak bisa dibandingkan
begitu, sehingga yang diuji adalah kewajiban mencantumkan catatan yang
menjelaskan ketidakberaturannya.
"""

from __future__ import annotations

import pytest

from frdrill import dataio
from frdrill.conjugaison import (
    MODELES,
    MODELES_REGULIERS,
    PRONOMS,
    PRONOMS_AFFICHES,
    TERMINAISONS,
    conjuguer,
    elision,
    forme_affichee,
    negation,
    radical,
    tableau,
    verifier,
)


def test_tabel_beraturan_sama_dengan_hasil_mesin():
    problems = []
    for v in dataio.verbs():
        problems += verifier(v)
    assert not problems, "\n".join(problems)


def test_setiap_kata_kerja_punya_enam_bentuk():
    salah = [v["id"] for v in dataio.verbs() if len(v["present"]) != 6]
    assert not salah, f"tabel bukan enam baris: {salah}"


def test_modele_dikenal():
    salah = [v["id"] for v in dataio.verbs() if v["modele"] not in MODELES]
    assert not salah, f"modele tidak dikenal: {salah}"


def test_kata_kerja_tak_beraturan_wajib_bercatatan():
    kurang = [
        v["id"] for v in dataio.verbs()
        if v["modele"] not in MODELES_REGULIERS and not (v.get("note") or "").strip()
    ]
    assert not kurang, f"tak beraturan tanpa catatan: {kurang}"


def test_kata_kerja_beraturan_tidak_perlu_catatan_ketidakberaturan():
    """Catatan pada kata kerja beraturan membuat pembelajar mengira ada
    kekecualian padahal tidak ada."""
    salah = [
        v["id"] for v in dataio.verbs()
        if v["modele"] in MODELES_REGULIERS and (v.get("note") or "").strip()
    ]
    assert not salah, f"kata kerja beraturan dengan catatan ketidakberaturan: {salah}"


def test_auxiliaire_sah():
    salah = [v["id"] for v in dataio.verbs() if v["auxiliaire"] not in ("avoir", "être")]
    assert not salah, f"auxiliaire tidak dikenal: {salah}"


def test_kelompok_sah_dan_sejalan_dengan_modele():
    problems = []
    for v in dataio.verbs():
        if v["groupe"] not in (1, 2, 3):
            problems.append(f"{v['id']}: groupe {v['groupe']}")
        if v["modele"] == "ir-iss" and v["groupe"] != 2:
            problems.append(f"{v['id']}: model ir-iss seharusnya kelompok 2")
        if v["modele"] == "er" and v["groupe"] != 1:
            problems.append(f"{v['id']}: model er seharusnya kelompok 1")
    assert not problems, "\n".join(problems)


def test_infinitif_sesuai_modelnya():
    problems = []
    for v in dataio.verbs():
        inf = v["infinitif"]
        if v["modele"] == "er" and not inf.endswith("er"):
            problems.append(f"{v['id']}: model er tetapi infinitif {inf}")
        if v["modele"] == "ir-iss" and not inf.endswith("ir"):
            problems.append(f"{v['id']}: model ir-iss tetapi infinitif {inf}")
        if v["modele"] == "re" and not inf.endswith("re"):
            problems.append(f"{v['id']}: model re tetapi infinitif {inf}")
    assert not problems, "\n".join(problems)


def test_tiga_kelompok_terwakili():
    kelompok = {v["groupe"] for v in dataio.verbs()}
    assert kelompok == {1, 2, 3}, f"kelompok yang ada: {kelompok}"


def test_kata_kerja_paling_dasar_ada_di_tahap_awal():
    """être dan avoir diperlukan sebelum kalimat apa pun bisa disusun."""
    awal = {v["infinitif"] for v in dataio.verbs(1)}
    assert {"être", "avoir"} <= awal, f"tahap 1 memuat: {awal}"


# ------------------------------------------------- pengujian fungsi mesin ---

def test_conjuguer_er():
    assert conjuguer("parler", "er") == [
        "parle", "parles", "parle", "parlons", "parlez", "parlent"
    ]


def test_conjuguer_ir_iss():
    assert conjuguer("finir", "ir-iss") == [
        "finis", "finis", "finit", "finissons", "finissez", "finissent"
    ]


def test_conjuguer_re():
    assert conjuguer("vendre", "re") == [
        "vends", "vends", "vend", "vendons", "vendez", "vendent"
    ]


def test_radical_menolak_infinitif_yang_tidak_cocok():
    with pytest.raises(ValueError):
        radical("finir", "er")
    with pytest.raises(ValueError):
        conjuguer("être", "irregulier")


def test_jumlah_pronom_enam():
    assert len(PRONOMS) == 6
    assert len(PRONOMS_AFFICHES) == 6
    assert all(len(t) == 6 for t in TERMINAISONS.values())


def test_forme_affichee_memakai_elisi_untuk_je():
    assert forme_affichee(0, "ai") == "j'ai"
    assert forme_affichee(0, "parle") == "je parle"
    assert forme_affichee(3, "parlons") == "nous parlons"


def test_negation_mengapit_kata_kerja():
    assert negation(0, "parle") == "je ne parle pas"
    assert negation(0, "ai") == "je n'ai pas"
    assert negation(5, "parlent") == "ils / elles ne parlent pas"


def test_elision_hanya_di_depan_vokal_dan_h():
    assert elision("je", "ai") == "j'ai"
    assert elision("je", "habite") == "j'habite"
    assert elision("ne", "parle") == "ne parle"


def test_tableau_memasangkan_pronom_dan_bentuk():
    etre = dataio.verb_by_id("c01")
    pasangan = tableau(etre)
    assert pasangan[0] == ("je", "suis")
    assert pasangan[4] == ("vous", "êtes")


def test_verb_by_id_mengembalikan_none_untuk_id_asing():
    assert dataio.verb_by_id("c99") is None
