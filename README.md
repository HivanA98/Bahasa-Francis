# Latihan Bahasa Prancis (A1)

Bahan latihan Bahasa Prancis untuk pelajar penutur Bahasa Indonesia yang
**mulai dari nol**: belum pernah belajar Bahasa Prancis sama sekali.

Materi ini berangkat dari tiga hal yang paling sering membuat penutur Bahasa
Indonesia tersandung, dan ketiganya tidak ada padanannya dalam Bahasa
Indonesia:

1. **Tulisan tidak sama dengan bunyi.** `beaucoup` dibaca /boku/, `petit`
   dibaca /pəti/. Karena itu setiap kata di sini membawa lafal IPA sekaligus
   ejaan bantu berbahasa Indonesia.
2. **Setiap kata benda bergender.** `le livre` tetapi `la table`, dan gender
   itu merembet ke artikel, kata sifat, serta kata milik.
3. **Kata kerja berubah mengikuti pelakunya.** Satu kata "makan" dalam Bahasa
   Indonesia menjadi enam bentuk dalam Bahasa Prancis.

Sasarannya tingkat A1 (pemula) menuju A2.

| | |
|:--|:--|
| Kosakata | 159 kata, 6 tahap, semuanya berlafal IPA |
| Gender dan artikel | 76 kata benda, soal dibuat otomatis dari data |
| Topik tata bahasa | 12 topik, 60 soal |
| Konjugasi présent | 30 kata kerja, 4 kelompok, 16 soal + soal buatan otomatis |
| Pelafalan | 18 aturan ejaan, 33 soal, 10 teks untuk dibaca |
| Serapan dan faux-amis | 32 kata, 10 soal |
| Total kartu | 318 |
| Lembar kerja tertulis | 12 lembar + 12 kunci jawaban |
| Pengujian otomatis | 344 |

## Dua cara memakai

### 1. Aplikasi kartu di browser

Buka `index.html` — tidak perlu memasang apa pun. Bila repositori ini
diterbitkan lewat GitHub Pages, alamatnya menjadi
<https://hivana98.github.io/Bahasa-Francis/>.

Lima modul dalam bentuk kartu bolak-balik: kosakata (dua arah, dengan atau
tanpa artikel), tata bahasa (pilihan ganda), konjugasi (tabel enam baris),
pelafalan, serta kata serapan dan faux-amis. Sakelar "Sembunyikan artikel"
mengubah kartu kosakata mana pun menjadi latihan gender. Progres memakai lima
kotak Leitner yang sama dengan versi terminal dan tersimpan di `localStorage`
peramban Anda sendiri.

Pintasan papan ketik: `Spasi` balik kartu · `←` `→` navigasi · `1`–`4` pilih
jawaban · `H` sudah hafal · `B` belum hafal · `S` acak · `L` tampilkan atau
sembunyikan lafal · `/` cari.

Untuk menjalankannya di komputer sendiri, cukup peladen statis apa pun:

```bash
python -m http.server 8766
```

lalu buka <http://localhost:8766>. Berkas `index.html` juga bisa dibuka
langsung (`file://`) karena datanya dimuat lewat tag `<script>`, bukan
`fetch()`.

### 2. Latihan di terminal

`python quiz.py` memberi hal yang tidak ada di versi web: jawaban yang
**ditulis sendiri** (arti kata dan bentuk konjugasi), sesi berbatas waktu,
interleaving antar modul, pembatasan materi baru per sesi, dan pengenalan
materi menurut urutan tahap.

Progres kedua versi terpisah: aplikasi web memakai `localStorage`, versi
terminal memakai `progress.json`. Keduanya tidak saling tahu, jadi pilih salah
satu untuk materi yang sama.

## Yang TIDAK ada di sini

- **Tidak ada rekaman suara.** Lafal ditulis dengan IPA dan ejaan bantu. Untuk
  tiga bunyi yang tidak ada dalam Bahasa Indonesia — /y/ pada `tu`, /ø œ/ pada
  `deux`, dan /ʁ/ pada `rue` — tulisan tidak bisa menggantikan telinga.
  Dengarkanlah penutur asli untuk ketiganya.
- **Tidak ada terjemahan kalimat panjang.** Semua contoh adalah kalimat
  tingkat A1 yang bisa dipakai langsung.
- **Tidak ada dialek dan tidak ada bahasa gaul.** Hanya français standard,
  yaitu ragam yang diajarkan di kelas bahasa dan dipakai dalam tulisan.
