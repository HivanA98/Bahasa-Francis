"""Fonetik Bahasa Prancis: pemeriksa IPA dan pengubah IPA ke ejaan bantu.

Bahasa Prancis ditulis jauh berbeda dari cara membacanya, dan materi ini tidak
memuat rekaman suara. Karena itu setiap lema membawa satu field `ipa`, dan
ejaan bantu berbahasa Indonesia (`approx`) DIHITUNG dari field itu oleh modul
ini — tidak ditulis tangan. Dua akibatnya:

* Ejaan bantu tidak mungkin berbeda-beda gayanya antar entri.
* Bila IPA sebuah kata salah ditulis, ejaan bantunya ikut salah, sehingga satu
  kesalahan tidak perlu dicari di dua tempat.

Yang TIDAK dilakukan modul ini: menerka IPA dari ejaan Prancis. Arah itu
mustahil dibuat tepat tanpa kamus (lihat `fils` yang bisa /fis/ atau /fil/),
jadi IPA tetap ditulis manusia dan modul ini hanya memeriksa serta mengubahnya.

Skema ejaan bantu (lihat juga data/pelafalan.json → skema_lafal):

    ü   bunyi /y/   : bibir seperti mengucapkan "u", lidah seperti "i"
    ö   bunyi /ø œ/ : bibir seperti "o", lidah seperti "e" pada "enak"
    ë   bunyi /ə/   : e pepet, seperti "e" pada "besar"
    é   bunyi /e/   : e taling tertutup, seperti "e" pada "sate"
    è   bunyi /ɛ/   : e taling terbuka, seperti "e" pada "nenek"
    ang eng ong ung : vokal nasal /ɑ̃ ɛ̃ ɔ̃ œ̃/, "ng" hanya penanda sengau
    zh  bunyi /ʒ/   : tidak ada dalam Bahasa Indonesia
    sy  bunyi /ʃ/   : seperti "sy" pada "syukur"
    r   bunyi /ʁ/   : digetarkan di tenggorokan, bukan di ujung lidah
"""

from __future__ import annotations

import unicodedata

#: Tanda nasal U+0303 (combining tilde). Ditulis sesudah vokalnya.
NASAL = "̃"

#: Vokal nasal, masing-masing dua titik kode (vokal + U+0303).
VOYELLES_NASALES = ("ɑ" + NASAL, "ɛ" + NASAL, "ɔ" + NASAL, "œ" + NASAL)

#: Vokal lisan (oral) Bahasa Prancis baku.
VOYELLES_ORALES = ("a", "ɑ", "e", "ɛ", "i", "o", "ɔ", "u", "y", "ø", "œ", "ə")

#: Semivokal: /j/ (yod), /w/ (oui), /ɥ/ (huit).
SEMIVOYELLES = ("j", "w", "ɥ")

#: Konsonan. /ŋ/ hanya muncul pada kata serapan (parking, camping).
CONSONNES = (
    "p", "b", "t", "d", "k", "g", "f", "v", "s", "z", "ʃ", "ʒ",
    "m", "n", "ɲ", "ŋ", "l", "ʁ",
)

#: Semua fonem, diurutkan dari yang terpanjang supaya pemenggalan tidak
#: memotong vokal nasal menjadi vokal lisan + tanda.
PHONEMES = tuple(
    sorted(VOYELLES_NASALES + VOYELLES_ORALES + SEMIVOYELLES + CONSONNES,
           key=len, reverse=True)
)

VOYELLES = frozenset(VOYELLES_NASALES + VOYELLES_ORALES)
NOYAUX = VOYELLES | frozenset(SEMIVOYELLES)

#: Konsonan yang boleh merapat pada konsonan di depannya dalam satu suku kata
#: (gugus /pl/, /tʁ/, /kl/ ...). Dipakai saat memenggal suku kata.
LIQUIDES = frozenset(("l", "ʁ")) | frozenset(SEMIVOYELLES)

#: Titik kode yang sah di dalam field IPA, termasuk spasi pemisah kata.
IPA_CHARS = frozenset("".join(PHONEMES) + " ")

