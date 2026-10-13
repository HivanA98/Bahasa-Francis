"""Morfologi Bahasa Prancis: artikel, bentuk jamak, dan bentuk feminin.

Tiga hal yang paling sering salah bagi penutur Bahasa Indonesia, karena
ketiganya tidak ada padanannya dalam Bahasa Indonesia:

* **Artikel.** Setiap kata benda hampir selalu didahului artikel, dan
  bentuknya bergantung pada gender serta bunyi awal kata (le, la, l').
* **Jamak.** Ditulis tetapi umumnya tidak dibunyikan: "le livre" dan
  "les livres" hanya berbeda pada artikelnya ketika diucapkan.
* **Feminin.** Kata sifat berubah mengikuti gender kata yang disifatinya.

Ketiganya bisa diturunkan dengan aturan untuk sebagian besar kata. Fungsi di
modul ini menghasilkan bentuk BERATURAN; data tetap menyimpan bentuk
sebenarnya, dan pengujian membandingkan keduanya. Bila berbeda, data wajib
memuat catatan (`morpho_note`) yang menjelaskan kekecualiannya. Dengan begitu
setiap bentuk tak beraturan menjadi pilihan yang disengaja, bukan salah taip.
"""

from __future__ import annotations

from .phonetique import commence_par_voyelle

#: -ou yang berjamak dengan -x. Tujuh kata, selebihnya memakai -s.
OU_EN_X = ("bijou", "caillou", "chou", "genou", "hibou", "joujou", "pou")

#: -eu yang berjamak dengan -s, bukan -x.
EU_EN_S = ("pneu", "bleu")

#: -al yang berjamak dengan -s, bukan -aux.
AL_EN_S = ("bal", "carnaval", "festival", "récital", "chacal", "régal", "cal",
           "cérémonial", "choral", "narval")

#: -ail yang berjamak dengan -aux.
AIL_EN_AUX = ("travail", "vitrail", "corail", "émail", "bail", "soupirail",
              "fermail", "vantail")


def pluriel(mot: str) -> str | None:
    """Bentuk jamak beraturan sebuah kata benda atau kata sifat.

    Mengembalikan None bila kata itu lebih dari satu kata, karena jamak frasa
    (pomme de terre, grand-père) tidak bisa diterka dengan aman.
    """
    if " " in mot:
        return None
    low = mot.lower()
    if low.endswith(("s", "x", "z")):
        return mot
    if low.endswith(("eau", "au")):
        return mot + "x"
    if low.endswith("eu"):
        return mot + ("s" if low in EU_EN_S else "x")
    if low.endswith("ail"):
        return mot[:-3] + "aux" if low in AIL_EN_AUX else mot + "s"
    if low.endswith("al"):
        return mot + "s" if low in AL_EN_S else mot[:-2] + "aux"
    if low.endswith("ou"):
        return mot + ("x" if low in OU_EN_X else "s")
    return mot + "s"


def feminin(mot: str) -> str | None:
    """Bentuk feminin beraturan sebuah kata sifat.

    Aturan yang diterapkan, dari yang paling khusus:

        -e      tidak berubah      facile  -> facile
        -eux    -> -euse           heureux -> heureuse
        -f      -> -ve             neuf    -> neuve
        -er     -> -ère            cher    -> chère
        -el     -> -elle           quel    -> quelle
        -en     -> -enne           italien -> italienne
        -on     -> -onne           bon     -> bonne
        -et     -> -ette           muet    -> muette
        lainnya -> +e              grand   -> grande

    Bentuk di luar aturan ini (beau/belle, vieux/vieille, blanc/blanche,
    long/longue, complet/complète) wajib ditulis di data beserta catatannya.
    """
    if " " in mot:
        return None
    low = mot.lower()
    if low.endswith("e"):
        return mot
    if low.endswith("eux"):
        return mot[:-1] + "se"
    if low.endswith("f"):
        return mot[:-1] + "ve"
    if low.endswith("er"):
        return mot[:-2] + "ère"
    if low.endswith("el"):
        return mot + "le"
    if low.endswith("en"):
        return mot + "ne"
    if low.endswith("on"):
        return mot + "ne"
    if low.endswith("et"):
        return mot + "te"
    return mot + "e"


def article_defini(mot: str, ipa: str, genre: str | None, *, h_aspire: bool = False) -> str:
    """Artikel takrif: le, la, atau l'.

    Elisi (l') ditentukan oleh BUNYI awal kata, bukan ejaannya: "l'heure"
    karena h-nya tidak dibunyikan, tetapi "le héros" karena h-nya aspiré.
    Kata ber-h aspiré ditandai di data lewat field `h_aspire`.
    """
    if genre not in ("m", "f"):
        return ""
    if commence_par_voyelle(ipa) and not h_aspire:
        return "l'"
    return "le" if genre == "m" else "la"


def article_indefini(genre: str | None) -> str:
    """Artikel tak takrif: un atau une. Tidak pernah mengalami elisi."""
    if genre == "m":
        return "un"
    if genre == "f":
        return "une"
    return ""


def avec_article(mot: str, ipa: str, genre: str | None, *, h_aspire: bool = False) -> str:
    """Kata benda beserta artikel takrifnya: "le livre", "l'heure"."""
    art = article_defini(mot, ipa, genre, h_aspire=h_aspire)
    if not art:
        return mot
    return f"{art}{mot}" if art.endswith("'") else f"{art} {mot}"


__all__ = [
    "AIL_EN_AUX",
    "AL_EN_S",
    "EU_EN_S",
    "OU_EN_X",
    "article_defini",
    "article_indefini",
    "avec_article",
    "feminin",
    "pluriel",
]
