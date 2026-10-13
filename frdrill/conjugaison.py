"""Mesin konjugasi présent de l'indicatif.

Bahasa Prancis mewajibkan bentuk kata kerja berubah mengikuti pelakunya, dan
inilah bagian yang paling asing bagi penutur Bahasa Indonesia: "saya makan",
"kami makan", dan "mereka makan" memakai satu bentuk yang sama dalam Bahasa
Indonesia, tetapi tiga bentuk berbeda dalam Bahasa Prancis.

Modul ini membentuk konjugasi BERATURAN dari infinitifnya:

    modele "er"      parler  -> parle, parles, parle, parlons, parlez, parlent
    modele "ir-iss"  finir   -> finis, finis, finit, finissons, finissez, finissent
    modele "re"      vendre  -> vends, vends, vend, vendons, vendez, vendent

Kata kerja yang tidak mengikuti ketiga model itu disimpan lengkap di
data/konjugasi.json dengan `modele` bernilai "irregulier" (être, avoir, aller,
faire, ...) atau "er-modifie" (manger, commencer, acheter, ... yang hanya
berubah ejaannya). Pengujian di tests/ membandingkan hasil mesin ini dengan
data untuk setiap kata kerja beraturan, sehingga tabel di data tidak bisa
menyimpang dari aturannya, dan setiap bentuk tak beraturan wajib punya
catatan.

Hanya présent yang dibentuk mesin. Materi tingkat A1 memerlukan passé composé
juga, tetapi bentuk itu tersusun dari auxiliaire + participe passé yang
disimpan apa adanya di data, bukan diterka dari infinitif.
"""

from __future__ import annotations

#: Enam baris konjugasi, dalam urutan baku buku pelajaran Prancis.
PRONOMS = ("je", "tu", "il", "nous", "vous", "ils")

#: Label yang ditampilkan untuk setiap baris. Satu bentuk kata kerja dipakai
#: oleh beberapa kata ganti sekaligus (il/elle/on, ils/elles).
PRONOMS_AFFICHES = (
    "je",
    "tu",
    "il / elle / on",
    "nous",
    "vous",
    "ils / elles",
)

TERMINAISONS = {
    "er": ("e", "es", "e", "ons", "ez", "ent"),
    "ir-iss": ("is", "is", "it", "issons", "issez", "issent"),
    "re": ("s", "s", "", "ons", "ez", "ent"),
}

#: Model yang bisa dibentuk mesin. Model lain wajib tersimpan lengkap di data.
MODELES_REGULIERS = tuple(TERMINAISONS)

MODELES = MODELES_REGULIERS + ("er-modifie", "irregulier")

#: Huruf awal yang memicu elisi pada je, ne, dan de.
VOYELLES_ELISION = frozenset("aeiouéèêëîïôöùûüy")


def radical(infinitif: str, modele: str) -> str:
    """Radikal (stem) sebuah infinitif beraturan: parler -> parl, finir -> fin."""
    if modele not in TERMINAISONS:
        raise ValueError(f"modele bukan model beraturan: {modele}")
    if modele == "er" and not infinitif.endswith("er"):
        raise ValueError(f"{infinitif} bukan kata kerja -er")
    if modele == "ir-iss" and not infinitif.endswith("ir"):
        raise ValueError(f"{infinitif} bukan kata kerja -ir")
    if modele == "re" and not infinitif.endswith("re"):
        raise ValueError(f"{infinitif} bukan kata kerja -re")
    return infinitif[:-2]


def conjuguer(infinitif: str, modele: str) -> list[str]:
    """Enam bentuk présent sebuah kata kerja beraturan.

    >>> conjuguer("parler", "er")[:3]
    ['parle', 'parles', 'parle']
    >>> conjuguer("finir", "ir-iss")[3]
    'finissons'
    """
    stem = radical(infinitif, modele)
    return [stem + t for t in TERMINAISONS[modele]]


def elision(mot: str, suivant: str) -> str:
    """Gabungkan je/ne/de/que dengan kata sesudahnya: je + ai -> j'ai.

    Elisi di sini ditentukan dari ejaan: vokal atau h di awal kata berikutnya.
    Semua kata kerja dalam materi ini yang berawalan h (habiter) memakai h
    muet, sehingga aturan sederhana ini cukup. Untuk kata ber-h aspiré
    (le héros) lihat phonetique.elide yang menerima penanda khusus.
    """
    first = suivant[:1].lower()
    if first in VOYELLES_ELISION or first == "h":
        return f"{mot[:-1]}'{suivant}"
    return f"{mot} {suivant}"


def forme_affichee(index: int, forme: str) -> str:
    """Satu baris konjugasi lengkap dengan kata gantinya: "j'ai", "nous avons"."""
    if index == 0:
        return elision("je", forme)
    return f"{PRONOMS_AFFICHES[index]} {forme}"


def negation(index: int, forme: str) -> str:
    """Bentuk negatif satu baris: "je ne parle pas", "je n'ai pas".

    Negasi Bahasa Prancis mengapit kata kerjanya dengan DUA kata: ne ... pas.
    "ne" mengalami elisi menjadi "n'" di depan bunyi vokal.
    """
    ne = elision("ne", forme)
    sujet = "je" if index == 0 else PRONOMS_AFFICHES[index]
    return f"{sujet} {ne} pas"


def tableau(verbe: dict) -> list[tuple[str, str]]:
    """Tabel (kata ganti, bentuk) untuk satu entri kata kerja dari data."""
    return list(zip(PRONOMS_AFFICHES, verbe["present"]))


def verifier(verbe: dict) -> list[str]:
    """Bandingkan tabel di data dengan hasil mesin untuk kata kerja beraturan.

    Kembalian kosong berarti cocok (atau memang tak beraturan dan sudah
    dicatat). Dipakai oleh pengujian, bukan saat latihan berjalan.
    """
    problems: list[str] = []
    modele = verbe["modele"]
    if modele not in MODELES:
        return [f"{verbe['id']}: modele tidak dikenal: {modele}"]
    if len(verbe["present"]) != 6:
        problems.append(f"{verbe['id']}: tabel présent tidak berisi 6 bentuk")
        return problems
    if modele in MODELES_REGULIERS:
        attendu = conjuguer(verbe["infinitif"], modele)
        if attendu != verbe["present"]:
            problems.append(
                f"{verbe['id']} ({verbe['infinitif']}): tabel berbeda dari model "
                f"{modele}. Mesin: {attendu}. Data: {verbe['present']}"
            )
    elif not (verbe.get("note") or "").strip():
        problems.append(
            f"{verbe['id']} ({verbe['infinitif']}): modele {modele} wajib memuat "
            "catatan yang menjelaskan ketidakberaturannya"
        )
    return problems


__all__ = [
    "MODELES",
    "MODELES_REGULIERS",
    "PRONOMS",
    "PRONOMS_AFFICHES",
    "TERMINAISONS",
    "VOYELLES_ELISION",
    "conjuguer",
    "elision",
    "forme_affichee",
    "negation",
    "radical",
    "tableau",
    "verifier",
]
