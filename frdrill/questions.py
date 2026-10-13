"""Pembuat soal untuk setiap mode latihan.

Soal yang dibuat otomatis — kosakata dua arah, artikel dan gender, konjugasi,
dan elisi — selalu mengambil kunci jawaban LANGSUNG dari data atau dari mesin
di frdrill/, bukan dari daftar jawaban terpisah. Dengan begitu kunci tidak
mungkin menyimpang dari sumbernya. Pengecoh dipilih dengan generator acak
ber-seed agar hasilnya bisa diulang dan diuji.

Enam mode:

    kosakata-fr   Prancis ke Indonesia, jawaban ditulis sendiri
    kosakata-id   Indonesia ke Prancis, pilihan ganda
    genre         artikel takrif: le, la, atau l' (dibuat otomatis)
    tatabahasa    soal tata bahasa dan catatan kata serapan
    konjugasi     tabel konjugasi: ditulis sendiri dan pilihan ganda
    pelafalan     lafal, kata berbunyi sama, liaison, elisi, dan membaca
"""

from __future__ import annotations

import random
import re
import unicodedata
from dataclasses import dataclass, field

from . import conjugaison, dataio, morphologie
from .phonetique import approx, elide

MODES = (
    "kosakata-fr",
    "kosakata-id",
    "genre",
    "tatabahasa",
    "konjugasi",
    "pelafalan",
)

MODE_LABELS = {
    "kosakata-fr": "Kosakata: Prancis ke Indonesia",
    "kosakata-id": "Kosakata: Indonesia ke Prancis",
    "genre": "Gender dan artikel",
    "tatabahasa": "Tata bahasa",
    "konjugasi": "Konjugasi",
    "pelafalan": "Pelafalan",
}

_ACCEPTED_CACHE: dict[tuple, frozenset[str]] = {}


@dataclass
class Question:
    card_id: str
    mode: str
    kind: str  # "mcq" | "typed" | "selfcheck"
    question: str
    stimulus_fr: str | None = None
    stimulus_ipa: str | None = None
    stimulus_label: str | None = None
    options: list[str] | None = None
    options_lang: str | None = None  # "fr" | "id" | "ipa"
    answer: int | None = None
    accepted: list[str] = field(default_factory=list)
    accepted_lang: str = "id"
    reveal: str = ""
    reveal_fr: str | None = None
    reveal_ipa: str | None = None
    explain: str | None = None
    #: True bila soal ini pengulangan materi baru di lintasan kedua sesi yang
    #: sama. quiz.py tidak menaikkan kotak Leitner dua kali.
    repeat: bool = False
    #: Tahap materi (1-6). Dipakai session.py untuk memperkenalkan kartu baru
    #: menurut urutan tahap, bukan secara acak dari seluruh materi.
    stage: int | None = None

    def is_correct_text(self, text: str) -> bool:
        norm = normalize_fr if self.accepted_lang == "fr" else normalize_id
        return norm(text) in {norm(a) for a in self.accepted}


# ------------------------------------------------------- jawaban bertaip ---

_PUNCT_RE = re.compile(r"[^\w\s]", flags=re.UNICODE)
_SPACE_RE = re.compile(r"\s+")


def normalize_id(text: str) -> str:
    """Bakukan jawaban Bahasa Indonesia: huruf kecil, tanpa tanda baca."""
    text = unicodedata.normalize("NFKC", text).strip().lower()
    text = _PUNCT_RE.sub(" ", text)
    return _SPACE_RE.sub(" ", text).strip()


def normalize_fr(text: str) -> str:
    """Bakukan jawaban Bahasa Prancis.

    Aksen, tanda kutip, tanda hubung, dan spasi diabaikan, sehingga "j'ai",
    "jai", dan "J AI" sama-sama diterima. Alasannya: menaip aksen di papan
    ketik Indonesia sukar, dan yang dilatih di sini adalah bentuk katanya,
    bukan kemampuan mengetik aksen. Aksen tetap ditampilkan pada jawabannya
    supaya tetap terlihat benar.
    """
    text = unicodedata.normalize("NFD", text).strip().lower()
    text = "".join(ch for ch in text if not unicodedata.combining(ch))
    return re.sub(r"[^a-z0-9]", "", text)