APPROX = {
    "ɑ" + NASAL: "ang",
    "ɛ" + NASAL: "eng",
    "ɔ" + NASAL: "ong",
    "œ" + NASAL: "ung",
    "a": "a", "ɑ": "a",
    "e": "é", "ɛ": "è",
    "i": "i",
    "o": "o", "ɔ": "o",
    "u": "u",
    "y": "ü",
    "ø": "ö", "œ": "ö",
    "ə": "ë",
    "j": "y", "w": "w", "ɥ": "ü",
    "p": "p", "b": "b", "t": "t", "d": "d", "k": "k", "g": "g",
    "f": "f", "v": "v", "s": "s", "z": "z",
    "ʃ": "sy", "ʒ": "zh",
    "m": "m", "n": "n", "ɲ": "ny", "ŋ": "ng",
    "l": "l", "ʁ": "r",
}

#: Huruf yang sah di dalam field berbahasa Prancis. Kutip satu ditulis ASCII
#: (') dan bukan U+2019, supaya jawaban yang ditaip pengguna tetap cocok.
#: Tanda baca yang diizinkan memuat tanda pisah (—) untuk dialog dan tanda
#: kutip Prancis (« »), keduanya lazim dalam teks Prancis.
LETTRES = frozenset("abcdefghijklmnopqrstuvwxyzàâäçéèêëîïôöùûüÿœæ")
PONCTUATION = frozenset(" '-.,!?:;()—«»")


def nfc(text: str) -> str:
    return unicodedata.normalize("NFC", text)


def is_nfc(text: str) -> bool:
    return nfc(text) == text


# ------------------------------------------------------------------- IPA ---

def tokenize(ipa: str) -> list[str]:
    """Penggal IPA menjadi daftar fonem; spasi tetap menjadi satu token.

    Titik kode yang tidak dikenali dikembalikan apa adanya sebagai satu token,
    sehingga pemeriksa di bawah dapat melaporkannya.
    """
    out: list[str] = []
    i = 0
    while i < len(ipa):
        for p in PHONEMES:
            if ipa.startswith(p, i):
                out.append(p)
                i += len(p)
                break
        else:
            out.append(ipa[i])
            i += 1
    return out


def validate_ipa(ipa: str, *, require_vowel: bool = True) -> list[str]:
    """Kembalikan daftar masalah pada satu field IPA; kosong berarti sah.

    `require_vowel` dimatikan untuk field yang memang berisi SATU FONEM saja,
    misalnya kolom ipa pada aturan ejaan (/ʃ/, /ɲ/) dan pada skema lafal.
    Field yang berisi kata atau frasa tetap wajib memuat vokal.
    """
    problems: list[str] = []
    if not ipa:
        return ["IPA kosong"]
    if not is_nfc(ipa):
        problems.append("IPA belum berbentuk NFC")
    if "/" in ipa or "[" in ipa:
        problems.append("IPA ditulis tanpa garis miring; tandanya ditambahkan saat ditampilkan")
    asing = sorted({ch for ch in ipa if ch not in IPA_CHARS})
    if asing:
        problems.append(f"titik kode di luar fonem Prancis: {asing}")
    if ipa != ipa.strip() or "  " in ipa:
        problems.append("spasi berlebih")
    if require_vowel:
        for mot in ipa.split(" "):
            if not mot:
                continue
            if not (set(tokenize(mot)) & NOYAUX):
                problems.append(f"bagian {mot!r} tidak memuat satu pun vokal")
    return problems


def syllabes(ipa: str) -> list[list[str]]:
    """Penggal satu kata IPA menjadi suku kata, sesederhana mungkin.

    Aturan yang dipakai: suku kata terbuka diutamakan. Satu konsonan di antara
    dua vokal menjadi awal suku kata berikutnya (/mɛʁsi/ → mɛʁ-si karena ʁs
    adalah dua konsonan; /kafe/ → ka-fe). Dua konsonan dipisah, kecuali bila
    yang kedua adalah /l ʁ j w ɥ/ sehingga keduanya tetap satu gugus
    (/tʁavaj/ → tʁa-vaj).

    Pemenggalan ini hanya untuk menyisipkan tanda hubung pada ejaan bantu,
    bukan untuk kajian fonologi.
    """
    toks = [t for t in tokenize(ipa) if t != " "]
    syls: list[list[str]] = []
    cur: list[str] = []
    i = 0
    while i < len(toks):
        t = toks[i]
        cur.append(t)
        if t in VOYELLES:
            # Kumpulkan konsonan sesudah vokal, lalu tentukan di mana
            # suku kata berikutnya dimulai.
            j = i + 1
            cons: list[str] = []
            while j < len(toks) and toks[j] not in VOYELLES:
                cons.append(toks[j])
                j += 1
            if j >= len(toks):
                # Tidak ada vokal lagi: semua konsonan menjadi penutup.
                cur.extend(cons)
                i = j
                break
            onset = 0
            if len(cons) == 1:
                onset = 1
            elif len(cons) >= 2:
                onset = 2 if cons[-1] in LIQUIDES else 1
            if onset:
                cur.extend(cons[: len(cons) - onset])
                syls.append(cur)
                cur = list(cons[len(cons) - onset:])
            else:
                cur.extend(cons)
                syls.append(cur)
                cur = []
            i = j
        else:
            i += 1
    if cur:
        syls.append(cur)
    return syls


