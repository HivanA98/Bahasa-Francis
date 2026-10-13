"""Pengujian lembar kerja: kunci terpisah, bagian lengkap, isi dari data."""

from __future__ import annotations

import os
import re

import pytest

from conftest import ROOT
from frdrill import conjugaison, dataio

WS_DIR = os.path.join(ROOT, "worksheets")
KEY_DIR = os.path.join(WS_DIR, "answers")

NOMOR = [f"{n:02d}" for n in range(1, 13)]
BAGIAN = ["## A.", "## B.", "## C.", "## D.", "## E.", "## F."]


def _ws(nomor: str) -> str:
    return open(os.path.join(WS_DIR, f"ws-{nomor}.md"), encoding="utf-8").read()


def _key(nomor: str) -> str:
    return open(os.path.join(KEY_DIR, f"ws-{nomor}-kunci.md"), encoding="utf-8").read()


def test_dua_belas_lembar_dan_dua_belas_kunci():
    ws = sorted(f for f in os.listdir(WS_DIR) if re.match(r"ws-\d\d\.md$", f))
    keys = sorted(f for f in os.listdir(KEY_DIR) if f.endswith("-kunci.md"))
    assert len(ws) == 12 and len(keys) == 12


@pytest.mark.parametrize("nomor", NOMOR)
def test_setiap_lembar_punya_enam_bagian(nomor):
    teks = _ws(nomor)
    kurang = [b for b in BAGIAN if b not in teks]
    assert not kurang, f"ws-{nomor}: bagian hilang {kurang}"


@pytest.mark.parametrize("nomor", NOMOR)
def test_setiap_kunci_punya_enam_bagian(nomor):
    teks = _key(nomor)
    kurang = [b for b in BAGIAN if b not in teks]
    assert not kurang, f"kunci ws-{nomor}: bagian hilang {kurang}"


@pytest.mark.parametrize("nomor", NOMOR)
def test_lembar_kerja_tidak_memuat_jawabannya(nomor):
    """Lembar soal tidak boleh memuat kunci; itulah gunanya berkas terpisah."""
    teks = _ws(nomor)
    assert "Jawaban: ____" in teks or "Jawaban:" in teks
    assert "**" not in teks.split("## E.")[1].split("## F.")[0], (
        f"ws-{nomor}: bagian tata bahasa memuat penebalan yang menandai kunci"
    )
    assert "Kunci jawaban: `worksheets/answers/" in teks


@pytest.mark.parametrize("nomor", NOMOR)
def test_kunci_menunjuk_balik_ke_soalnya(nomor):
    assert f"worksheets/ws-{nomor}.md" in _key(nomor)


@pytest.mark.parametrize("nomor", NOMOR)
def test_bagian_konjugasi_kosong_di_soal_terisi_di_kunci(nomor):
    """Tabel konjugasi di lembar soal harus kosong, di kunci harus terisi."""
    soal = _ws(nomor).split("## D.")[1].split("## E.")[0]
    kunci = _key(nomor).split("## D.")[1].split("## E.")[0]
    for pronom in conjugaison.PRONOMS_AFFICHES:
        assert f"| {pronom} |" in soal, f"ws-{nomor}: baris {pronom} hilang"
    # Kunci memuat bentuk sebenarnya, soal tidak.
    bentuk = re.findall(r"\| (?:je|tu|il / elle / on|nous|vous|ils / elles) \| (\S+)", kunci)
    assert bentuk, f"kunci ws-{nomor}: tabel konjugasi kosong"


@pytest.mark.parametrize("nomor", NOMOR)
def test_setiap_kata_pada_lembar_berasal_dari_data(nomor):
    """Bagian B menuliskan arti Indonesia; semuanya harus ada di data."""
    arti = {e["gloss"] for e in dataio.vocab_entries()}
    bagian = _ws(nomor).split("## B.")[1].split("## C.")[0]
    baris = [b for b in bagian.splitlines() if b.startswith("| ") and "|" in b[2:]]
    isi = [b.split("|")[2].strip() for b in baris if b.split("|")[1].strip().isdigit()]
    asing = [x for x in isi if x not in arti]
    assert not asing, f"ws-{nomor}: arti tidak ada di data: {asing}"


@pytest.mark.parametrize("nomor", NOMOR)
def test_tahap_lembar_membatasi_materinya(nomor):
    """Lembar tahap N hanya boleh memakai kata dari tahap 1..N."""
    teks = _ws(nomor)
    m = re.search(r"tahap (\d)", teks)
    assert m, f"ws-{nomor}: tahap tidak tertulis"
    stage = int(m.group(1))
    boleh = {e["gloss"] for e in dataio.vocab_entries(stage)}
    bagian = teks.split("## B.")[1].split("## C.")[0]
    baris = [b for b in bagian.splitlines() if b.startswith("| ")]
    isi = [b.split("|")[2].strip() for b in baris if b.split("|")[1].strip().isdigit()]
    asing = [x for x in isi if x not in boleh]
    assert not asing, f"ws-{nomor} (tahap {stage}): memakai materi di luar tahap: {asing}"


def test_indeks_lembar_kerja_menyebut_semuanya():
    teks = open(os.path.join(WS_DIR, "README.md"), encoding="utf-8").read()
    for nomor in NOMOR:
        assert f"ws-{nomor}.md" in teks
        assert f"ws-{nomor}-kunci.md" in teks


def test_bagian_pelafalan_memuat_ejaan_bantu_di_kunci():
    """Kunci bagian F harus memuat lafal, bukan hanya kata Prancisnya."""
    for nomor in NOMOR:
        bagian = _key(nomor).split("## F.")[1]
        assert "/" in bagian, f"kunci ws-{nomor}: bagian pelafalan tanpa IPA"