def expand_accepted(gloss: str, alt: list[str] | None = None) -> list[str]:
    """Kembangkan arti menjadi daftar jawaban yang diterima.

    "besar, tinggi (orang)" menghasilkan: kalimat utuhnya, "besar",
    "tinggi (orang)", dan "tinggi". Tujuannya supaya pengguna tidak dihukum
    karena menulis salah satu arti saja.
    """
    out: list[str] = []

    def add(s: str) -> None:
        s = s.strip()
        if s and s not in out:
            out.append(s)

    add(gloss)
    for piece in re.split(r"[,;/]", gloss):
        add(piece)
        add(re.sub(r"\([^)]*\)", "", piece))
    for a in alt or []:
        add(a)
        add(re.sub(r"\([^)]*\)", "", a))
    return [o for o in out if o]


def accepted_set(entry: dict) -> frozenset[str]:
    """Himpunan jawaban yang diterima untuk satu entri, sudah dibakukan."""
    key = (entry["gloss"], tuple(entry.get("alt") or ()))
    cached = _ACCEPTED_CACHE.get(key)
    if cached is None:
        cached = frozenset(
            normalize_id(a) for a in expand_accepted(entry["gloss"], entry.get("alt"))
        )
        _ACCEPTED_CACHE[key] = cached
    return cached


# ------------------------------------------------------------- pengecoh ---

def _pick_distractors(
    rng: random.Random, pool: list[dict], target: dict, key: str, n: int = 3
) -> list[str]:
    """Pilih n pengecoh, mengutamakan kata dengan kelas kata yang sama."""
    want = target[key]
    same_pos = [e for e in pool if e[key] != want and e.get("pos") == target.get("pos")]
    same_cat = [e for e in pool if e[key] != want and e.get("cat") == target.get("cat")]
    others = [e for e in pool if e[key] != want]
    chosen: list[str] = []
    for bucket in (same_pos, same_cat, others):
        rng.shuffle(bucket)
        for e in bucket:
            if e[key] not in chosen and len(chosen) < n:
                chosen.append(e[key])
        if len(chosen) >= n:
            break
    return chosen[:n]


def _shuffle_options(
    rng: random.Random, correct: str, distractors: list[str]
) -> tuple[list[str], int]:
    opts = [correct] + [d for d in distractors if d != correct]
    rng.shuffle(opts)
    return opts, opts.index(correct)


# ------------------------------------------------------------- kosakata ---

def vocab_detail(e: dict) -> str:
    """Keterangan singkat satu entri: kelas kata, gender, jamak, feminin."""
    bits = [dataio.POS_LABELS.get(e["pos"], e["pos"])]
    if e.get("genre"):
        bits.append(dataio.GENRE_LABELS[e["genre"]])
    if e["pos"] == "nom" and e.get("pluriel"):
        bits.append(f"jamak: {e['pluriel']}")
    if e.get("feminin"):
        bits.append(f"feminin: {e['feminin']}")
    return " · ".join(bits)


def vocab_display(e: dict) -> str:
    """Bentuk tampilan sebuah lema: kata benda selalu dengan artikelnya."""
    if e["pos"] == "nom" and e.get("article"):
        art = e["article"]
        return f"{art}{e['fr']}" if art.endswith("'") else f"{art} {e['fr']}"
    return e["fr"]


def vocab_fr_to_id(e: dict) -> Question:
    return Question(
        card_id=e["id"],
        mode="kosakata-fr",
        kind="typed",
        stage=e["stage"],
        question="Apa arti kata ini?",
        stimulus_fr=vocab_display(e),
        stimulus_ipa=e["ipa"],
        accepted=expand_accepted(e["gloss"], e.get("alt")),
        accepted_lang="id",
        reveal=f"{e['gloss']}  ({vocab_detail(e)})",
        reveal_fr=e["example"]["fr"],
        explain=f"{e['example']['fr']} = {e['example']['gloss']}",
    )


