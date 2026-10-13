# Yang masih perlu ditinjau manusia

Pengujian otomatis di `tests/` memeriksa **bentuk** data: lambang IPA yang
sah, artikel yang sejalan dengan gender, tabel konjugasi yang sesuai
aturannya, kunci jawaban yang tidak menyimpang dari sumbernya. Pengujian itu
**tidak bisa** memeriksa apakah isinya benar sebagai bahasa.

Daftar di bawah adalah hal-hal yang sebaiknya diperiksa dengan kamus rujukan
(Larousse, Le Robert, Wiktionnaire) atau dengan pengajar, sebelum dihafalkan.

## 1. Lafal (IPA)

IPA di materi ini adalah lafal baku (français standard) sebuah kata ketika
diucapkan **sendiri**, mengikuti lafal acuan kamus.

- **Vokal sengau /œ̃/.** Materi ini membedakan `un` /œ̃/ dari `pain` /ɛ̃/.
  Banyak penutur Prancis utara, termasuk Paris, sudah melebur keduanya menjadi
  /ɛ̃/. Keduanya diterima; kamus masih mencatat /œ̃/.
- **Pasangan /e/ dan /ɛ/ di akhir kata.** Pembedaan `sait` /sɛ/ dan `ses` /se/
  tidak lagi dipertahankan oleh semua penutur. Soal homofon di materi ini
  sengaja hanya memakai kata yang lafalnya disepakati.
- **Bunyi /ə/.** Materi menuliskannya (`je` /ʒə/, `samedi` /samdi/) sesuai
  lafal hati-hati. Dalam percakapan sebenarnya, bunyi itu sering hilang —
  dibahas pada aturan p18.
- **Lafal di dalam kalimat.** Contoh kalimat sengaja TIDAK diberi IPA, karena
  satu kalimat punya beberapa lafal yang sama-sama benar bergantung kecepatan
  bicara dan pilihan liaison.

## 2. Gender kata benda

Gender setiap kata benda ditulis berdasarkan kamus, tetapi tidak ada mesin
yang bisa memverifikasinya. Yang diperiksa pengujian hanyalah bahwa artikelnya
(le/la/l') sejalan dengan gender yang tertulis dan dengan bunyi awal katanya.

Kata yang gendernya layak diperiksa ulang karena sering tertukar:

- `livre` — maskulin (buku), tetapi ada `la livre` (setengah kilogram).
- `légume`, `musée` — maskulin walaupun berakhiran -e dan -ée.
- `eau` — feminin walaupun tidak berakhiran -e.
- `enfant` — bisa maskulin atau feminin mengikuti anaknya.
- `après-midi` — umumnya maskulin; bentuk feminin masih tercatat di sebagian
  kamus sebagai varian lama.

## 3. Bentuk jamak dan feminin yang menyimpang

Setiap bentuk yang berbeda dari aturan mesin wajib memuat `morpho_note`.
Bentuk-bentuk berikut sengaja ditulis menyimpang:

| Kata | Bentuk | Alasan yang dicatat |
|:-----|:-------|:--------------------|
| `monsieur` | messieurs | dahulu dua kata: mon + sieur |
| `madame` | mesdames | dahulu dua kata: ma + dame |
| `grand-père` | grands-pères | kedua bagian ikut berjamak |
| `grand-mère` | grands-mères | grand tidak menjadi grande |
| `après-midi` | après-midi | bentuk baku; `après-midis` juga diterima sejak 1990 |
| `fils`, `riz`, `bus`, `mois` | tidak berubah | sudah berakhiran -s atau -z |
| `blanc` | blanche | c berubah menjadi ch |
| `un` | une | satu-satunya angka yang bergender |

Yang perlu ditinjau: apakah `grands-mères` atau `grand-mères` yang sebaiknya
diajarkan lebih dahulu. Kamus mencatat keduanya; materi ini memilih bentuk
baku yang lama.

## 4. Konjugasi

Tabel kata kerja beraturan dibandingkan dengan mesin, sehingga tidak mungkin
salah taip. Yang perlu ditinjau manusia:

- Penggolongan `partir` dan `venir` sebagai kelompok 3, bukan kelompok 2.
  Penggolongan ini baku, tetapi sebagian buku memakai istilah berbeda.
- Kata kerja -er yang ejaannya berubah (manger, commencer, acheter, préférer,
  appeler) ditampilkan sebagai kelompok tersendiri dalam daftar, walaupun
  field `groupe`-nya tetap 1 sebagaimana tata bahasa Prancis menggolongkannya.
  Pemisahan itu hanya untuk keperluan latihan, dan dinyatakan di dalam
  penjelasan kelompoknya.
- Daftar kata kerja ber-auxiliaire être pada passé composé disebutkan sebagai
  "sekelompok kecil kata kerja perpindahan". Daftar lengkapnya lebih rumit
  (termasuk kata kerja pronominal), dan itu di luar tingkat A1.

## 5. Kata serapan dan jalur masuknya

Modul 5 menyebut 22 kata Prancis yang bentuknya dikenal dalam Bahasa
Indonesia. **Jalur masuknya tidak diklaim secara rinci.** Sebagian besar
diperkirakan masuk melalui Bahasa Belanda pada masa kolonial, dan untuk
beberapa kata jalurnya masih diperdebatkan atau bisa lebih dari satu:

- `sopir` — dari `chauffeur`, kemungkinan besar lewat Belanda `chauffeur`.
- `montir` — dari `monteur`, lewat Belanda `monteur`.
- `insinyur` — dari `ingénieur`, lewat Belanda `ingenieur`.
- `etalase` — dari `étalage`, lewat Belanda `etalage`.
- `kroket`, `omelet`, `mayones`, `saus` — nama makanan yang bisa masuk lewat
  Belanda maupun langsung.
- `balon`, `kupon`, `salon`, `biro` — bentuknya sama dalam Belanda dan
  Prancis, sehingga jalurnya tidak bisa dipastikan dari bentuknya saja.

Yang **dipakai** dalam materi ini hanyalah kemiripan bentuknya sebagai alat
bantu ingat, bukan klaim etimologi. Bila Anda memerlukan etimologi yang
tepercaya, rujuklah Kamus Besar Bahasa Indonesia dan kamus etimologi.

## 6. Nada dan pilihan kata dalam Bahasa Indonesia

Penjelasan ditulis dalam Bahasa Indonesia baku. Beberapa pilihan yang bisa
diperdebatkan:

- Istilah tata bahasa dibiarkan dalam Bahasa Prancis (artikel takrif,
  partitif, liaison, elisi, participe passé) dengan penjelasan Indonesia,
  bukan diterjemahkan paksa.
- "Ejaan bantu" dipakai, bukan "transliterasi", karena yang dihasilkan bukan
  alih aksara melainkan pendekatan bunyi.
- Nama bahasa ditulis "Bahasa Prancis" sesuai KBBI, bukan "Perancis" maupun
  "Francis" — walaupun nama folder repositori ini memakai ejaan lain.
