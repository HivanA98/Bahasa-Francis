"""Pengujian kunci jawaban: tepat satu jawaban benar, dan kunci sesuai data."""

from __future__ import annotations

import random

import pytest

from frdrill import dataio
from frdrill.phonetique import elide
from frdrill.questions import (
    MODES,
    accepted_set,
    build_pool,
    conjugation_mcq,
    conjugation_typed,
    elision_question,
    genre_question,
    normalize_fr,
    normalize_id,
    vocab_id_to_fr,
)

SEEDS = (0, 1, 2, 7, 42)


def _all_mcq_items():
    for group, label in (
        (dataio.grammar_items(), "tatabahasa"),
        (dataio.verb_items(), "konjugasi"),
        (dataio.loan_items(), "serapan"),
        ([i for i in dataio.phon_items() if i["type"] != "elision"], "pelafalan"),
    ):
        for item in group:
            yield label, item


def test_indeks_jawaban_dalam_jangkauan():
    problems = []
    for label, item in _all_mcq_items():
        if not 0 <= item["answer"] < len(item["options"]):
            problems.append(f"{label} {item['id']}: answer di luar jangkauan")
    assert not problems, "\n".join(problems)


def test_pilihan_jawaban_tidak_ganda():
    """Pilihan ganda identik akan membuat dua jawaban sama-sama benar."""
    problems = []
    for label, item in _all_mcq_items():
        opts = item["options"]
        ganda = sorted({o for o in opts if opts.count(o) > 1})
        if ganda:
            problems.append(f"{label} {item['id']}: pilihan kembar {ganda}")
    assert not problems, "\n".join(problems)


def test_jumlah_pilihan_memadai():
    problems = [
        f"{label} {item['id']}: hanya {len(item['options'])} pilihan"
        for label, item in _all_mcq_items() if len(item["options"]) < 3
    ]
    assert not problems, "\n".join(problems)


def test_options_lang_sah():
    problems = [
        f"{label} {item['id']}: options_lang={item['options_lang']}"
        for label, item in _all_mcq_items()
        if item["options_lang"] not in ("fr", "id", "ipa")
    ]
    assert not problems, "\n".join(problems)


# ------------------------------------------------------ modul pelafalan ---

def test_semua_pilihan_homophone_berbunyi_sama():
    """Soal 'mana yang berarti X' tidak boleh bisa dijawab dari bunyinya.

    Bila salah satu pilihan berbeda lafalnya, soalnya menjadi sepele karena
    pengecohnya bukan homofon sama sekali.
    """
    problems = []
    for item in dataio.phon_items(kind="homophone"):
        bunyi = set(item["options_ipa"])
        if len(bunyi) != 1:
            problems.append(f"{item['id']}: lafal pilihan berbeda-beda {sorted(bunyi)}")
        elif item["options_ipa"][0] != item["ipa"]:
            problems.append(f"{item['id']}: ipa soal berbeda dari lafal pilihannya")
        if len(item["options_ipa"]) != len(item["options"]):
            problems.append(f"{item['id']}: jumlah options_ipa tidak sepadan")
    assert not problems, "\n".join(problems)


def test_kunci_soal_lafal_sama_dengan_field_ipa():
    problems = []
    for item in dataio.phon_items(kind="lafal"):
        if item["options"][item["answer"]] != item["ipa"]:
            problems.append(
                f"{item['id']}: kunci {item['options'][item['answer']]!r} "
                f"berbeda dari ipa {item['ipa']!r}"
            )
    assert not problems, "\n".join(problems)


def test_pengecoh_soal_lafal_berbeda_dari_kuncinya():
    problems = []
    for item in dataio.phon_items(kind="lafal"):
        lain = [o for i, o in enumerate(item["options"]) if i != item["answer"]]
        if item["ipa"] in lain:
            problems.append(f"{item['id']}: pengecoh sama dengan kunci")
    assert not problems, "\n".join(problems)


def test_kunci_soal_graphie_ada_di_aturannya():
    """Kunci wajib tercantum sebagai graphie pada regle yang dirujuk soal."""
    problems = []
    for item in dataio.phon_items(kind="graphie"):
        regle = dataio.rule_by_id(item["regle"])
        assert regle is not None
        kunci = item["options"][item["answer"]]
        if kunci not in regle["graphies"]:
            problems.append(
                f"{item['id']}: kunci {kunci!r} tidak ada di graphies {regle['graphies']}"
            )
    assert not problems, "\n".join(problems)