def vocab_id_to_fr(e: dict, pool: list[dict], rng: random.Random) -> Question:
    """Indonesia ke Prancis, pilihan ganda.

    Pengecoh tidak boleh menerima teks pertanyaan sebagai jawabannya sendiri.
    Tanpa saringan ini, pertanyaan "kata Prancis untuk 'malam'" bisa memuat
    soir dan nuit sekaligus, sehingga ada dua jawaban benar.
    """
    prompt_key = normalize_id(e["gloss"])
    safe = [
        o for o in pool
        if o["id"] != e["id"] and prompt_key not in accepted_set(o)
    ]
    distractors = _pick_distractors(rng, safe, e, "fr", 3)
    options, answer = _shuffle_options(rng, e["fr"], distractors)
    return Question(
        card_id=e["id"],
        mode="kosakata-id",
        kind="mcq",
        stage=e["stage"],
        question=f"Mana kata Prancis untuk ‘{e['gloss']}’?",
        options=options,
        options_lang="fr",
        answer=answer,
        reveal=f"{vocab_display(e)} = {e['gloss']}  ({vocab_detail(e)})",
        reveal_fr=e["example"]["fr"],
        reveal_ipa=e["ipa"],
        explain=f"{e['example']['fr']} = {e['example']['gloss']}",
    )


# --------------------------------------------------------- gender/artikel ---

def genre_question(e: dict, rng: random.Random) -> Question:
    """Soal buatan: artikel takrif mana yang tepat untuk kata benda ini.

    Kuncinya diambil dari field `article` pada data, yang pada gilirannya
    diperiksa pengujian terhadap aturan di morphologie.article_defini. Jadi
    kunci soal ini terikat pada dua sumber sekaligus.
    """
    correct = f"{e['article']}{e['fr']}" if e["article"].endswith("'") \
        else f"{e['article']} {e['fr']}"
    bentuk = [f"le {e['fr']}", f"la {e['fr']}", f"l'{e['fr']}"]
    options = [b for b in bentuk if b != correct]
    rng.shuffle(options)
    options = [correct] + options[:2]
    rng.shuffle(options)
    genre_txt = dataio.GENRE_LABELS[e["genre"]]
    return Question(
        card_id=e["id"],
        mode="genre",
        kind="mcq",
        stage=e["stage"],
        question="Mana bentuk dengan artikel takrif yang tepat?",
        stimulus_fr=e["fr"],
        stimulus_ipa=e["ipa"],
        stimulus_label=f"arti: {e['gloss']}",
        options=options,
        options_lang="fr",
        answer=options.index(correct),
        reveal=f"{correct} ({genre_txt}, jamak: {e['pluriel']})",
        explain=(
            f"{e['fr']} bergender {genre_txt}. "
            + ("Diawali bunyi vokal, sehingga artikelnya menjadi l'."
               if e["article"].endswith("'")
               else f"Artikelnya {e['article']}.")
        ),
    )


# ------------------------------------------------------------ tata bahasa ---

def grammar_question(item: dict) -> Question:
    return Question(
        card_id=item["id"],
        mode="tatabahasa",
        kind="mcq",
        stage=item["stage"],
        question=item["prompt"],
        stimulus_fr=item.get("prompt_fr"),
        options=list(item["options"]),
        options_lang=item["options_lang"],
        answer=item["answer"],
        reveal=item["options"][item["answer"]],
        explain=item.get("explain"),
    )


def loan_question(item: dict) -> Question:
    """Soal modul kata serapan. Dikerjakan bersama mode tata bahasa."""
    return Question(
        card_id=item["id"],
        mode="tatabahasa",
        kind="mcq",
        stage=item["stage"],
        question=item["prompt"],
        stimulus_fr=item.get("prompt_fr"),
        options=list(item["options"]),
        options_lang=item["options_lang"],
        answer=item["answer"],
        reveal=item["options"][item["answer"]],
        explain=item.get("explain"),
    )


# -------------------------------------------------------------- konjugasi ---

def verb_item_question(item: dict) -> Question:
    return Question(
        card_id=item["id"],
        mode="konjugasi",
        kind="mcq",
        stage=item["stage"],
        question=item["prompt"],
        stimulus_fr=item.get("prompt_fr"),
        options=list(item["options"]),
        options_lang=item["options_lang"],
        answer=item["answer"],
        reveal=item["options"][item["answer"]],
        explain=item.get("explain"),
    )


def _tableau_txt(verbe: dict) -> str:
    return " · ".join(
        conjugaison.forme_affichee(i, f) for i, f in enumerate(verbe["present"])
    )


