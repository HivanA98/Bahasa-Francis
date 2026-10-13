"""Pengujian ekspor: hasil di repositori harus sama dengan yang dihasilkan ulang.

Berkas di data/csv/, anki/, worksheets/, dan webdata.js adalah TURUNAN dari
data/*.json. Pengujian ini membuat ulang semuanya ke folder sementara lalu
membandingkannya dengan yang tersimpan. Bila berbeda, berarti data sudah
berubah tetapi ekspornya belum dibuat ulang.
"""

from __future__ import annotations

import csv
import json
import os
import re

import pytest

from conftest import ROOT, load_tool

CSV_DIR = os.path.join(ROOT, "data", "csv")
ANKI_DIR = os.path.join(ROOT, "anki")
WS_DIR = os.path.join(ROOT, "worksheets")
KEY_DIR = os.path.join(WS_DIR, "answers")
WEBDATA = os.path.join(ROOT, "webdata.js")


def _regenerate_exports(tmp_path):
    mod = load_tool("build_exports")
    mod.CSV_DIR = str(tmp_path / "csv")
    mod.ANKI_DIR = str(tmp_path / "anki")
    mod.main()
    return str(tmp_path / "csv"), str(tmp_path / "anki")


def _regenerate_worksheets(tmp_path):
    mod = load_tool("build_worksheets")
    mod.WS_DIR = str(tmp_path / "ws")
    mod.KEY_DIR = str(tmp_path / "ws" / "answers")
    mod.main()
    return str(tmp_path / "ws"), str(tmp_path / "ws" / "answers")


def _compare_dirs(baru: str, lama: str, label: str) -> None:
    nama_baru = sorted(f for f in os.listdir(baru) if os.path.isfile(os.path.join(baru, f)))
    nama_lama = sorted(f for f in os.listdir(lama) if os.path.isfile(os.path.join(lama, f)))
    assert nama_baru == nama_lama, (
        f"{label}: daftar berkas berbeda.\nbaru: {nama_baru}\ntersimpan: {nama_lama}"
    )
    beda = []
    for nama in nama_baru:
        a = open(os.path.join(baru, nama), encoding="utf-8").read()
        b = open(os.path.join(lama, nama), encoding="utf-8").read()
        if a != b:
            beda.append(nama)
    assert not beda, (
        f"{label}: berkas berikut tidak mutakhir, jalankan ulang skripnya: {beda}"
    )


def test_ekspor_csv_mutakhir(tmp_path):
    csv_baru, _ = _regenerate_exports(tmp_path)
    _compare_dirs(csv_baru, CSV_DIR, "data/csv")


def test_ekspor_anki_mutakhir(tmp_path):
    _, anki_baru = _regenerate_exports(tmp_path)
    nama = sorted(f for f in os.listdir(ANKI_DIR) if f.endswith(".csv"))
    assert sorted(os.listdir(anki_baru)) == nama
    beda = [
        n for n in nama
        if open(os.path.join(anki_baru, n), encoding="utf-8").read()
        != open(os.path.join(ANKI_DIR, n), encoding="utf-8").read()
    ]
    assert not beda, f"anki/: tidak mutakhir, jalankan tools/build_exports.py: {beda}"


def test_lembar_kerja_mutakhir(tmp_path):
    ws_baru, key_baru = _regenerate_worksheets(tmp_path)
    nama_ws_baru = sorted(f for f in os.listdir(ws_baru) if f.endswith(".md"))
    nama_ws_lama = sorted(f for f in os.listdir(WS_DIR) if f.endswith(".md"))
    assert nama_ws_baru == nama_ws_lama
    beda = [
        n for n in nama_ws_baru
        if open(os.path.join(ws_baru, n), encoding="utf-8").read()
        != open(os.path.join(WS_DIR, n), encoding="utf-8").read()
    ]
    assert not beda, f"worksheets/: tidak mutakhir: {beda}"
    _compare_dirs(key_baru, KEY_DIR, "worksheets/answers")


def test_webdata_mutakhir(tmp_path):
    mod = load_tool("build_web")
    mod.OUT = str(tmp_path / "webdata.js")
    mod.main()
    baru = open(mod.OUT, encoding="utf-8").read()
    lama = open(WEBDATA, encoding="utf-8").read()
    assert baru == lama, "webdata.js tidak mutakhir, jalankan tools/build_web.py"


# ----------------------------------------------- isi berkas hasil ekspor ---

def _read_csv(path: str) -> tuple[list[str], list[list[str]]]:
    with open(path, encoding="utf-8", newline="") as f:
        rows = list(csv.reader(f))
    return rows[0], rows[1:]