def test_kunci_soal_liaison_sesuai_jenisnya():
    problems = []
    for item in dataio.phon_items(kind="liaison"):
        label = dataio.LIAISON_LABELS[item["liaison_type"]]
        if item["options"][item["answer"]] != label:
            problems.append(
                f"{item['id']}: kunci {item['options'][item['answer']]!r} "
                f"tidak sesuai liaison_type {item['liaison_type']}"
            )
        if set(item["options"]) != set(dataio.LIAISON_LABELS.values()):
            problems.append(f"{item['id']}: pilihan liaison tidak lengkap")
    assert not problems, "\n".join(problems)


def test_soal_elisi_memuat_dua_kata_dan_memang_berelisi():
    problems = []
    for item in dataio.phon_items(kind="elision"):
        mots = item.get("mots") or []
        if len(mots) != 2:
            problems.append(f"{item['id']}: mots harus berisi dua kata")
            continue
        hasil = elide(mots[0], mots[1])
        q = elision_question(item)
        if q.accepted != [hasil]:
            problems.append(f"{item['id']}: kunci soal tidak dihitung dari mesin")
    assert not problems, "\n".join(problems)


def test_kumpulan_soal_elisi_memuat_contoh_tanpa_elisi():
    """Kalau semua contohnya berelisi, pembelajar akan menyangka elisi selalu
    terjadi. Harus ada setidaknya satu contoh yang justru tidak berelisi."""
    hasil = [
        elide(i["mots"][0], i["mots"][1]) for i in dataio.phon_items(kind="elision")
    ]
    assert any("'" not in h for h in hasil), "tidak ada contoh tanpa elisi"


# --------------------------------------------------- soal buatan otomatis ---

@pytest.mark.parametrize("seed", SEEDS)
def test_soal_kosakata_id_ke_fr_hanya_satu_jawaban_benar(seed):
    pool = dataio.vocab_entries()
    by_fr: dict[str, list[dict]] = {}
    for e in pool:
        by_fr.setdefault(e["fr"], []).append(e)
    problems = []
    for e in pool:
        q = vocab_id_to_fr(e, pool, random.Random(seed))
        if q.options[q.answer] != e["fr"]:
            problems.append(f"{e['id']}: kunci tidak menunjuk kata yang benar")
        if len(set(q.options)) != len(q.options):
            problems.append(f"{e['id']}: pilihan kembar")
        prompt_key = normalize_id(e["gloss"])
        for i, opt in enumerate(q.options):
            if i == q.answer:
                continue
            for cand in by_fr.get(opt, []):
                if prompt_key in accepted_set(cand):
                    problems.append(
                        f"{e['id']} '{e['gloss']}': pengecoh {opt} juga jawaban benar"
                    )
    assert not problems, "\n".join(problems)


@pytest.mark.parametrize("seed", SEEDS)
def test_soal_artikel_hanya_satu_jawaban_benar(seed):
    problems = []
    for e in dataio.nouns():
        q = genre_question(e, random.Random(seed))
        benar = q.options[q.answer]
        diharapkan = (
            f"{e['article']}{e['fr']}" if e["article"].endswith("'")
            else f"{e['article']} {e['fr']}"
        )
        if benar != diharapkan:
            problems.append(f"{e['id']}: kunci {benar!r} bukan {diharapkan!r}")
        if len(set(q.options)) != len(q.options):
            problems.append(f"{e['id']}: pilihan kembar")
        if len(q.options) != 3:
            problems.append(f"{e['id']}: pilihan artikel seharusnya tiga")
    assert not problems, "\n".join(problems)


@pytest.mark.parametrize("seed", SEEDS)
def test_soal_konjugasi_buatan_memakai_tabel_data(seed):
    problems = []
    for v in dataio.verbs():
        for i in range(6):
            q = conjugation_typed(v, i)
            if v["present"][i] not in q.accepted:
                problems.append(f"{v['id']} baris {i}: kunci tidak dari tabel data")
            m = conjugation_mcq(v, i, random.Random(seed))
            if m.options[m.answer] != v["present"][i]:
                problems.append(f"{v['id']} baris {i}: kunci pilihan ganda salah")
            if len(set(m.options)) != len(m.options):
                problems.append(f"{v['id']} baris {i}: pilihan kembar")
            for o in m.options:
                if o not in v["present"]:
                    problems.append(f"{v['id']}: pengecoh {o} bukan bentuk kata kerja ini")
    assert not problems, "\n".join(problems)