def conjugation_typed(verbe: dict, index: int) -> Question:
    """Soal buatan: tulis bentuk présent untuk satu kata ganti.

    Kunci diambil dari tabel present di data. Jawaban diterima baik ditulis
    sendiri ("parlons") maupun bersama kata gantinya ("nous parlons").
    """
    forme = verbe["present"][index]
    pronom = conjugaison.PRONOMS_AFFICHES[index]
    return Question(
        card_id=verbe["id"],
        mode="konjugasi",
        kind="typed",
        stage=verbe["stage"],
        question=f"Apa bentuk présent dari {verbe['infinitif']} untuk « {pronom} »?",
        stimulus_fr=verbe["infinitif"],
        stimulus_ipa=verbe["ipa"],
        stimulus_label=f"arti: {verbe['gloss']}",
        accepted=[forme, conjugaison.forme_affichee(index, forme)],
        accepted_lang="fr",
        reveal=conjugaison.forme_affichee(index, forme),
        reveal_fr=verbe["example"]["fr"],
        explain=f"{_tableau_txt(verbe)}\n   {verbe['example']['fr']} = {verbe['example']['gloss']}",
    )


def conjugation_mcq(verbe: dict, index: int, rng: random.Random) -> Question:
    """Soal buatan: pilih bentuk yang tepat di antara bentuk-bentuk kata kerja
    itu sendiri. Pengecoh dari tabelnya sendiri jauh lebih berguna daripada
    pengecoh acak, karena kesalahan nyata memang terjadi antar baris."""
    forme = verbe["present"][index]
    pronom = conjugaison.PRONOMS_AFFICHES[index]
    lain = [f for f in verbe["present"] if f != forme]
    # Urutan dibakukan lalu diacak, supaya hasilnya tetap bisa diulang.
    unik: list[str] = []
    for f in lain:
        if f not in unik:
            unik.append(f)
    rng.shuffle(unik)
    options, answer = _shuffle_options(rng, forme, unik[:3])
    return Question(
        card_id=verbe["id"],
        mode="konjugasi",
        kind="mcq",
        stage=verbe["stage"],
        question=f"Mana bentuk {verbe['infinitif']} untuk « {pronom} »?",
        stimulus_label=f"arti: {verbe['gloss']}",
        options=options,
        options_lang="fr",
        answer=answer,
        reveal=conjugaison.forme_affichee(index, forme),
        explain=_tableau_txt(verbe),
    )


# -------------------------------------------------------------- pelafalan ---

def _ipa_label(ipa: str) -> str:
    return f"/{ipa}/  ({approx(ipa)})"


def phon_question(item: dict) -> Question:
    """Soal pelafalan bertipe lafal, homophone, graphie, atau liaison."""
    t = item["type"]
    if t == "lafal":
        return Question(
            card_id=item["id"],
            mode="pelafalan",
            kind="mcq",
            stage=item["stage"],
            question="Bagaimana kata ini dibunyikan?",
            stimulus_fr=item["prompt_fr"],
            stimulus_label=f"arti: {item['gloss']}",
            options=list(item["options"]),
            options_lang="ipa",
            answer=item["answer"],
            reveal=_ipa_label(item["ipa"]),
            explain=item.get("explain"),
        )
    if t == "homophone":
        return Question(
            card_id=item["id"],
            mode="pelafalan",
            kind="mcq",
            stage=item["stage"],
            question=(
                f"Semua pilihan dibunyikan {_ipa_label(item['ipa'])}. "
                f"Mana yang berarti ‘{item['gloss']}’?"
            ),
            options=list(item["options"]),
            options_lang="fr",
            answer=item["answer"],
            reveal=item["options"][item["answer"]],
            explain=item.get("explain"),
        )
    if t == "graphie":
        return Question(
            card_id=item["id"],
            mode="pelafalan",
            kind="mcq",
            stage=item["stage"],
            question=f"Gabungan huruf mana yang dibunyikan {_ipa_label(item['ipa'])}?",
            options=list(item["options"]),
            options_lang="fr",
            answer=item["answer"],
            reveal=item["options"][item["answer"]],
            explain=item.get("explain"),
        )
    if t == "liaison":
        return Question(
            card_id=item["id"],
            mode="pelafalan",
            kind="mcq",
            stage=item["stage"],
            question="Apakah liaison di antara kedua kata ini wajib, boleh, atau terlarang?",
            stimulus_fr=item["prompt_fr"],
            stimulus_label=f"arti: {item['gloss']}",
            options=list(item["options"]),
            options_lang="id",
            answer=item["answer"],
            reveal=f"{dataio.LIAISON_LABELS[item['liaison_type']]} — {_ipa_label(item['ipa'])}",
            explain=item.get("explain"),
        )
    raise ValueError(f"jenis soal pelafalan tidak dikenal: {t}")


