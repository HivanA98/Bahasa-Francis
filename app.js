/* ============================================================
   Latihan Bahasa Prancis — app.js

   Data dimuat dari webdata.js (global FR_DATA), bukan lewat fetch(),
   sehingga aplikasi jalan di GitHub Pages maupun saat index.html dibuka
   langsung dari berkas (file://).

   Semua lafal, bentuk berartikel, dan baris konjugasi sudah dihitung oleh
   tools/build_web.py memakai frdrill/, jadi berkas ini hanya menampilkan.

   Penjadwalan memakai lima kotak Leitner, sama seperti quiz.py. Progres
   disimpan di localStorage peramban dan tidak dikirim ke mana pun.
   ============================================================ */

"use strict";

/* ---------------------------------------------------- penyimpanan ---- */

const LS = { prog: "fr.progress.v1", prefs: "fr.prefs.v1", theme: "fr.theme" };

function lsGet(key, fallback) {
  try {
    const raw = localStorage.getItem(key);
    return raw ? JSON.parse(raw) : fallback;
  } catch { return fallback; }
}
function lsSet(key, val) {
  try { localStorage.setItem(key, JSON.stringify(val)); } catch { /* mode privat */ }
}

/* Jeda ulangan per kotak, dalam hari. Sama dengan INTERVALS di
   frdrill/leitner.py; ubah keduanya bila ingin jadwal lain. */
const BOX_DAYS = { 1: 0, 2: 1, 3: 3, 4: 7, 5: 16 };
const MAX_BOX = 5;

const progress = lsGet(LS.prog, { cards: {} });
if (!progress.cards) progress.cards = {};

const prefs = Object.assign(
  { lafal: true, artikel: false, arah: false, due: false, hide: false },
  lsGet(LS.prefs, {})
);

function todayISO() {
  const d = new Date();
  return new Date(d.getTime() - d.getTimezoneOffset() * 60000).toISOString().slice(0, 10);
}
function addDays(iso, n) {
  const d = new Date(iso + "T00:00:00");
  d.setDate(d.getDate() + n);
  return new Date(d.getTime() - d.getTimezoneOffset() * 60000).toISOString().slice(0, 10);
}
function stateOf(id) { return progress.cards[id] || null; }
function boxOf(id) { const s = stateOf(id); return s ? s.box : 0; }
function isDue(id) {
  const s = stateOf(id);
  if (!s) return true;                 // kartu baru selalu dianggap jatuh tempo
  return s.due <= todayISO();
}
function grade(id, ok) {
  const s = stateOf(id) || { box: 1, due: todayISO(), seen: 0, right: 0 };
  s.seen += 1;
  if (ok) { s.right += 1; s.box = Math.min(s.box + 1, MAX_BOX); }
  else { s.box = 1; }
  s.due = addDays(todayISO(), BOX_DAYS[s.box]);
  progress.cards[id] = s;
  lsSet(LS.prog, progress);
}

/* ---------------------------------------------------------- utilitas ---- */