@pytest.mark.parametrize(
    "nama",
    ["kosakata.csv", "tatabahasa_items.csv", "konjugasi_verbes.csv",
     "pelafalan_items.csv", "serapan_entries.csv"],
)
def test_csv_punya_baris_judul_dan_isi(nama):
    header, rows = _read_csv(os.path.join(CSV_DIR, nama))
    assert header and header[0] == "id"
    assert rows, f"{nama} kosong"
    assert all(len(r) == len(header) for r in rows), f"{nama}: jumlah kolom tidak rata"


def test_kolom_answer_text_sesuai_kunci():
    """Kolom answer_text pada CSV harus sama dengan options[answer]."""
    for nama in ("tatabahasa_items.csv", "konjugasi_items.csv", "serapan_items.csv"):
        header, rows = _read_csv(os.path.join(CSV_DIR, nama))
        i_opts, i_ans, i_text = (header.index(c) for c in ("options", "answer", "answer_text"))
        for r in rows:
            opts = r[i_opts].split(" | ")
            assert r[i_text] == opts[int(r[i_ans])], f"{nama}: {r[0]} answer_text salah"


def test_csv_kosakata_memuat_semua_entri():
    from frdrill import dataio

    _header, rows = _read_csv(os.path.join(CSV_DIR, "kosakata.csv"))
    assert len(rows) == len(dataio.vocab_entries())
    assert [r[0] for r in rows] == [e["id"] for e in dataio.vocab_entries()]


def test_csv_konjugasi_memuat_enam_bentuk():
    from frdrill import dataio

    header, rows = _read_csv(os.path.join(CSV_DIR, "konjugasi_verbes.csv"))
    kolom = [header.index(c) for c in ("je", "tu", "il", "nous", "vous", "ils")]
    for r, v in zip(rows, dataio.verbs()):
        assert [r[i] for i in kolom] == v["present"], f"{r[0]}: tabel CSV tidak cocok"


def test_anki_memakai_baris_pengarah_dan_tanpa_baris_judul():
    for nama in os.listdir(ANKI_DIR):
        if not nama.endswith(".csv"):
            continue
        baris = open(os.path.join(ANKI_DIR, nama), encoding="utf-8").read().splitlines()
        assert baris[0] == "#separator:Comma", f"{nama}: baris pengarah hilang"
        assert any(b.startswith("#tags column:") for b in baris[:4]), nama
        isi = [b for b in baris if not b.startswith("#")]
        assert isi, f"{nama} tidak punya kartu"
        assert not isi[0].startswith('"id"'), f"{nama}: Anki tidak memakai baris judul"


def test_anki_setiap_kartu_punya_sisi_depan_dan_belakang():
    for nama in os.listdir(ANKI_DIR):
        if not nama.endswith(".csv"):
            continue
        with open(os.path.join(ANKI_DIR, nama), encoding="utf-8", newline="") as f:
            rows = [r for r in csv.reader(f) if r and not r[0].startswith("#")]
        for r in rows:
            assert r[0].strip(), f"{nama}: ada kartu tanpa sisi depan"
            assert r[1].strip(), f"{nama}: ada kartu tanpa sisi belakang"


def test_anki_jumlah_kolom_seragam_per_berkas():
    for nama in os.listdir(ANKI_DIR):
        if not nama.endswith(".csv"):
            continue
        with open(os.path.join(ANKI_DIR, nama), encoding="utf-8", newline="") as f:
            rows = [r for r in csv.reader(f) if r and not r[0].startswith("#")]
        lebar = {len(r) for r in rows}
        assert len(lebar) == 1, f"{nama}: lebar kolom tidak seragam {lebar}"


def test_anki_kolom_tag_benar():
    """Kolom terakhir setiap kartu harus berisi tag, bukan isi pelajaran."""
    for nama in os.listdir(ANKI_DIR):
        if not nama.endswith(".csv"):
            continue
        with open(os.path.join(ANKI_DIR, nama), encoding="utf-8", newline="") as f:
            rows = [r for r in csv.reader(f) if r and not r[0].startswith("#")]
        for r in rows:
            assert r[-1].startswith("prancis::"), f"{nama}: kolom tag tidak berisi tag"


# ----------------------------------------------------------- aplikasi web ---

def _webdata() -> dict:
    teks = open(WEBDATA, encoding="utf-8").read()
    mulai = teks.index("{")
    return json.loads(teks[mulai:].rstrip().rstrip(";"))


def test_webdata_memuat_semua_modul():
    d = _webdata()
    for kunci in ("kosakata", "tatabahasa", "topik", "konjugasi", "groupes",
                  "pelafalan", "regles", "skema", "serapan", "catatan"):
        assert kunci in d, f"webdata.js kehilangan {kunci}"
        assert d[kunci], f"webdata.js: {kunci} kosong"


