"""Pengujian penyusun sesi: jatah materi baru, ulangan, dan interleaving."""

from __future__ import annotations

import datetime as dt

import pytest

from frdrill import dataio
from frdrill.leitner import Progress
from frdrill.questions import MODES
from frdrill.session import (
    GROUP_WEIGHTS,
    MODE_GROUPS,
    NEW_SHARE,
    plan_session,
    upcoming_counts,
)

HARI = dt.date(2026, 1, 1)


def test_sesi_pertama_memperkenalkan_kartu_baru():
    plan = plan_session(Progress(), new_per_session=8, seed=1, on=HARI)
    assert plan.questions
    assert plan.n_new > 0
    assert plan.n_due == 0


def test_jatah_kartu_baru_dihormati():
    """Jumlah KARTU baru dibatasi, walaupun satu kartu bisa muncul sebagai
    beberapa soal (Prancis ke Indonesia, Indonesia ke Prancis, artikel)."""
    for n in (2, 4, 8):
        plan = plan_session(Progress(), new_per_session=n, seed=2, on=HARI)
        # Jatah dibagi per kelompok dengan pembulatan ke atas, sehingga
        # jumlahnya bisa sedikit melebihi n tetapi tidak boleh berlipat.
        assert plan.n_new <= n + len(GROUP_WEIGHTS)


def test_new_nol_berarti_tidak_ada_materi_baru():
    plan = plan_session(Progress(), new_per_session=0, seed=3, on=HARI)
    assert plan.n_new == 0
    assert not plan.questions, "tanpa kartu jatuh tempo dan tanpa materi baru, sesi kosong"


def test_satu_kata_dilatih_beberapa_arah():
    """Kartu kosakata yang sama muncul sebagai soal di beberapa mode."""
    plan = plan_session(
        Progress(), modes=["kosakata-fr", "kosakata-id"], new_per_session=4,
        seed=4, on=HARI,
    )
    per_card: dict[str, set[str]] = {}
    for q in plan.questions:
        per_card.setdefault(q.card_id, set()).add(q.mode)
    assert any(len(m) > 1 for m in per_card.values())


def test_kartu_belum_jatuh_tempo_tidak_muncul():
    p = Progress()
    ids = [e["id"] for e in dataio.vocab_entries()[:20]]
    for cid in ids:
        p.record_answer(cid, True, HARI)      # jatuh tempo besok
    plan = plan_session(p, new_per_session=0, seed=5, on=HARI)
    assert not any(q.card_id in ids for q in plan.questions)
    besok = plan_session(p, new_per_session=0, seed=5, on=HARI + dt.timedelta(days=1))
    assert any(q.card_id in ids for q in besok.questions)


def test_ulangan_tidak_tergeser_habis_oleh_materi_baru():
    p = Progress()
    for e in dataio.vocab_entries()[:60]:
        p.record_answer(e["id"], False, HARI)   # semuanya jatuh tempo hari ini
    plan = plan_session(p, new_per_session=20, limit=40, seed=6, on=HARI)
    baru = sum(1 for q in plan.questions if p.is_new(q.card_id))
    assert baru <= max(1, int(40 * NEW_SHARE)) + 1
    assert len(plan.questions) - baru > 0


def test_materi_baru_masuk_menurut_urutan_tahap():
    plan = plan_session(Progress(), new_per_session=6, seed=7, on=HARI)
    tahap = [q.stage for q in plan.questions if q.stage is not None]
    assert tahap and max(tahap) <= 2, f"tahap pada sesi pertama: {sorted(set(tahap))}"


def test_interleaving_mencampur_mode():
    plan = plan_session(Progress(), new_per_session=8, seed=8, on=HARI)
    modes = [q.mode for q in plan.questions]
    assert len(set(modes)) > 1
    # Tidak boleh satu mode berderet lebih dari separuh sesi.
    deret = maks = 1
    for a, b in zip(modes, modes[1:]):
        deret = deret + 1 if a == b else 1
        maks = max(maks, deret)
    assert maks <= max(3, len(modes) // 2)


def test_sesi_dapat_diulang_dengan_seed_sama():
    a = plan_session(Progress(), seed=9, on=HARI)
    b = plan_session(Progress(), seed=9, on=HARI)
    assert [q.card_id for q in a.questions] == [q.card_id for q in b.questions]
    assert [q.question for q in a.questions] == [q.question for q in b.questions]


def test_seed_berbeda_menghasilkan_susunan_berbeda():
    a = plan_session(Progress(), seed=10, on=HARI)
    b = plan_session(Progress(), seed=11, on=HARI)
    assert [q.card_id for q in a.questions] != [q.card_id for q in b.questions]


def test_batas_soal_dihormati():
    for limit in (5, 12, 30):
        plan = plan_session(Progress(), limit=limit, new_per_session=20, seed=12, on=HARI)
        assert len(plan.questions) <= limit


def test_lintasan_kedua_tidak_menambah_kartu_baru():
    plan = plan_session(Progress(), new_per_session=4, limit=40, seed=13, on=HARI)
    ulangan = [q for q in plan.questions if q.repeat]
    if ulangan:
        kartu_baru = {q.card_id for q in plan.questions if not q.repeat}
        assert all(q.card_id in kartu_baru for q in ulangan)


@pytest.mark.parametrize("mode", MODES)
def test_sesi_satu_mode_hanya_memuat_mode_itu(mode):
    plan = plan_session(Progress(), modes=[mode], new_per_session=6, seed=14, on=HARI)
    assert plan.questions
    assert {q.mode for q in plan.questions} == {mode}


def test_pembatasan_tahap_menyaring_materi():
    plan = plan_session(Progress(), stage=1, new_per_session=20, seed=15, on=HARI)
    assert all(q.stage <= 1 for q in plan.questions if q.stage is not None)


def test_setiap_mode_punya_kelompok_materi():
    assert set(MODE_GROUPS) == set(MODES)
    assert set(MODE_GROUPS.values()) <= set(GROUP_WEIGHTS)


def test_ringkasan_mendatang_menjumlah_seluruh_kartu():
    p = Progress()
    ids = dataio.all_card_ids()
    p.record_answer(ids[0], True, HARI)
    c = upcoming_counts(p, ids, HARI)
    assert c["baru"] + c["jatuh_tempo"] + c["belum_jatuh_tempo"] == len(ids)
    assert c["belum_jatuh_tempo"] == 1