const $ = (sel) => document.querySelector(sel);
const esc = (s) => String(s)
  .replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;")
  .replace(/"/g, "&quot;");

function fr(text, size) {
  return `<div class="fr ${size || "fr-lg"}" lang="fr">${esc(text)}</div>`;
}
/* Lafal selalu dua bagian: IPA untuk ketepatan, ejaan bantu untuk jalan
   masuknya. Keduanya hanya muncul bila sakelar Lafal menyala. */
function lafal(ipa, approx) {
  if (!prefs.lafal || !ipa) return "";
  return `<div class="lafal"><span class="ipa">/${esc(ipa)}/</span>
    <span class="approx">${esc(approx)}</span></div>`;
}
function note(text, cls) {
  return text ? `<div class="note ${cls || ""}">${esc(text)}</div>` : "";
}

/* ----------------------------------------------------- pembuat kartu ---- */

const D = typeof FR_DATA !== "undefined" ? FR_DATA : null;

/* Bentuk tampilan kata benda tanpa artikelnya, dipakai oleh sakelar
   "Sembunyikan artikel" untuk melatih ingatan gender. */
function sansArticle(x) {
  return x.pos === "nom" ? x.fr : x.display;
}

const MODES = {
  kosakata: {
    label: "Kosakata",
    toggles: ["artikel", "arah"],
    items: () => D.kosakata,
    search: (x) => [x.fr, x.display, x.ipa, x.approx, x.gloss, x.detail, x.catLabel]
      .concat(x.alt).join(" "),
    kind: () => "flip",
    front(x) {
      if (prefs.arah) {
        return `<div class="id-xl">${esc(x.gloss)}</div>
                <div class="detail" style="margin-top:8px">${esc(x.posLabel)}</div>`;
      }
      const teks = prefs.artikel ? sansArticle(x) : x.display;
      return fr(teks, "fr-xl") + lafal(x.ipa, x.approx) +
        (prefs.artikel && x.pos === "nom"
          ? `<div class="hint" style="position:static;margin-top:10px">Apa artikelnya: le, la, atau l' ?</div>`
          : "");
    },
    back(x) {
      return `<div class="meaning">${esc(x.gloss)}</div>
        <div class="detail">${esc(x.detail)}</div>
        ${prefs.arah || prefs.artikel ? fr(x.display, "fr-lg") + lafal(x.ipa, x.approx) : ""}
        <hr class="sep" />
        <div class="example">${fr(x.exFr, "fr-md")}
          <div class="gloss">${esc(x.exGloss)}</div></div>
        ${note(x.note)}
        ${note(x.morphoNote, "warn")}`;
    },
  },

  tatabahasa: {
    label: "Tata bahasa",
    toggles: [],
    items: () => D.tatabahasa,
    search: (x) => [x.prompt, x.promptFr, x.catLabel].concat(x.options).join(" "),
    kind: () => "mcq",
    front(x) {
      return `<div class="prompt">${esc(x.prompt)}</div>
        ${x.promptFr ? fr(x.promptFr, "fr-lg") : ""}`;
    },
    back(x) {
      return `<div class="detail">${esc(x.catLabel)}</div>
        <div class="meaning">${x.optionsLang === "fr"
          ? `<span class="fr fr-md" lang="fr">${esc(x.options[x.answer])}</span>`
          : esc(x.options[x.answer])}</div>
        ${note(x.explain)}`;
    },
  },

  konjugasi: {
    label: "Konjugasi",
    toggles: [],
    items: () => D.konjugasi,
    search: (x) => (x.kind === "verbe"
      ? [x.infinitif, x.ipa, x.approx, x.gloss, x.modele, x.catLabel].join(" ")
      : [x.prompt, x.promptFr, x.catLabel].concat(x.options).join(" ")),
    kind: (x) => (x.kind === "soal" ? "mcq" : "flip"),
    front(x) {
      if (x.kind === "soal") {
        return `<div class="prompt">${esc(x.prompt)}</div>
          ${x.promptFr ? fr(x.promptFr, "fr-lg") : ""}`;
      }
      return fr(x.infinitif, "fr-xl") + lafal(x.ipa, x.approx) +
        `<div class="detail" style="margin-top:10px">${esc(x.gloss)}</div>
         <div class="hint" style="position:static">Sebutkan keenam bentuk présent-nya</div>`;
    },
    back(x) {
      if (x.kind === "soal") {
        return `<div class="detail">${esc(x.catLabel)}</div>
          <div class="meaning">${x.optionsLang === "fr"
            ? `<span class="fr fr-md" lang="fr">${esc(x.options[x.answer])}</span>`
            : esc(x.options[x.answer])}</div>
          ${note(x.explain)}`;
      }
      return `<div class="detail">${esc(x.catLabel)}</div>
        <table class="conj">${x.formes.map((f) =>
          `<tr><td>${esc(f.pronom)}</td><td lang="fr">${esc(f.forme)}</td></tr>`).join("")}
        </table>
        <dl class="kv" style="margin-top:12px">
          <dt>Passé composé</dt><dd lang="fr">${esc(x.auxiliaire)} + ${esc(x.participePasse)}</dd>
        </dl>
        <div class="example" style="margin-top:10px">${fr(x.exFr, "fr-md")}
          <div class="gloss">${esc(x.exGloss)}</div></div>
        ${note(x.note, "warn")}
        ${note(x.lafalNote)}`;
    },
  },

  pelafalan: {
    label: "Pelafalan",
    toggles: [],
    items: () => D.pelafalan,
    search: (x) => [x.promptFr || x.fr || "", x.ipa, x.approx, x.gloss, x.catLabel]
      .concat(x.options || []).join(" "),
    /* Soal berpilihan menjadi kartu pilihan ganda; elisi dan teks menjadi
       kartu bolak-balik karena jawabannya ditulis, bukan dipilih. */
    kind: (x) => (x.kind === "soal" && x.type !== "elision" ? "mcq" : "flip"),
    front(x) {
      if (x.kind === "teks") {
        return fr(x.fr, "fr-lg") +
          `<div class="hint" style="position:static;margin-top:10px">Baca dengan suara, lalu buka lafalnya</div>`;
      }
      if (x.type === "elision") {
        return fr(`${x.mots[0]} + ${x.mots[1]}`, "fr-lg") +
          `<div class="detail" style="margin-top:10px">${esc(x.gloss)}</div>
           <div class="hint" style="position:static">Bagaimana keduanya ditulis bila digabung?</div>`;
      }
      if (x.type === "lafal") {
        return fr(x.promptFr, "fr-xl") +
          `<div class="detail" style="margin-top:10px">arti: ${esc(x.gloss)}</div>
           <div class="hint" style="position:static">Pilih lafal yang tepat</div>`;
      }
      if (x.type === "homophone") {
        return `<div class="prompt">Semua pilihan dibunyikan
            <span class="ipa">/${esc(x.ipa)}/</span> (${esc(x.approx)}).<br />
            Mana yang berarti ‘${esc(x.gloss)}’?</div>`;
      }
      if (x.type === "graphie") {
        return `<div class="prompt">Gabungan huruf mana yang dibunyikan
          <span class="ipa">/${esc(x.ipa)}/</span> (${esc(x.approx)})?</div>`;
      }
      return `<div class="prompt">Apakah liaison di antara kedua kata ini wajib,
          boleh, atau terlarang?</div>${fr(x.promptFr, "fr-lg")}`;
    },
    back(x) {
      if (x.kind === "teks") {
        return fr(x.fr, "fr-md") + lafal(x.ipa, x.approx) +
          `<div class="gloss detail" style="margin-top:8px">${esc(x.gloss)}</div>
           ${note(x.explain)}`;
      }
      if (x.type === "elision") {
        return fr(x.reponse, "fr-xl") + lafal(x.ipa, x.approx) + note(x.explain);
      }
      const jawab = x.options[x.answer];
      const isi = x.optionsLang === "ipa"
        ? `<span class="ipa">/${esc(jawab)}/</span> <span class="approx">${esc(x.optionsApprox[x.answer] || "")}</span>`
        : `<span class="fr fr-md" lang="fr">${esc(jawab)}</span>`;
      return `<div class="detail">${esc(x.catLabel)}</div>
        <div class="meaning">${isi}</div>
        ${x.type !== "lafal" && x.ipa ? lafal(x.ipa, x.approx) : ""}
        ${note(x.explain)}`;
    },
  },

  serapan: {
    label: "Serapan & faux-amis",
    toggles: [],
    items: () => D.serapan,
    search: (x) => [x.fr, x.ipa, x.approx, x.indonesien, x.sensFr, x.catLabel].join(" "),
    kind: () => "flip",
    front(x) {
      return fr(x.fr, "fr-xl") + lafal(x.ipa, x.approx) +
        `<div class="hint" style="position:static;margin-top:10px">${
          x.kind === "serapan"
            ? "Kata Indonesia mana yang berkerabat, dan apakah artinya sama?"
            : "Hati-hati: bentuknya menjebak. Apa arti sebenarnya?"
        }</div>`;
    },
    back(x) {
      return `<dl class="kv">
          <dt>Arti Prancis</dt><dd><strong>${esc(x.sensFr)}</strong></dd>
          <dt>Bentuk mirip</dt><dd>${esc(x.indonesien)}</dd>
          ${x.genreLabel ? `<dt>Gender</dt><dd>${esc(x.genreLabel)}</dd>` : ""}
          <dt>Jenis</dt><dd>${esc(x.catLabel)}</dd>
        </dl>
        ${x.ecart ? note(x.ecart, "warn") : note("Artinya sama dalam kedua bahasa.")}
        ${note(x.note)}`;
    },
  },
};

/* ------------------------------------------------------------ keadaan ---- */

let mode = "kosakata";
let deck = [];
let index = 0;
let activeCat = "*";
let activeStage = 0;
let query = "";
let shuffled = false;
let answered = false;

const els = {
  tabs: $("#tabs"), chips: $("#chips"), stages: $("#stages"), search: $("#search"),
  card: $("#card"), badge: $("#badge"), box: $("#box"), front: $("#front"),
  back: $("#back"), choices: $("#choices"), hint: $("#hint"),
  counter: $("#counter"), fill: $("#fill"), grade: $("#grade"),
  stats: $("#stats"), panel: $("#panel"),
};

/* ------------------------------------------------------------ susunan ---- */

function allItems() { return MODES[mode].items(); }

function buildDeck() {
  const cfg = MODES[mode];
  const q = query.trim().toLowerCase();
  deck = allItems().filter((x) => {
    if (activeCat !== "*" && x.cat !== activeCat) return false;
    if (activeStage && x.stage > activeStage) return false;
    if (prefs.due && !isDue(x.id)) return false;
    if (prefs.hide && boxOf(x.id) >= MAX_BOX) return false;
    if (q && !cfg.search(x).toLowerCase().includes(q)) return false;
    return true;
  });
  if (shuffled) {
    for (let i = deck.length - 1; i > 0; i--) {
      const j = Math.floor(Math.random() * (i + 1));
      [deck[i], deck[j]] = [deck[j], deck[i]];
    }
  }
  if (index >= deck.length) index = 0;
}

function renderChips() {
  const seen = new Map();
  for (const x of allItems()) {
    if (activeStage && x.stage > activeStage) continue;
    const prev = seen.get(x.cat) || { label: x.catLabel, n: 0 };
    prev.n += 1;
    seen.set(x.cat, prev);
  }
  const total = allItems().filter((x) => !activeStage || x.stage <= activeStage).length;
  let html = `<button data-cat="*" aria-pressed="${activeCat === "*"}">Semua<span class="n">${total}</span></button>`;
  for (const [cat, info] of seen) {
    html += `<button data-cat="${esc(cat)}" aria-pressed="${activeCat === cat}">${esc(info.label)}<span class="n">${info.n}</span></button>`;
  }
  els.chips.innerHTML = html;
}

function renderToggles() {
  const aktif = MODES[mode].toggles;
  $("#wrap-artikel").hidden = !aktif.includes("artikel");
  $("#wrap-arah").hidden = !aktif.includes("arah");
}

/* ------------------------------------------------------------ tampilan ---- */

function render() {
  const cfg = MODES[mode];
  els.card.classList.remove("is-flipped");
  answered = false;

  if (!deck.length) {
    els.front.innerHTML = `<p class="empty">Tidak ada kartu yang cocok dengan saringan ini.<br />
      Coba hapus pencarian, pilih "Semua tahap", atau matikan "Jatuh tempo saja".</p>`;
    els.back.innerHTML = "";
    els.choices.hidden = true;
    els.grade.hidden = true;
    els.badge.textContent = "";
    els.box.textContent = "";
    els.counter.textContent = "0 / 0";
    els.fill.style.width = "0%";
    els.hint.textContent = "";
    return;
  }

  const x = deck[index];
  const kind = cfg.kind(x);

  els.badge.textContent = `${x.catLabel || ""} · tahap ${x.stage}`;
  const b = boxOf(x.id);
  els.box.textContent = b ? `kotak ${b}${isDue(x.id) ? " · jatuh tempo" : ""}` : "belum dilatih";

  els.front.innerHTML = cfg.front(x);
  els.back.innerHTML = cfg.back(x);

  if (kind === "mcq") {
    els.choices.hidden = false;
    els.choices.innerHTML = x.options.map((o, i) => {
      let isi;
      if (x.optionsLang === "ipa") {
        isi = `<span class="opt-ipa">/${esc(o)}/</span>` +
          (prefs.lafal && x.optionsApprox && x.optionsApprox[i]
            ? ` <span class="opt-approx">${esc(x.optionsApprox[i])}</span>` : "");
      } else if (x.optionsLang === "fr") {
        isi = `<span class="opt-fr" lang="fr">${esc(o)}</span>`;
      } else {
        isi = esc(o);
      }
      return `<button type="button" data-i="${i}"><span class="num">${i + 1}.</span>${isi}</button>`;
    }).join("");
    els.grade.hidden = true;
    els.hint.textContent = "Pilih satu jawaban (tekan 1–4)";
  } else {
    els.choices.hidden = true;
    els.choices.innerHTML = "";
    els.grade.hidden = false;
    els.hint.textContent = "Klik atau tekan Spasi untuk melihat jawaban";
  }

  els.counter.textContent = `${index + 1} / ${deck.length}`;
  els.fill.style.width = `${((index + 1) / deck.length) * 100}%`;
  renderPanel(x);
  fitCard();
}

/* Kedua sisi kartu diposisikan absolut, sehingga tingginya harus dihitung.
   Tanpa ini, kartu pilihan ganda atau tabel konjugasi yang panjang akan
   terpotong. */
function fitCard() {
  els.card.style.height = "auto";
  let h = 0;
  for (const face of els.card.querySelectorAll(".face")) {
    h = Math.max(h, face.scrollHeight);
  }
  // Sisa 4px supaya bilah gulir tidak muncul karena pembulatan.
  els.card.style.height = Math.max(300, h + 4) + "px";
}

function flip() {
  if (!deck.length) return;
  if (MODES[mode].kind(deck[index]) === "mcq" && !answered) return;
  els.card.classList.toggle("is-flipped");
}

function answer(i) {
  if (answered || !deck.length) return;
  const x = deck[index];
  if (MODES[mode].kind(x) !== "mcq") return;
  answered = true;
  const benar = i === x.answer;
  grade(x.id, benar);
  for (const btn of els.choices.querySelectorAll("button")) {
    const bi = Number(btn.dataset.i);
    btn.disabled = true;
    if (bi === x.answer) btn.classList.add("is-right");
    else if (bi === i) btn.classList.add("is-wrong");
  }
  els.hint.textContent = benar ? "Benar. Spasi untuk penjelasan." : "Belum tepat. Spasi untuk penjelasan.";
  const b = boxOf(x.id);
  els.box.textContent = `kotak ${b}`;
  renderStats();
}

function gradeFlip(ok) {
  if (!deck.length) return;
  grade(deck[index].id, ok);
  renderStats();
  next();
}

function next() { if (deck.length) { index = (index + 1) % deck.length; render(); } }
function prev() { if (deck.length) { index = (index - 1 + deck.length) % deck.length; render(); } }

/* -------------------------------------------------------------- panel ---- */

function renderPanel(x) {
  let html = "";
  if (mode === "tatabahasa") {
    const t = D.topik.find((t) => t.id === x.cat);
    if (t) {
      html = `<details open><summary>${esc(t.title)}</summary><div class="body">
        <p>${esc(t.explanation)}</p>
        ${t.examples.map((e) => `<div class="fr fr-sm" lang="fr">${esc(e.fr)}</div>
          <p style="margin-top:0">${esc(e.gloss)}</p>`).join("")}
        <p><strong>Pengecualian dan catatan:</strong></p>
        ${t.caveats.map((c) => `<div class="caveat">${esc(c)}</div>`).join("")}
      </div></details>`;
    } else if (x.cat === "serapan") {
      html = `<details><summary>Tentang modul kata serapan</summary><div class="body">
        ${D.catatan.serapan.map((c) => `<p>${esc(c)}</p>`).join("")}
      </div></details>`;
    }
  } else if (mode === "konjugasi") {
    html = `<details><summary>Empat kelompok kata kerja</summary><div class="body">
      ${D.groupes.map((g) => `<p><strong>${esc(g.nom)}</strong><br />
        <span class="fr fr-sm" lang="fr">${esc(g.terminaisons.join(" · "))}</span><br />
        ${esc(g.explication)}
        ${g.note ? `<br /><span style="opacity:.75">${esc(g.note)}</span>` : ""}</p>`).join("")}
    </div></details>`;
  } else if (mode === "pelafalan") {
    const r = D.regles.find((r) => r.id === x.regle);
    html = r
      ? `<details open><summary>${esc(r.titre)} — ${esc(r.graphies.join(", "))}</summary><div class="body">
          <p>${esc(r.explication)}</p>
          ${r.exemples.map((e) => `<p><span class="fr fr-sm" lang="fr">${esc(e.fr)}</span>
            <span class="ipa">/${esc(e.ipa)}/</span> <em>${esc(e.approx)}</em> — ${esc(e.gloss)}</p>`).join("")}
          ${r.note ? `<div class="caveat">${esc(r.note)}</div>` : ""}
        </div></details>`
      : "";
    html += `<details><summary>Skema ejaan bantu (${D.skema.length} bunyi)</summary><div class="body">
      <table><tr><th>IPA</th><th>Ejaan bantu</th><th>Keterangan</th></tr>
      ${D.skema.map((s) => `<tr><td class="sym">/${esc(s.ipa)}/</td>
        <td class="sym">${esc(s.approx)}</td>
        <td>${esc(s.deskripsi)} <em lang="fr">${esc(s.contoh)}</em></td></tr>`).join("")}
      </table>
      ${D.catatan.pelafalan.map((c) => `<p style="margin-top:10px">${esc(c)}</p>`).join("")}
    </div></details>`;
  } else if (mode === "serapan") {
    html = `<details><summary>Cara memakai modul ini</summary><div class="body">
      ${D.catatan.serapan.map((c) => `<p>${esc(c)}</p>`).join("")}
    </div></details>`;
  } else if (mode === "kosakata") {
    html = `<details><summary>Tentang lafal pada kartu kosakata</summary><div class="body">
      ${D.catatan.kosakata.map((c) => `<p>${esc(c)}</p>`).join("")}
    </div></details>`;
  }
  els.panel.innerHTML = html;
}

function renderStats() {
  const ids = allItems().map((x) => x.id);
  const kotak = { 1: 0, 2: 0, 3: 0, 4: 0, 5: 0 };
  let baru = 0, jatuhTempo = 0, dilihat = 0, benar = 0;
  for (const id of ids) {
    const s = stateOf(id);
    if (!s) { baru += 1; continue; }
    kotak[s.box] += 1;
    dilihat += s.seen || 0;
    benar += s.right || 0;
    if (isDue(id)) jatuhTempo += 1;
  }
  const maxN = Math.max(1, ...Object.values(kotak));
  const baris = [1, 2, 3, 4, 5].map((b) =>
    `<tr><td>Kotak ${b}</td><td><span class="bar" style="width:${(kotak[b] / maxN) * 160}px"></span>
      &nbsp;${kotak[b]}</td></tr>`).join("");
  const pct = dilihat ? Math.round((benar / dilihat) * 100) : 0;
  els.stats.innerHTML = `<h3>Kemajuan pada modul ${esc(MODES[mode].label)}</h3>
    <table>
      <tr><td>Total kartu</td><td>${ids.length}</td></tr>
      <tr><td>Belum dilatih</td><td>${baru}</td></tr>
      <tr><td>Jatuh tempo</td><td>${jatuhTempo}</td></tr>
      ${baris}
    </table>
    <p>${dilihat ? `Jawaban tercatat: ${dilihat}, benar ${benar} (${pct}%).` : "Belum ada jawaban tercatat."}
    Jeda ulangan per kotak: 0, 1, 3, 7, dan 16 hari.</p>`;
}

/* ------------------------------------------------------------- kendali ---- */

function setMode(m) {
  mode = m;
  activeCat = "*";
  index = 0;
  answered = false;
  for (const b of els.tabs.querySelectorAll("button")) {
    b.setAttribute("aria-pressed", String(b.dataset.mode === m));
  }
  renderToggles();
  renderChips();
  buildDeck();
  render();
  renderStats();
}

function refresh() {
  renderChips();
  buildDeck();
  render();
}

/* Nama tema yang dikenal. Dipakai juga untuk membuang kelas tema lama secara
   tepat sasaran. */
const THEMES = ["papier", "nuit", "lavande"];
const THEME_BAWAAN = "papier";

function setTheme(name) {
  // Nilai dari localStorage bisa saja rusak atau berasal dari versi lama.
  // Tanpa penyaringan ini, body pernah berakhir dengan kelas
  // "theme-[object Object]": tidak ada tema yang sah, tidak ada tombol tema
  // yang tampak aktif, dan nilai rusaknya ditulis balik sehingga menetap.
  if (!THEMES.includes(name)) name = THEME_BAWAAN;

  // classList, bukan className: menimpa className akan menghapus kelas lain
  // yang mungkin ada pada <body>.
  for (const t of THEMES) document.body.classList.remove("theme-" + t);
  document.body.classList.add("theme-" + name);
  for (const b of document.querySelectorAll(".theme-dot")) {
    b.setAttribute("aria-pressed", String(b.dataset.theme === name));
  }
  lsSet(LS.theme, name);
}

function bindToggle(id, key) {
  const el = $(id);
  el.checked = prefs[key];
  el.addEventListener("change", () => {
    prefs[key] = el.checked;
    lsSet(LS.prefs, prefs);
    index = 0;
    refresh();
  });
}

function init() {
  if (!D) {
    document.body.innerHTML = '<p class="empty">webdata.js gagal dimuat. ' +
      'Jalankan <code>python tools/build_web.py</code> lalu muat ulang halaman.</p>';
    return;
  }

  setTheme(lsGet(LS.theme, THEME_BAWAAN));

  els.tabs.addEventListener("click", (e) => {
    const b = e.target.closest("button");
    if (b) setMode(b.dataset.mode);
  });
  els.chips.addEventListener("click", (e) => {
    const b = e.target.closest("button");
    if (!b) return;
    activeCat = b.dataset.cat;
    index = 0;
    refresh();
  });
  els.stages.addEventListener("click", (e) => {
    const b = e.target.closest("button");
    if (!b) return;
    activeStage = Number(b.dataset.stage);
    for (const s of els.stages.querySelectorAll("button")) {
      s.setAttribute("aria-pressed", String(Number(s.dataset.stage) === activeStage));
    }
    activeCat = "*";
    index = 0;
    refresh();
  });
  els.search.addEventListener("input", () => {
    query = els.search.value;
    index = 0;
    buildDeck();
    render();
  });
  els.choices.addEventListener("click", (e) => {
    const b = e.target.closest("button");
    if (b) answer(Number(b.dataset.i));
  });
  els.card.addEventListener("click", (e) => {
    if (!e.target.closest(".choices")) flip();
  });

  $("#btn-flip").addEventListener("click", (e) => { e.stopPropagation(); flip(); });
  $("#btn-next").addEventListener("click", next);
  $("#btn-prev").addEventListener("click", prev);
  $("#btn-right").addEventListener("click", () => gradeFlip(true));
  $("#btn-wrong").addEventListener("click", () => gradeFlip(false));
  $("#btn-shuffle").addEventListener("click", (e) => {
    shuffled = !shuffled;
    e.currentTarget.setAttribute("aria-pressed", String(shuffled));
    index = 0;
    buildDeck();
    render();
  });
  $("#btn-stats").addEventListener("click", (e) => {
    const buka = els.stats.hidden;
    els.stats.hidden = !buka;
    e.currentTarget.setAttribute("aria-expanded", String(buka));
    if (buka) renderStats();
  });
  $("#btn-reset").addEventListener("click", () => {
    if (!confirm("Hapus seluruh progres di peramban ini? Tindakan ini tidak bisa dibatalkan.")) return;
    progress.cards = {};
    lsSet(LS.prog, progress);
    refresh();
    renderStats();
  });

  for (const b of document.querySelectorAll(".theme-dot")) {
    b.addEventListener("click", () => setTheme(b.dataset.theme));
  }

  bindToggle("#tg-lafal", "lafal");
  bindToggle("#tg-artikel", "artikel");
  bindToggle("#tg-arah", "arah");
  bindToggle("#tg-due", "due");
  bindToggle("#tg-hide", "hide");

  document.addEventListener("keydown", (e) => {
    if (e.target === els.search) {
      if (e.key === "Escape") { els.search.value = ""; query = ""; index = 0; refresh(); els.search.blur(); }
      return;
    }
    if (e.ctrlKey || e.metaKey || e.altKey) return;
    switch (e.key) {
      case " ": case "Enter": e.preventDefault(); flip(); break;
      case "ArrowRight": e.preventDefault(); next(); break;
      case "ArrowLeft": e.preventDefault(); prev(); break;
      case "h": case "H": gradeFlip(true); break;
      case "b": case "B": gradeFlip(false); break;
      case "s": case "S": $("#btn-shuffle").click(); break;
      case "l": case "L": $("#tg-lafal").click(); break;
      case "/": e.preventDefault(); els.search.focus(); break;
      default:
        if (/^[1-9]$/.test(e.key)) answer(Number(e.key) - 1);
    }
  });

  window.addEventListener("resize", fitCard);
  if (document.fonts && document.fonts.ready) document.fonts.ready.then(fitCard);

  setMode("kosakata");

  // Jumlah kartu pada tab diambil dari data, bukan ditulis tangan.
  for (const b of els.tabs.querySelectorAll("button")) {
    const n = MODES[b.dataset.mode].items().length;
    b.querySelector("span").textContent = String(n);
  }
}

document.addEventListener("DOMContentLoaded", init);