- **Tidak ada tingkat B1 ke atas.** Imparfait, futur simple, subjonctif, dan
  kata ganti objek sengaja ditinggalkan.
- **Tidak ada janji hasil.** Kecepatan belajar setiap orang berbeda-beda.

## Persyaratan

Python 3.10 atau lebih baru. Tidak ada pustaka pihak ketiga yang perlu
dipasang untuk menjalankan latihannya; `pytest` hanya diperlukan untuk
menjalankan pengujian.

Terminal Anda perlu bisa menampilkan huruf beraksen dan lambang IPA. Di
Windows, Windows Terminal menampilkannya jauh lebih baik daripada `cmd.exe`
lama.

## Mulai cepat

```bash
python quiz.py
```

Sesi bawaan: 20 menit, campuran semua mode, 8 kartu baru. Progres tersimpan di
`progress.json`.

```bash
python quiz.py --stats
```

## Bendera baris perintah

| Bendera | Arti |
|:--------|:-----|
| `--mode MODE` | Batasi mode. Boleh diulang atau dipisah koma. Bawaan: semua. |
| `--stage N` | Batasi materi sampai tahap N (1-6). |
| `--minutes M` | Lama sesi dalam menit (bawaan 20). Sesi berhenti saat waktunya habis. |
| `--limit N` | Batas jumlah soal dalam satu sesi. |
| `--new N` | Kartu baru per sesi (bawaan 8). `--new 0` berarti hanya mengulang. |
| `--no-lafal` | Sembunyikan lafal IPA dan ejaan bantu. |
| `--seed N` | Nilai awal pengacak, untuk mengulang susunan sesi yang sama. |
| `--progress BERKAS` | Lokasi berkas progres selain `progress.json`. |
| `--stats` | Tampilkan ringkasan kemajuan lalu keluar. |
| `--reset` | Hapus berkas progres (meminta konfirmasi). |
| `--no-color` | Matikan warna. |

Mode yang tersedia:

| Mode | Isi |
|:-----|:----|
| `kosakata-fr` | Prancis ke Indonesia. Jawaban **ditulis** (bukan pilihan ganda). |
| `kosakata-id` | Indonesia ke Prancis. Pilihan ganda. |
| `genre` | Artikel takrif: le, la, atau l'. Soal dibuat otomatis dari data. |
| `tatabahasa` | Soal tata bahasa dan catatan kata serapan. |
| `konjugasi` | Tabel konjugasi: ditulis sendiri dan pilihan ganda. |
| `pelafalan` | Lafal, kata berbunyi sama, liaison, elisi, dan membaca teks. |

Di dalam sesi: ketik nomor untuk pilihan ganda, `l` untuk melewati, `k` untuk
keluar, `?` untuk melihat jawaban pada soal yang jawabannya ditulis (dihitung
salah).

Jawaban berbahasa Prancis **dinilai tanpa memperhatikan aksen, tanda kutip,
dan spasi**: `j'ai`, `jai`, dan `J AI` sama-sama diterima. Alasannya, menaip
aksen di papan ketik Indonesia menyulitkan, sedangkan yang dilatih di sini
adalah bentuk katanya. Jawaban yang benar tetap ditampilkan dengan aksennya.

## Isi materi

### Modul 1 — Kosakata inti (`data/kosakata.json`)

159 kata dalam 6 tahap: sapaan, kata ganti, angka 0-10, keluarga, benda
sehari-hari, warna, makanan, tempat dan kendaraan, waktu, kata kerja, kata
sifat, dan kata tugas.

Setiap entri memuat: kata seperti di kamus, lafal IPA, arti Indonesia, kelas
kata, gender dan artikel (untuk kata benda), bentuk jamak, bentuk feminin
(untuk kata sifat), satu contoh kalimat tingkat A1, dan catatan pemakaian.

**Ejaan bantu tidak ditulis tangan.** Ia dihitung dari IPA oleh
`frdrill/phonetique.py`, sehingga tidak mungkin berbeda-beda gayanya antar
entri. Skemanya:

| Ejaan bantu | Bunyi | Keterangan |
|:------------|:------|:-----------|
| `ü` | /y/ | bibir seperti "u", lidah seperti "i" — `tu` menjadi `tü` |
| `ö` | /ø œ/ | bibir seperti "o", lidah seperti "e" — `deux` menjadi `dö` |
| `ë` | /ə/ | e pepet, seperti "e" pada "besar" |
| `é` `è` | /e/ /ɛ/ | e tertutup dan e terbuka, seperti "sate" dan "nenek" |
| `ang` `eng` `ong` `ung` | /ɑ̃ ɛ̃ ɔ̃ œ̃/ | vokal sengau; "ng" hanya penanda, tidak dibunyikan |
| `zh` | /ʒ/ | tidak ada dalam Bahasa Indonesia — `jour` menjadi `zhur` |
| `sy` | /ʃ/ | seperti "sy" pada "syukur" |
| `r` | /ʁ/ | digetarkan di tenggorokan, bukan di ujung lidah |

### Modul 2 — Tata bahasa dasar (`data/tatabahasa.json`)

| Topik | Isi |
|:------|:----|
| g01 | Gender kata benda: maskulin dan feminin |
| g02 | Artikel takrif: le, la, l', les |
| g03 | Artikel tak takrif: un, une, des |
| g04 | Jamak: ditulis tetapi tidak dibunyikan |
| g05 | Kata ganti pelaku dan pilihan tu atau vous |
| g06 | Negasi: ne ... pas mengapit kata kerja |
| g07 | Tiga cara bertanya |
| g08 | Artikel partitif: du, de la, des |
| g09 | Kata sifat: menyesuaikan diri dan sebagian mendahului |
| g10 | Kata milik: mengikuti barangnya, bukan pemiliknya |
| g11 | Kata depan yang melebur: au, aux, du, des |
| g12 | Kemarin dan besok: passé composé dan futur proche |

Setiap topik memiliki field `caveats` yang memuat pengecualian dan batas
berlakunya aturan. Hal-hal itu sengaja ditulis sebagai catatan, bukan sebagai
aturan mutlak.

### Modul 3 — Konjugasi présent (`data/konjugasi.json`)

30 kata kerja dalam empat kelompok: `-er` beraturan, `-ir` dengan sisipan
`-iss-`, `-re` beraturan, dan kata kerja tak beraturan (être, avoir, aller,
faire, prendre, venir, pouvoir, vouloir, savoir, dire, boire, partir,
comprendre). Ditambah lima kata kerja `-er` yang ejaannya berubah
(manger, commencer, acheter, préférer, appeler).

Tabel konjugasi kata kerja beraturan **dibandingkan dengan mesin** di
`frdrill/conjugaison.py` oleh pengujian otomatis. Bila tabel di data berbeda
dari aturannya, pengujian gagal. Kata kerja tak beraturan wajib memuat catatan
yang menjelaskan ketidakberaturannya — sehingga tidak ada bentuk aneh yang
masuk diam-diam karena salah taip.

Soal "apa bentuk X untuk Y" **dibuat otomatis** dari tabel itu, dan pengecohnya
diambil dari baris lain kata kerja yang sama — karena kesalahan nyata memang
terjadi antar baris, bukan antar kata kerja.

### Modul 4 — Pelafalan (`data/pelafalan.json`)

Keterampilan penghubung menuju bahasa lisan: dari tulisan Prancis ke bunyinya.

18 aturan ejaan (konsonan akhir yang diam, vokal sengau, `u` lawan `ou`,
gabungan huruf, `c` dan `g` keras atau lembut, `h` yang tidak pernah
dibunyikan, `ill`, liaison, elisi, dan `e` yang hilang dalam percakapan),
33 soal dalam lima jenis, serta 10 teks pendek untuk dibaca sendiri.

| Jenis soal | Isi | Pengaman kuncinya |
|:-----------|:----|:------------------|
| `lafal` | Pilih IPA yang tepat untuk sebuah kata | Kunci wajib sama dengan field `ipa` |
| `homophone` | Pilih ejaan yang berarti X | Semua pilihan wajib berlafal sama persis |
| `graphie` | Gabungan huruf mana yang berbunyi X | Kunci wajib tercantum pada aturan yang dirujuk |
| `liaison` | Wajib, boleh, atau terlarang | Kunci wajib sesuai field `liaison_type` |
| `elision` | Gabungkan dua kata | Kunci dihitung mesin, tidak ditulis di data |

Soal homofon tidak bisa dijawab dari bunyinya, karena semua pilihannya memang
berbunyi sama (`vert`, `verre`, `vers`, `ver` semuanya /vɛʁ/). Hal ini diuji
otomatis.

### Modul 5 — Serapan dan faux-amis (`data/serapan.json`)