def _join(tokens: list[str]) -> str:
    """Gabungkan ejaan bantu satu suku kata tanpa huruf kembar di sambungannya.

    /ʃ/ menjadi "sy" dan /j/ menjadi "y", sehingga /ʃjɛ̃/ (chien) akan menjadi
    "syyeng" bila disambung mentah. Huruf kembar di titik sambung dilebur:
    hasilnya "syeng".
    """
    out = ""
    for t in tokens:
        piece = APPROX.get(t, t)
        if out and piece and out[-1] == piece[0]:
            piece = piece[1:]
        out += piece
    return out


def approx(ipa: str) -> str:
    """Ubah IPA menjadi ejaan bantu berbahasa Indonesia, bersuku kata.

    >>> approx("bɔ̃ʒuʁ")
    'bong-zhur'
    >>> approx("mɛʁsi")
    'mèr-si'
    """
    mots = []
    for mot in ipa.split(" "):
        if not mot:
            continue
        mots.append("-".join(_join(s) for s in syllabes(mot)))
    return " ".join(mots)


# ---------------------------------------------------------- ejaan Prancis ---

def validate_french(text: str, *, allow_upper: bool = True) -> list[str]:
    """Periksa field berbahasa Prancis: hanya huruf Latin beraksen dan tanda baca."""
    problems: list[str] = []
    if not text:
        return ["teks kosong"]
    if not is_nfc(text):
        problems.append("teks belum berbentuk NFC")
    if "’" in text:
        problems.append("memakai kutip tipografis U+2019; pakai ' biasa")
    for ch in text:
        if ch in PONCTUATION:
            continue
        low = ch.lower()
        if low in LETTRES:
            if not allow_upper and ch != low:
                problems.append(f"huruf kapital tidak diharapkan: {ch!r}")
            continue
        if ch.isdigit():
            continue
        problems.append(f"karakter di luar ejaan Prancis: {ch!r}")
    return problems


def commence_par_voyelle(ipa: str) -> bool:
    """True bila kata diawali bunyi vokal, bukan konsonan atau semivokal.

    Dipakai untuk elisi (l', j', d') dan liaison. Semivokal tidak dihitung:
    /jaɔʁt/ (yaourt) tetap memakai "le".
    """
    toks = tokenize(ipa.strip())
    return bool(toks) and toks[0] in VOYELLES


def elide(mot_court: str, suivant: str, *, h_aspire: bool = False) -> str:
    """Gabungkan kata pendek dengan kata sesudahnya, dengan elisi bila perlu.

    >>> elide("je", "ai")
    "j'ai"
    >>> elide("le", "livre")
    'le livre'

    Elisi ditentukan dari EJAAN kata berikutnya (vokal atau h), bukan dari
    IPA-nya, supaya fungsi ini bisa dipakai pada teks biasa. Kata ber-h aspiré
    (le héros, la haine) karena itu wajib ditandai lewat `h_aspire`.
    """
    base = mot_court[:-1] if mot_court.endswith("e") else mot_court
    if mot_court == "la":
        base = "l"
    first = suivant[:1].lower()
    if h_aspire or first not in set("aeiouéèêëîïôöùûüyh"):
        return f"{mot_court} {suivant}"
    return f"{base}'{suivant}"


__all__ = [
    "APPROX",
    "CONSONNES",
    "IPA_CHARS",
    "LETTRES",
    "LIQUIDES",
    "NASAL",
    "NOYAUX",
    "PHONEMES",
    "PONCTUATION",
    "SEMIVOYELLES",
    "VOYELLES",
    "VOYELLES_NASALES",
    "VOYELLES_ORALES",
    "approx",
    "commence_par_voyelle",
    "elide",
    "is_nfc",
    "nfc",
    "syllabes",
    "tokenize",
    "validate_french",
    "validate_ipa",
]