def elision_question(item: dict) -> Question:
    """Soal buatan: gabungkan dua kata, dengan elisi bila perlu.

    Kunci dihitung oleh phonetique.elide, bukan ditulis di data, sehingga
    kunci dan aturannya tidak bisa berbeda.
    """
    a, b = item["mots"]
    jawab = elide(a, b)
    return Question(
        card_id=item["id"],
        mode="pelafalan",
        kind="typed",
        stage=item["stage"],
        question=f"Tulis gabungan « {a} » + « {b} » sebagaimana ditulis dalam Bahasa Prancis.",
        stimulus_label=f"arti: {item['gloss']}",
        accepted=[jawab],
        accepted_lang="fr",
        reveal=f"{jawab}  {_ipa_label(item['ipa'])}",
        explain=item.get("explain"),
    )


def passage_question(p: dict) -> Question:
    return Question(
        card_id=p["id"],
        mode="pelafalan",
        kind="selfcheck",
        stage=p["stage"],
        question=(
            f"Bacalah dengan suara (Level {p['level']}), lalu bandingkan dengan lafalnya."
        ),
        stimulus_fr=p["fr"],
        options=None,
        reveal=f"{_ipa_label(p['ipa'])}\n   {p['gloss']}",
        reveal_ipa=p["ipa"],
        explain=p.get("note"),
    )


# -------------------------------------------------------------- kumpulan ---

def _conjugation_indices(verbe: dict, rng: random.Random) -> tuple[int, int]:
    """Satu baris tunggal dan satu baris jamak, dipilih ber-seed.

    Melatih dua baris per kata kerja per sesi, bukan keenamnya, supaya satu
    kata kerja tidak memakan seluruh sesi.
    """
    return rng.choice((0, 1, 2)), rng.choice((3, 4, 5))


def build_pool(mode: str, stage: int | None, rng: random.Random) -> list[Question]:
    """Bangun seluruh soal yang tersedia untuk satu mode."""
    if mode == "kosakata-fr":
        return [vocab_fr_to_id(e) for e in dataio.vocab_entries(stage)]
    if mode == "kosakata-id":
        pool = dataio.vocab_entries(stage)
        return [vocab_id_to_fr(e, pool, rng) for e in pool]
    if mode == "genre":
        return [genre_question(e, rng) for e in dataio.nouns(stage)]
    if mode == "tatabahasa":
        qs = [grammar_question(i) for i in dataio.grammar_items(stage)]
        qs += [loan_question(i) for i in dataio.loan_items(stage)]
        return qs
    if mode == "konjugasi":
        qs = [verb_item_question(i) for i in dataio.verb_items(stage)]
        for v in dataio.verbs(stage):
            i_sing, i_plur = _conjugation_indices(v, rng)
            qs.append(conjugation_typed(v, i_sing))
            qs.append(conjugation_mcq(v, i_plur, rng))
        return qs
    if mode == "pelafalan":
        qs: list[Question] = []
        for i in dataio.phon_items(stage):
            if i["type"] == "elision":
                qs.append(elision_question(i))
            else:
                qs.append(phon_question(i))
        qs += [passage_question(p) for p in dataio.phon_passages(stage)]
        return qs
    raise ValueError(f"mode tidak dikenal: {mode}")


__all__ = [
    "MODES",
    "MODE_LABELS",
    "Question",
    "accepted_set",
    "build_pool",
    "conjugation_mcq",
    "conjugation_typed",
    "elision_question",
    "expand_accepted",
    "genre_question",
    "grammar_question",
    "loan_question",
    "normalize_fr",
    "normalize_id",
    "passage_question",
    "phon_question",
    "verb_item_question",
    "vocab_detail",
    "vocab_display",
    "vocab_fr_to_id",
    "vocab_id_to_fr",
]