Catatan pendek, bukan latihan utama. Memuat 22 kata Prancis yang bentuknya
sudah dikenal dalam Bahasa Indonesia (restoran, biro, butik, garasi, bagasi,
sopir, trotoar, kupon, parfum, amatir, insinyur, salon, etalase, mayones,
kroket, omelet, saus, kudeta, balon, toilet, montir, kafe) dan 10 faux-amis
yang menjebak (librairie, journal, actuellement, éventuellement, sympathique,
assister, demander, rester, coin, pain).

Hampir separuh kata serapan itu sudah **bergeser artinya**: `salon` berarti
ruang tamu, `bureau` berarti kantor, `ballon` berarti bola. Modul ini memakai
kosakata yang sudah Anda miliki, sekaligus menandai di mana modal itu
menyesatkan.

Jalur masuk kata-kata itu ke Bahasa Indonesia — umumnya melalui Bahasa
Belanda — tidak diklaim secara rinci; lihat `data/NEEDS_REVIEW.md`.

## Cara kerja penjadwalan

Lima kotak Leitner. Jawaban benar menaikkan kartu satu kotak, jawaban salah
mengembalikannya ke kotak 1.

| Kotak | Jeda sebelum diulang |
|------:|---------------------:|
| 1 | hari itu juga |
| 2 | 1 hari |
| 3 | 3 hari |
| 4 | 7 hari |
| 5 | 16 hari |

Angka-angka itu adalah pilihan praktis yang lazim dipakai pada kartu Leitner,
**bukan hasil pengukuran**. Ubah `INTERVALS` di `frdrill/leitner.py` bila
jadwal lain lebih cocok — dan ubah juga `BOX_DAYS` di `app.js` agar versi web
sejalan. Pengujian memeriksa keduanya tetap sama.

Empat hal lain yang diterapkan penjadwal:

- **Ulangan didahulukan.** Selama masih ada kartu jatuh tempo, materi baru
  dibatasi paling banyak 45% dari satu sesi. Tanpa pembatasan ini materi baru
  memakan seluruh sesi dan kartu lama tidak pernah naik kotak.
- **Interleaving.** Soal dari mode berbeda disilang bergantian, dan materi lama
  disisipkan di antara materi baru kira-kira 2 lama : 1 baru. Mencampur materi
  umumnya menghasilkan ingatan yang lebih tahan lama daripada mengerjakan satu
  blok materi sejenis berturut-turut, meski terasa lebih sulit saat dikerjakan.
- **Materi baru masuk menurut urutan tahap**, bukan acak dari seluruh materi,
  walaupun `--stage` tidak diberikan.
- **Satu kata, beberapa arah.** Jatah kartu baru dibagi per kelompok materi,
  bukan per mode. Satu kata baru lalu dilatih sebagai arti, sebagai kata
  Prancis, dan sebagai gender — bukan tiga kata berbeda.

## Jadwal 6 minggu

Dengan pengaturan bawaan (20 menit per sesi, 8 kartu baru, 5 sesi per minggu),
penjadwal memperkenalkan **kira-kira 20 kartu baru per minggu**, yang terbagi
menjadi sekitar 10 kata baru ditambah soal tata bahasa, konjugasi, dan
pelafalan.

| Minggu | Kosakata (kumulatif) | Tahap | Tata bahasa | Konjugasi | Pelafalan |
|-------:|---------------------:|:------|:------------|:----------|:----------|
| 1 | 10 | tahap 1 | g01, g02 | être, avoir, parler | konsonan akhir, huruf e |
| 2 | 20 | tahap 1 selesai | g03, g04 | aller, habiter, aimer | vokal sengau |
| 3 | 30 | tahap 2 | g05, g06 | manger, regarder | u lawan ou, elisi |
| 4 | 40 | tahap 2-3 | g07, g08 | finir, choisir, faire | gabungan huruf, c dan g |
| 5 | 50 | tahap 3 | g09, g10 | vendre, prendre, venir | ill, liaison |
| 6 | 60 | tahap 3-4 | g11, g12 | pouvoir, vouloir, boire | liaison terlarang, e yang hilang |

Pada akhir minggu ke-6 dengan pengaturan bawaan, **seluruh 12 topik tata
bahasa sudah diperkenalkan**, sedangkan kosakata mencapai sekitar 60 dari 159
kata. Menyelesaikan seluruh 318 kartu pada kecepatan yang sama memerlukan
sekitar **16 minggu** (kira-kira 80 sesi).