def test_jawaban_konjugasi_menerima_bentuk_dengan_dan_tanpa_kata_ganti():
    v = dataio.verb_by_id("c05")  # parler
    q = conjugation_typed(v, 3)
    assert q.is_correct_text("parlons")
    assert q.is_correct_text("nous parlons")
    assert not q.is_correct_text("parlez")


def test_jawaban_prancis_memaafkan_aksen_dan_tanda_kutip():
    v = dataio.verb_by_id("c02")  # avoir
    q = conjugation_typed(v, 0)
    assert q.is_correct_text("ai")
    assert q.is_correct_text("j'ai")
    assert q.is_correct_text("J AI")
    assert not q.is_correct_text("as")


@pytest.mark.parametrize("seed", SEEDS)
@pytest.mark.parametrize("mode", MODES)
def test_setiap_soal_punya_kunci_yang_sah(mode, seed):
    problems = []
    for q in build_pool(mode, None, random.Random(seed)):
        if q.kind == "mcq":
            if q.options is None or q.answer is None:
                problems.append(f"{q.card_id}: soal mcq tanpa pilihan atau kunci")
                continue
            if not 0 <= q.answer < len(q.options):
                problems.append(f"{q.card_id}: kunci di luar jangkauan")
            if len(set(q.options)) != len(q.options):
                problems.append(f"{q.card_id}: pilihan kembar")
        elif q.kind == "typed":
            if not q.accepted:
                problems.append(f"{q.card_id}: soal bertaip tanpa jawaban yang diterima")
        elif q.kind == "selfcheck":
            if not q.reveal:
                problems.append(f"{q.card_id}: selfcheck tanpa jawaban pembanding")
        else:
            problems.append(f"{q.card_id}: kind tidak dikenal: {q.kind}")
        if not q.question.strip():
            problems.append(f"{q.card_id}: pertanyaan kosong")
        if q.accepted_lang not in ("fr", "id"):
            problems.append(f"{q.card_id}: accepted_lang tidak dikenal")
    assert not problems, "\n".join(problems)


def test_jawaban_bertaip_menerima_arti_utama():
    """Mengetik arti utama harus dinilai benar."""
    problems = []
    for q in build_pool("kosakata-fr", None, random.Random(0)):
        entry = next(e for e in dataio.vocab_entries() if e["id"] == q.card_id)
        if not q.is_correct_text(entry["gloss"]):
            problems.append(f"{q.card_id}: arti utama tidak diterima")
        for a in entry.get("alt") or []:
            if not q.is_correct_text(a):
                problems.append(f"{q.card_id}: arti alternatif {a!r} tidak diterima")
    assert not problems, "\n".join(problems)


def test_jawaban_bertaip_menolak_arti_yang_salah():
    livre = next(e for e in dataio.vocab_entries() if e["fr"] == "livre")
    q = next(q for q in build_pool("kosakata-fr", None, random.Random(0))
             if q.card_id == livre["id"])
    assert q.is_correct_text("buku")
    assert q.is_correct_text("  BUKU  ")
    assert not q.is_correct_text("pulpen")
    assert not q.is_correct_text("")


def test_normalisasi_dua_bahasa_berbeda_perlakuan():
    # Bahasa Indonesia: tanda baca dibuang, spasi dipertahankan.
    assert normalize_id("Tidak apa-apa!") == "tidak apa apa"
    # Bahasa Prancis: aksen, kutip, dan spasi diabaikan.
    assert normalize_fr("J'ai") == normalize_fr("jai") == "jai"
    assert normalize_fr("préfère") == normalize_fr("prefere")


@pytest.mark.parametrize("mode", MODES)
def test_pool_dapat_diulang_dengan_seed_sama(mode):
    a = build_pool(mode, None, random.Random(5))
    b = build_pool(mode, None, random.Random(5))
    assert [q.question for q in a] == [q.question for q in b]
    assert [q.options for q in a] == [q.options for q in b]


@pytest.mark.parametrize("mode", MODES)
def test_pembatasan_tahap_mengurangi_soal(mode):
    semua = build_pool(mode, None, random.Random(0))
    tahap1 = build_pool(mode, 1, random.Random(0))
    assert len(tahap1) <= len(semua)
    assert all(q.stage <= 1 for q in tahap1 if q.stage is not None)
