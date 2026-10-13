"""Pengujian kotak Leitner: kenaikan, penurunan, jadwal, dan berkas progres."""

from __future__ import annotations

import datetime as dt
import json
import os

import pytest

from frdrill.leitner import (
    INTERVALS,
    MAX_BOX,
    MIN_BOX,
    PROGRESS_VERSION,
    CardState,
    Progress,
)

HARI = dt.date(2026, 1, 1)


def test_kartu_baru_mulai_di_kotak_satu_dan_jatuh_tempo():
    st = CardState()
    assert st.box == MIN_BOX
    assert st.is_due()


def test_jawaban_benar_menaikkan_satu_kotak():
    st = CardState()
    st.answer(True, HARI)
    assert st.box == 2
    assert st.correct == 1 and st.seen == 1


def test_jawaban_salah_mengembalikan_ke_kotak_satu():
    st = CardState(box=4)
    st.answer(False, HARI)
    assert st.box == MIN_BOX
    assert st.wrong == 1


def test_kotak_tidak_melebihi_maksimum():
    st = CardState(box=MAX_BOX)
    st.answer(True, HARI)
    assert st.box == MAX_BOX


@pytest.mark.parametrize("box,jeda", sorted(INTERVALS.items()))
def test_jadwal_sesuai_tabel_jeda(box, jeda):
    st = CardState(box=box - 1 if box > MIN_BOX else MIN_BOX)
    if box == MIN_BOX:
        st.answer(False, HARI)
    else:
        st.answer(True, HARI)
    assert st.box == box
    assert st.due == (HARI + dt.timedelta(days=jeda)).isoformat()


def test_kartu_belum_jatuh_tempo_tidak_dianggap_due():
    st = CardState()
    st.answer(True, HARI)          # naik ke kotak 2, jatuh tempo besok
    assert not st.is_due(HARI)
    assert st.is_due(HARI + dt.timedelta(days=1))


def test_simpan_dan_muat_ulang(tmp_path):
    path = str(tmp_path / "progress.json")
    p = Progress()
    p.record_answer("v001", True, HARI)
    p.record_answer("v002", False, HARI)
    p.log_session({"tanggal": "2026-01-01", "soal": 2})
    p.save(path)

    q = Progress.load(path)
    assert q.version == PROGRESS_VERSION
    assert q.state("v001").box == 2
    assert q.state("v002").box == 1
    assert q.sessions[-1]["soal"] == 2


def test_memuat_berkas_yang_tidak_ada_menghasilkan_progres_kosong(tmp_path):
    p = Progress.load(str(tmp_path / "belum-ada.json"))
    assert p.cards == {}
    assert p.settings.get("lafal") is True


def test_berkas_dengan_kartu_rusak_tidak_menggugurkan_pemuatan(tmp_path):
    path = str(tmp_path / "progress.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump({
            "version": PROGRESS_VERSION,
            "cards": {"v001": {"box": 3, "due": "2026-01-01"}, "v002": "rusak"},
        }, f)
    p = Progress.load(path)
    assert p.state("v001").box == 3
    assert "v002" not in p.cards


def test_kotak_di_luar_jangkauan_dijepit_saat_dimuat(tmp_path):
    path = str(tmp_path / "progress.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump({"cards": {"a": {"box": 99}, "b": {"box": -4}}}, f)
    p = Progress.load(path)
    assert p.state("a").box == MAX_BOX
    assert p.state("b").box == MIN_BOX


def test_penulisan_atomik_tidak_meninggalkan_berkas_sementara(tmp_path):
    path = str(tmp_path / "sub" / "progress.json")
    p = Progress()
    p.record_answer("v001", True, HARI)
    p.save(path)
    sisa = [f for f in os.listdir(os.path.dirname(path)) if f.endswith(".tmp")]
    assert not sisa
    assert os.path.exists(path)


def test_hitungan_kotak_dan_daftar_jatuh_tempo():
    p = Progress()
    for cid in ("a", "b", "c"):
        p.record_answer(cid, True, HARI)
    p.record_answer("c", True, HARI)        # c naik ke kotak 3
    counts = p.box_counts(["a", "b", "c"])
    assert counts[2] == 2 and counts[3] == 1
    assert p.due_ids(["a", "b", "c"], HARI) == []
    assert p.due_ids(["a", "b", "c"], HARI + dt.timedelta(days=1)) == ["a", "b"]
    assert p.new_ids(["a", "zzz"]) == ["zzz"]


def test_sesi_yang_disimpan_dibatasi(tmp_path):
    path = str(tmp_path / "progress.json")
    p = Progress()
    for i in range(250):
        p.log_session({"tanggal": "2026-01-01", "soal": i})
    p.save(path)
    q = Progress.load(path)
    assert len(q.sessions) == 200
    assert q.sessions[-1]["soal"] == 249