Bila Anda ingin lebih cepat, naikkan `--new` ke sekitar 14 — tetapi beban
ulangannya ikut naik dan sesi 20 menit menjadi tidak cukup.

### Dari mana angka-angka itu

Angka di tabel berasal dari **cara kerja penjadwal**, bukan dari pengamatan
pembelajar nyata: jatah 8 kartu baru per sesi dibagi empat kelompok materi
dengan bobot 3:1:1:1, lalu dikalikan lima sesi per minggu. Kecepatan setiap
orang berbeda, dan tidak ada yang menjamin angka ini berlaku untuk Anda.

### Bila tunggakan menumpuk

Bila `--stats` menunjukkan kartu jatuh tempo jauh lebih banyak daripada yang
bisa Anda kerjakan:

```bash
python quiz.py --new 0            # satu sesi khusus mengulang, tanpa materi baru
python quiz.py --new 4            # perlambat laju materi baru
python quiz.py --minutes 30       # sesi lebih panjang
```

Memperlambat materi baru lebih baik daripada menumpuk kartu yang tidak pernah
diulang.

## Lembar kerja

12 lembar kerja Markdown di `worksheets/`, dua lembar per tahap, dengan kunci
jawaban **terpisah** di `worksheets/answers/`. Setiap lembar memuat enam
bagian: arti kata, menulis kata Prancis, artikel dan jamak, tabel konjugasi,
tata bahasa, dan pelafalan.

Lembar kerja dibuat dari data oleh skrip, bukan ditulis tangan, sehingga
kuncinya selalu sejalan dengan datanya. Jangan menyuntingnya langsung.

```bash
python tools/build_worksheets.py
```

## Anki

Ekspor CSV untuk Anki ada di `anki/`, beserta pemetaan kolom ke field di
`anki/README.md`.

```bash
python tools/build_exports.py
```

Catatan: bila Anda memakai Anki, pakailah penjadwalan Anki dan jangan
menjalankan `quiz.py` untuk materi yang sama. `progress.json` dan koleksi Anki
tidak saling tahu, sehingga satu kartu akan dijadwalkan oleh dua sistem
sekaligus.

## Pengujian

```bash
python -m pytest
```

344 pengujian. Yang diperiksa:

| Berkas | Isi |
|:-------|:----|
| `test_schema.py` | Id unik di seluruh modul, format id, tidak ada field kosong, kelas kata dan gender sah, kata benda bergender dan berartikel, kata sifat berbentuk feminin, setiap tahap dan setiap jenis soal terisi. |
| `test_phonetique.py` | IPA hanya memakai fonem Bahasa Prancis, teks Prancis hanya memakai huruf Prancis, bentuk NFC, setiap fonem yang dipakai dijelaskan di skema lafal, ejaan bantu pada kasus patokan, pemenggalan suku kata tidak kehilangan fonem. |
| `test_morphologie.py` | Artikel, bentuk jamak, dan bentuk feminin di data dibandingkan dengan aturan; penyimpangan wajib memiliki catatan. |
| `test_konjugasi.py` | Tabel kata kerja beraturan sama dengan hasil mesin, kata kerja tak beraturan wajib bercatatan, model sejalan dengan infinitif dan kelompoknya, elisi dan negasi. |
| `test_keys.py` | Setiap soal memiliki tepat satu jawaban benar, tidak ada pilihan kembar, semua pilihan homofon berlafal sama, kunci soal lafal sama dengan field IPA, kunci graphie ada pada aturannya, pengecoh soal buatan otomatis tidak ikut benar. |
| `test_leitner.py` | Kenaikan dan penurunan kotak, jeda sesuai tabel, jatuh tempo, simpan dan muat ulang, berkas rusak tidak merusak pemuatan, penulisan atomik. |
| `test_session.py` | Batas kartu baru, ulangan tidak tergeser habis oleh materi baru, kartu belum jatuh tempo tidak muncul, interleaving mencampur mode, materi baru masuk menurut urutan tahap, sesi dapat diulang dengan seed sama. |
| `test_exports.py` | Semua hasil ekspor mutakhir terhadap data (CSV, Anki, lembar kerja, dan `webdata.js`), kolom kunci sesuai, format Anki benar, ejaan bantu di web dihitung dari IPA, aplikasi web tidak memakai `fetch()`, dan jadwal Leitner web sama dengan terminal. |
| `test_worksheets.py` | Kunci berada di berkas terpisah, semua bagian ada, tabel konjugasi kosong di soal dan terisi di kunci, dan setiap butir berasal dari data pada tahap yang sesuai. |

