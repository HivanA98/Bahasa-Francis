# anki/ — ekspor untuk Anki

Berkas di folder ini **dibuat ulang** oleh `tools/build_exports.py` dari
`data/*.json`. Jangan menyuntingnya langsung; sunting datanya lalu jalankan:

```bash
python tools/build_exports.py
```

## Berkas

| Berkas | Jumlah kartu | Isi |
|:-------|-------------:|:----|
| `kosakata.csv` | 159 | Modul 1: kosakata inti |
| `tatabahasa.csv` | 60 | Modul 2: soal tata bahasa |
| `konjugasi.csv` | 30 | Modul 3: tabel konjugasi présent |
| `pelafalan.csv` | 28 | Modul 4: teks berlafal dan aturan ejaan |
| `serapan.csv` | 32 | Modul 5: kata serapan dan faux-amis |

## Pemetaan kolom

Kolom terakhir setiap berkas selalu **Tags**.

### `kosakata.csv` — 8 field

| Kolom | Isi | Saran field |
|------:|:----|:------------|
| 1 | kata beserta artikelnya (`le livre`) | Front |
| 2 | arti Bahasa Indonesia | Back |
| 3 | lafal: `/livʁ/ (livr)` | Lafal |
| 4 | kelas kata, gender, jamak | Keterangan |
| 5 | contoh kalimat Prancis | Contoh |
| 6 | arti contoh kalimat | ContohArti |
| 7 | catatan pemakaian | Catatan |
| 8 | tag | Tags |

### `tatabahasa.csv` — 5 field

| Kolom | Isi | Saran field |
|------:|:----|:------------|
| 1 | pertanyaan (memakai `<br>` bila ada contoh Prancis) | Front |
| 2 | jawaban benar | Back |
| 3 | penjelasan | Penjelasan |
| 4 | nama topik | Topik |
| 5 | tag | Tags |

### `konjugasi.csv` — 7 field

| Kolom | Isi | Saran field |
|------:|:----|:------------|
| 1 | infinitif | Front |
| 2 | tabel enam baris (dipisah `<br>`) | Back |
| 3 | arti | Arti |
| 4 | lafal infinitif | Lafal |
| 5 | `avoir + mangé` (bekal passé composé) | PasseCompose |
| 6 | catatan ketidakberaturan | Catatan |
| 7 | tag | Tags |

### `pelafalan.csv` — 5 field

| Kolom | Isi | Saran field |
|------:|:----|:------------|
| 1 | teks Prancis, atau gabungan huruf + nama aturan | Front |
| 2 | lafalnya, atau penjelasan aturannya | Back |
| 3 | arti, atau contoh-contohnya | Keterangan |
| 4 | catatan | Catatan |
| 5 | tag | Tags |

### `serapan.csv` — 6 field

| Kolom | Isi | Saran field |
|------:|:----|:------------|
| 1 | kata Prancis | Front |
| 2 | arti sebenarnya dalam Bahasa Prancis | Back |
| 3 | lafal | Lafal |
| 4 | bentuk mirip dalam Bahasa Indonesia atau Inggris | Mirip |
| 5 | pergeseran artinya | Pergeseran |
| 6 | tag | Tags |

## Cara impor

1. Anki: **File → Import**, pilih berkasnya.
2. Pilih jenis catatan (note type) yang jumlah fieldnya cukup — lihat tabel di
   atas.
3. Petakan setiap kolom ke field sesuai tabel. Kolom terakhir adalah **Tags**.
4. Pastikan "Allow HTML in fields" **dinyalakan** untuk `tatabahasa.csv` dan
   `konjugasi.csv` yang memakai `<br>`, dan boleh dimatikan untuk berkas lain.

Tiga baris pertama setiap berkas adalah pengarah untuk Anki 2.1.55 ke atas:

```
#separator:Comma
#html:false
#tags column:N
```

Anki versi tersebut dan yang lebih baru membaca pengarah itu, lalu langsung
memakai pemisah serta kolom tag yang benar. Bila Anki Anda lebih tua dan
menolak berkasnya, **hapus tiga baris itu** lalu atur pemisah dan kolom tag
secara manual di jendela impor.

## Tag

Setiap kartu membawa tiga tag: modulnya, kategorinya, dan tahapnya.

```
prancis::kosakata prancis::nourriture prancis::tahap4
prancis::konjugasi prancis::irregulier prancis::tahap1
```

Dengan begitu Anda bisa membuat subdeck atau saringan per tahap, misalnya
`tag:prancis::tahap1 OR tag:prancis::tahap2`.
