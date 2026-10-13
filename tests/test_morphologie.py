"""Pengujian morfologi: artikel, jamak, dan feminin pada data vs mesin.

Inilah pengaman utama data kosakata. Setiap kata benda menyimpan artikel dan
bentuk jamaknya, dan setiap kata sifat menyimpan bentuk femininnya. Pengujian
membandingkannya dengan aturan di frdrill/morphologie.py:

* bila cocok, keduanya saling meneguhkan;
* bila berbeda, data WAJIB memuat morpho_note yang menjelaskan kekecualiannya.

Dengan begitu tidak ada bentuk tak beraturan yang masuk diam-diam karena
salah taip.
"""

from __future__ import annotations

import pytest

from frdrill import dataio
from frdrill.morphologie import (
    article_defini,
    article_indefini,
    avec_article,
    feminin,
    pluriel,
)


def test_artikel_takrif_sesuai_aturan():
    problems = []
    for e in dataio.nouns():
        genre = "m" if e["genre"] == "m/f" else e["genre"]
        mesin = article_defini(e["fr"], e["ipa"], genre, h_aspire=e.get("h_aspire", False))
        if mesin != e["article"]:
            problems.append(
                f"{e['id']} ({e['fr']}): data {e['article']!r}, mesin {mesin!r}"
            )
    assert not problems, "\n".join(problems)


def test_artikel_l_apostrof_hanya_untuk_kata_bervokal():
    problems = []
    for e in dataio.nouns():
        bervokal = article_defini(e["fr"], e["ipa"], "m") == "l'"
        if (e["article"] == "l'") != bervokal:
            problems.append(f"{e['id']} ({e['fr']}): artikel {e['article']} vs lafal /{e['ipa']}/")
    assert not problems, "\n".join(problems)


def test_bentuk_jamak_sesuai_aturan_atau_dicatat():
    problems = []
    for e in dataio.nouns():
        mesin = pluriel(e["fr"])
        if mesin != e["pluriel"] and not (e.get("morpho_note") or "").strip():
            problems.append(
                f"{e['id']} ({e['fr']}): jamak {e['pluriel']!r} berbeda dari aturan "
                f"({mesin!r}) tetapi tidak ada morpho_note"
            )
    assert not problems, "\n".join(problems)


def test_bentuk_feminin_sesuai_aturan_atau_dicatat():
    problems = []
    for e in dataio.adjectives():
        mesin = feminin(e["fr"])
        if mesin != e["feminin"] and not (e.get("morpho_note") or "").strip():
            problems.append(
                f"{e['id']} ({e['fr']}): feminin {e['feminin']!r} berbeda dari aturan "
                f"({mesin!r}) tetapi tidak ada morpho_note"
            )
    assert not problems, "\n".join(problems)


def test_catatan_morfologi_hanya_pada_bentuk_yang_memang_menyimpang():
    """Catatan yang tidak perlu membuat pembaca mengira ada kekecualian."""
    problems = []
    for e in dataio.vocab_entries():
        catatan = (e.get("morpho_note") or "").strip()
        if not catatan:
            continue
        menyimpang = False
        if e["pos"] == "nom" and pluriel(e["fr"]) != e["pluriel"]:
            menyimpang = True
        if e["pos"] == "adjectif" and feminin(e["fr"]) != e["feminin"]:
            menyimpang = True
        # Kata yang bentuknya kebetulan sama dengan aturan tetapi memang perlu
        # dijelaskan (fils, riz, bus, mois, après-midi, grand-père) tetap
        # diizinkan selama catatannya menyebut alasannya.
        if not menyimpang and len(catatan) < 30:
            problems.append(f"{e['id']}: morpho_note tanpa penyimpangan dan tanpa alasan")
    assert not problems, "\n".join(problems)


@pytest.mark.parametrize(
    "mot,hasil",
    [
        ("livre", "livres"),
        ("bureau", "bureaux"),
        ("hôpital", "hôpitaux"),
        ("bus", "bus"),
        ("mois", "mois"),
        ("riz", "riz"),
        ("eau", "eaux"),
        ("bal", "bals"),
        ("festival", "festivals"),
        ("bijou", "bijoux"),
        ("trou", "trous"),
        ("pneu", "pneus"),
        ("jeu", "jeux"),
        ("travail", "travaux"),
        ("détail", "détails"),
    ],
)
def test_jamak_kasus_patokan(mot, hasil):
    assert pluriel(mot) == hasil


def test_jamak_frasa_tidak_diterka():
    assert pluriel("pomme de terre") is None


@pytest.mark.parametrize(
    "mot,hasil",
    [
        ("grand", "grande"),
        ("petit", "petite"),
        ("vert", "verte"),
        ("rouge", "rouge"),
        ("heureux", "heureuse"),
        ("neuf", "neuve"),
        ("cher", "chère"),
        ("quel", "quelle"),
        ("italien", "italienne"),
        ("bon", "bonne"),
        ("muet", "muette"),
    ],
)
def test_feminin_kasus_patokan(mot, hasil):
    assert feminin(mot) == hasil


@pytest.mark.parametrize(
    "mot,ipa,genre,hasil",
    [
        ("livre", "livʁ", "m", "le"),
        ("table", "tabl", "f", "la"),
        ("école", "ekɔl", "f", "l'"),
        ("hôtel", "otɛl", "m", "l'"),
        ("œuf", "œf", "m", "l'"),
    ],
)
def test_artikel_kasus_patokan(mot, ipa, genre, hasil):
    assert article_defini(mot, ipa, genre) == hasil


def test_artikel_tak_takrif():
    assert article_indefini("m") == "un"
    assert article_indefini("f") == "une"
    assert article_indefini(None) == ""


def test_avec_article_menyambung_tanpa_spasi_sesudah_apostrof():
    assert avec_article("école", "ekɔl", "f") == "l'école"
    assert avec_article("livre", "livʁ", "m") == "le livre"


def test_h_aspire_menghalangi_elisi():
    # héros: diawali bunyi vokal, tetapi h aspiré menahan elisi.
    assert article_defini("héros", "eʁo", "m") == "l'"
    assert article_defini("héros", "eʁo", "m", h_aspire=True) == "le"