def test_kunci_soal_di_webdata_sama_dengan_data():
    from frdrill import dataio

    d = _webdata()
    oleh_id = {x["id"]: x for x in d["tatabahasa"]}
    for item in dataio.grammar_items():
        web = oleh_id[item["id"]]
        assert web["options"] == item["options"]
        assert web["answer"] == item["answer"]


def test_ejaan_bantu_di_webdata_dihitung_dari_ipa():
    from frdrill.phonetique import approx

    d = _webdata()
    for x in d["kosakata"]:
        assert x["approx"] == approx(x["ipa"]), f"{x['id']}: ejaan bantu tidak sejalan"
    for s in d["skema"]:
        assert s["approx"] == approx(s["ipa"])


def test_kunci_elisi_di_webdata_dihitung_mesin():
    from frdrill.phonetique import elide

    d = _webdata()
    for x in d["pelafalan"]:
        if x.get("type") == "elision":
            assert x["reponse"] == elide(x["mots"][0], x["mots"][1])


def _tanpa_komentar(js: str) -> str:
    """Buang komentar /* */ dan // supaya pemeriksaan hanya mengenai kode."""
    js = re.sub(r"/\*.*?\*/", "", js, flags=re.S)
    return re.sub(r"//[^\n]*", "", js)


def test_aplikasi_web_tidak_memakai_fetch():
    """Aplikasi harus tetap jalan saat index.html dibuka lewat file://."""
    app = _tanpa_komentar(open(os.path.join(ROOT, "app.js"), encoding="utf-8").read())
    assert "fetch(" not in app
    assert "XMLHttpRequest" not in app
    html = open(os.path.join(ROOT, "index.html"), encoding="utf-8").read()
    assert 'src="webdata.js"' in html


def test_jeda_kotak_web_sama_dengan_versi_terminal():
    """BOX_DAYS di app.js harus sama dengan INTERVALS di frdrill/leitner.py."""
    from frdrill.leitner import INTERVALS

    app = open(os.path.join(ROOT, "app.js"), encoding="utf-8").read()
    m = re.search(r"BOX_DAYS\s*=\s*\{([^}]*)\}", app)
    assert m, "BOX_DAYS tidak ditemukan di app.js"
    web = {int(k): int(v) for k, v in re.findall(r"(\d+)\s*:\s*(\d+)", m.group(1))}
    assert web == INTERVALS, f"jadwal web {web} berbeda dari terminal {INTERVALS}"


def test_app_js_tidak_menimpa_class_body():
    """Mengganti tema tidak boleh menghapus kelas lain pada <body>.

    Menetapkan document.body.className akan menimpa SELURUH daftar kelas.
    Penggantian tema harus memakai classList supaya hanya kelas tema yang
    disentuh.
    """
    app = open(os.path.join(ROOT, "app.js"), encoding="utf-8").read()
    penimpaan = re.search(r"document\.body\.className\s*=", app)
    assert not penimpaan, (
        "app.js menimpa document.body.className; pakai classList.add/remove"
    )


def test_app_js_memvalidasi_nama_tema():
    """Nama tema dari localStorage harus disaring sebelum dipakai.

    Nilai yang rusak pernah menghasilkan class="theme-[object Object]":
    tidak ada tema yang sah, tidak ada tombol tema yang tampak aktif, dan
    nilai rusaknya ditulis balik sehingga menetap.
    """
    app = open(os.path.join(ROOT, "app.js"), encoding="utf-8").read()
    assert "THEMES" in app, "daftar tema yang dikenal tidak ada di app.js"
    assert re.search(r"THEMES\.includes\(\s*name\s*\)", app), (
        "setTheme tidak memeriksa apakah nama tema dikenal"
    )
    # Setiap tema di CSS harus terdaftar di app.js, dan sebaliknya.
    css = open(os.path.join(ROOT, "style.css"), encoding="utf-8").read()
    dari_css = set(re.findall(r"body\.theme-([a-z]+)", css))
    daftar = re.search(r"const THEMES = \[([^\]]*)\]", app).group(1)
    dari_app = set(re.findall(r'"([a-z]+)"', daftar))
    html = open(os.path.join(ROOT, "index.html"), encoding="utf-8").read()
    dari_html = set(re.findall(r'data-theme="([a-z]+)"', html))
    bawaan = dari_app - dari_css          # tema bawaan didefinisikan di :root
    assert len(bawaan) <= 1, f"lebih dari satu tema tanpa aturan CSS: {bawaan}"
    assert dari_css <= dari_app, f"tema di CSS tidak terdaftar di app.js: {dari_css - dari_app}"
    assert dari_html == dari_app, (
        f"tombol tema di HTML tidak cocok dengan THEMES: {dari_html} vs {dari_app}"
    )