### Apa yang TIDAK bisa diuji mesin

Pengujian di atas memeriksa **bentuk**, bukan **kebenaran isi bahasa**. Yang
tidak diperiksa mesin:

- Apakah lafal IPA sebuah kata memang benar. Pengujian hanya memeriksa bahwa
  lambangnya sah sebagai fonem Bahasa Prancis.
- Apakah gender sebuah kata benda memang benar. Pengujian memeriksa bahwa
  artikelnya sejalan dengan gender yang tertulis, bukan bahwa gendernya tepat.
- Apakah arti Bahasa Indonesia sudah tepat dan wajar.
- Apakah contoh kalimat terdengar wajar bagi penutur asli.
- Apakah penjelasan tata bahasa tidak menyederhanakan secara menyesatkan.

**Periksalah isinya dengan kamus rujukan atau dengan pengajar** sebelum
menghafalkannya. Hal-hal yang belum diyakini sepenuhnya didaftar di
`data/NEEDS_REVIEW.md`.

## Menyunting data

`data/*.json` adalah **satu-satunya sumber data**. Berkas di `data/csv/`,
`anki/`, `worksheets/`, dan `webdata.js` adalah turunan yang dibuat ulang oleh
skrip.

```bash
# 1. sunting data/kosakata.json (atau modul lain)
python -m pytest                      # 2. pastikan data masih sah
python tools/build_exports.py         # 3. buat ulang CSV dan Anki
python tools/build_worksheets.py      # 4. buat ulang lembar kerja
python tools/build_web.py             # 5. buat ulang data aplikasi web
python -m pytest                      # 6. pastikan semua hasil mutakhir
```

Pengujian `test_exports.py` akan gagal bila data sudah berubah tetapi
ekspornya belum dibuat ulang.

### Aturan penulisan data

| Field | Aturan |
|:------|:-------|
| `fr` dan seluruh teks Prancis | Huruf Latin beraksen saja. Kutip satu ditulis ASCII (`'`), bukan `’`, supaya jawaban yang ditaip pengguna tetap cocok. |
| `ipa` | Tanpa garis miring, hanya fonem Bahasa Prancis, lafal kata ketika diucapkan sendiri. |
| `article`, `pluriel`, `feminin` | Ditulis lengkap walaupun beraturan; pengujian membandingkannya dengan mesin. |
| `morpho_note` | Wajib ada bila bentuknya menyimpang dari aturan. |
| Contoh kalimat | Tingkat A1, dan tanda `?` serta `!` didahului satu spasi sesuai kaidah tipografi Prancis. |

Validator **tidak** menjangkau field prosa (`explanation`, `caveats`, `note`,
`explain`, `ecart`), dan memang seharusnya begitu: field itu memuat kata
Bahasa Indonesia, lambang IPA di tengah kalimat, dan contoh bentuk yang
sengaja salah untuk diperbandingkan. Isi field prosa karena itu perlu ditinjau
manusia.

## Struktur folder

```
index.html            aplikasi kartu di browser (GitHub Pages)
style.css             tiga tema: papier, nuit, lavande
app.js                kartu, saringan, Leitner di localStorage
webdata.js            data aplikasi web (dibuat ulang)
.nojekyll             agar GitHub Pages tidak memproses berkas lewat Jekyll
quiz.py               latihan di terminal
frdrill/              paket inti
  phonetique.py         pemeriksa IPA dan pengubah IPA ke ejaan bantu
  morphologie.py        artikel, bentuk jamak, bentuk feminin
  conjugaison.py        mesin konjugasi présent
  dataio.py             pemuat data dan daftar nilai yang sah
  leitner.py            lima kotak dan jadwalnya
  questions.py          pembuat soal untuk enam mode
  session.py            penyusun sesi: jatah baru, ulangan, interleaving
data/                 sumber data JSON + NEEDS_REVIEW.md
  csv/                  ekspor tabel (dibuat ulang)
anki/                 ekspor Anki (dibuat ulang)
worksheets/           lembar kerja + answers/ (dibuat ulang)
tools/                skrip pembuat ekspor
tests/                344 pengujian
```

## Lisensi

Tidak ada lisensi yang dilampirkan. Materi ini disusun untuk dipakai sendiri.
