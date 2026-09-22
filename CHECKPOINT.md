# 📍 CHECKPOINT — Baca file ini duluan di chat baru

Ini bukan dokumentasi resmi OpenMontage. Ini catatan pribadi user (riy389) —
ringkasan lengkap semua yang sudah dibahas/diputuskan sampai 5 September 2026,
supaya chat baru tidak perlu baca ulang AGENT_GUIDE.md dkk dari nol untuk
hal-hal yang sudah dipahami. Cukup baca file ini.

**Update 16 September 2026 — lihat poin 10 untuk apa yang berubah sejak
5 September.** Poin 1–9 di bawah dibiarkan apa adanya sebagai histori,
kecuali satu koreksi eksplisit di poin 1 (soal reuse OAuth) yang ditandai
jelas supaya tidak membingungkan pembaca berikutnya.

**Update 17 September 2026 — lihat poin 11 untuk hasil sesi testing
end-to-end pertama.** Video test BELUM final, banyak bug ditemukan dan
sebagian sudah di-fix — baca poin 11 sebelum lanjut kerja di project ini.

**Update 22 September 2026 — lihat poin 12 untuk Hermes plugin stack dan
pivot Cloudflare Workers AI image generation.**

---

## 0. Konteks environment user

- User cuma punya **HP + Termux** — tidak ada laptop/PC.
- Setup: **Hermes Agent** (Nous Research, open-source, self-improving CLI
  agent) dijalankan di **GitHub Codespace**, diakses dari HP via **Termux SSH**.
  Termux murni jadi terminal SSH — semua kerja berat (Python, FFmpeg, Node/
  Remotion, render video) terjadi di Codespace, bukan di HP.
- Model Hermes aktif: `gemini-3.6-flash` via Google AI Studio (bisa diganti
  kapan saja dengan `hermes model`, tanpa reinstall).
- Hermes gateway (`nohup hermes gateway run > ~/.hermes/gateway.log 2>&1 &`)
  sudah dijalankan di background — ini untuk chat ke Hermes dari Telegram/
  Discord/dll, TERPISAH dari sistem publish yang direncanakan di bawah.
- Hermes itu SATU instance yang dipakai lintas repo. Tidak perlu install ulang
  untuk repo baru — tinggal `cd` ke folder repo lain lalu jalankan `hermes`
  lagi. Ia otomatis baca context file lokal folder itu (urutan: `.hermes.md`
  → `AGENTS.override.md` → `AGENTS.md` → `CLAUDE.md` → `.cursorrules`, yang
  pertama ketemu dipakai, tidak digabung).
- **PENTING soal siapa mengerjakan apa:** `CHECKPOINT.md` ini (dan seluruh
  riset/setup dokumentasi sebelum `make setup` dijalankan) ditulis oleh
  Claude langsung lewat MCP GitHub connector — BUKAN Hermes. Hermes baru
  mulai terlibat di project ini SETELAH `make setup` dijalankan di
  Codespace (lihat poin 10). Percakapan lanjutan soal testing/debugging
  (poin 11 dst) adalah kolaborasi Claude (lewat chat + MCP) dan Hermes
  (lewat Codespace) secara bersamaan — user menjembatani keduanya dengan
  copy-paste prompt.

## 1. Repo ini vs repo WealthVault — JANGAN DICAMPUR

- **Repo ini** (`riy389/OpenMontage`): fork dari `calesthio/OpenMontage`,
  sistem produksi video agentic open-source. Dipakai untuk eksperimen/proyek
  video baru, terpisah dari WealthVault.
- **`riy389/wealthvault-agent`** (repo lain): pipeline YouTube Shorts harian
  otomatis yang SUDAH production dan jalan sendiri (M1–M6 lengkap, cron
  otomatis, dsb). Checkpoint-nya ada di **Issue #8 repo itu** (repo itu punya
  Issues aktif, beda dengan repo ini).
- Fork itu independen total. Apa pun yang diubah di sini **tidak memengaruhi**
  `calesthio/OpenMontage` (upstream) sama sekali, kecuali sengaja dikirim lewat
  Pull Request dan di-approve manual oleh pemilik upstream.
- **PENTING — perbedaan sifat video antara dua project ini:** WealthVault
  khusus YouTube Shorts (selalu di bawah 50MB, aman). OpenMontage BISA
  menghasilkan video normal/panjang, bukan cuma Shorts — jadi asumsi
  "video selalu di bawah 50MB" TIDAK berlaku otomatis di sini. Ini
  berdampak langsung ke desain `telegram_notify` (lihat poin 8).
- **PENTING — channel YouTube BEDA:** OpenMontage upload ke channel YouTube
  yang berbeda dari WealthVault (channel baru: "The Forgotten Shadows",
  niche dark history). **KOREKSI (sesi lanjutan, lihat poin 10):**
  `YT_CLIENT_ID`/`YT_CLIENT_SECRET` WealthVault BOLEH dan SUDAH di-reuse —
  itu identitas aplikasi Google Cloud, bukan identitas channel, jadi bisa
  dipakai untuk authorize channel manapun berkali-kali tanpa buat Client
  baru. Yang WAJIB baru per channel cuma `YT_REFRESH_TOKEN` (didapat lewat
  consent flow baru, dengan channel target aktif saat klik Allow). Ini
  sudah selesai dikerjakan — lihat poin 10.

## 2. Status fork ini per 5 September 2026

- Branch aktif: `main`.
- **Perubahan kode yang SUDAH masuk ke repo ini:**
  - `CHECKPOINT.md` (file ini)
  - `skills/meta/publish-distribution.md` — SUDAH di-push (termasuk revisi
    Step 3.5, lihat poin 8)
  - `tools/publishers/telegram_notify.py` — SUDAH di-push
  - `tools/publishers/youtube_upload.py` — SUDAH di-push
  - `requirements.txt` — SUDAH diupdate (tambah `google-api-python-client`)
  - **Semua 11 `skills/pipelines/<pipeline>/publish-director.md` yang punya
    stage publish — SUDAH diberi rujukan Distribution** (lihat poin 8.D)
- **Belum `make setup`, belum `.env` diisi** (per 5 September — SUDAH SELESAI
  di sesi lanjutan, lihat poin 10).
- **Issues dinonaktifkan** di repo fork ini (settingan GitHub, kemungkinan
  default fork) — makanya checkpoint disimpan di file ini, bukan di Issue,
  seperti pola WealthVault.

## 3. Cara pindah folder / mulai kerja di repo ini

```bash
cd /workspaces
git clone https://github.com/riy389/OpenMontage.git
cd OpenMontage
make setup
cp .env.example .env
hermes
```

Begitu `hermes` dijalankan dari folder ini, ia otomatis baca `AGENTS.md` di
root, yang isinya HANYA satu perintah wajib: baca `AGENT_GUIDE.md` sebelum
bertindak apa pun. Jangan skip ini — `AGENT_GUIDE.md` (48KB) berisi seluruh
kontrak operasi agent.

## 4. Arsitektur OpenMontage — ringkasan yang sudah dikonfirmasi baca langsung dari source

- **Instruction-driven, agent-first.** Hermes (agent) adalah orkestrator.
  Python di repo ini HANYA tools + persistence — TIDAK ADA orchestrator,
  reviewer, atau logic keputusan kreatif di Python.
- **Rule Zero:** setiap permintaan produksi video WAJIB lewat sistem
  pipeline. Dilarang keras menulis script Python ad-hoc untuk manggil tools
  langsung, atau skip pipeline demi API call langsung.
- **State machine per produksi:**
  `research → proposal → script → scene_plan → assets → edit → compose → publish`
  (stage `publish` ada di sebagian besar pipeline, TIDAK SEMUA — lihat
  pengecualian `documentary-montage` di poin 8.D).
- **12 folder pipeline** ada di `skills/pipelines/` (dikonfirmasi dengan
  menghitung langsung, BUKAN 11 seperti sempat dicatat sebelumnya):
  `animation`, `avatar-spokesperson`, `character-animation`, `cinematic`,
  `clip-factory`, `documentary-montage`, `explainer`, `hybrid`,
  `localization-dub`, `podcast-repurpose`, `screen-demo`, `talking-head`.
  **Hermes yang memilih** pipeline berdasarkan permintaan user — user TIDAK
  wajib tahu nama pipeline duluan. Kalau ambigu, Hermes yang tanya balik.
- **3 layer pengetahuan:**
  1. `tools/` — apa yang ada, cost, runtime (Layer 1, lewat `tool_registry.py`)
  2. `skills/` — cara OpenMontage mau tools itu dipakai, per-pipeline (Layer 2)
  3. `.agents/skills/` — pengetahuan vendor/teknologi mentah, WAJIB dibaca
     sebelum memanggil tool generation apa pun (prompting spesifik provider)

### Prompt ke Hermes tidak perlu panjang/detail

- Kalau permintaan masih vague ("bikinin video soal X"), Hermes otomatis baca
  `skills/meta/onboarding.md` dan membimbing dari situ.
- Kalau permintaan sudah spesifik, langsung masuk Rule Zero.
- User TIDAK perlu menulis scene plan/visual/dll di awal — itu justru
  dikerjakan Hermes per stage.

### Protokol komunikasi keputusan (ketat, dari AGENT_GUIDE.md)

- Sebelum generation call berbayar/konsekuensial: wajib sebutkan tool,
  provider, model, alasan, sample vs batch.
- Wajib tanya user dulu sebelum ganti provider/model/composition engine/mode
  — tidak boleh diam-diam substitusi.
- `decision_log` itu **append-only** — keputusan berubah = entry baru dengan
  `category`+`subject` sama, bukan menimpa yang lama.
- **Hard rule:** kalau Remotion & HyperFrames sama-sama tersedia, WAJIB
  tampilkan dua-duanya ke user sebelum lock `render_runtime`.

### Checkpoint & approval — mekanisme teknis (dari `lib/checkpoint.py`, dibaca langsung)

- Tahap yang di-gate (`human_approval_default: true` di manifest pipeline —
  biasanya `idea`/`proposal`, `script`, `scene_plan`, `assets`, `publish`):
  Hermes WAJIB berhenti total, tulis checkpoint `awaiting_human`, lalu
  **selesai turn-nya** — tidak boleh lanjut kerja di respons yang sama.
- Approval dilakukan dengan **membalas chat ke Hermes**, BUKAN klik apa pun
  di Backlot board (board itu read-only, lihat poin 6).
- Approval per-gate — persetujuan di satu gate tidak otomatis berlaku untuk
  gate berikutnya, kecuali user eksplisit bilang "approve semua" dan itu
  dicatat sebagai `decision_log` entry kategori `approval_policy`.
- **Fungsi resmi:** `write_checkpoint(pipeline_dir, project_id, stage, status,
  artifacts, *, pipeline_type=None, ..., human_approved=False, ...)` di
  `lib/checkpoint.py`. Ini **fail-closed** — kalau stage itu ternyata
  di-gate manifest (`human_approval_default: true`) tapi ditulis
  `status="completed"` tanpa `human_approved=True`, fungsi ini melempar
  `CheckpointValidationError` (`GATE VIOLATION`), bukan diam-diam lolos.
- **Prasyarat berurutan wajib** (`_enforce_stage_prerequisites`): sebuah
  stage tidak bisa maju ke `awaiting_human`/`completed` kalau stage
  sebelumnya di pipeline itu belum `completed` DAN (kalau stage sebelumnya
  itu gated) belum `human_approved=True`. Ini dicek otomatis oleh
  `write_checkpoint`, jadi tidak mungkin "loncat" gate lewat urutan salah.
- Setiap `write_checkpoint()` untuk stage `X` WAJIB menyertakan artifact
  kanoniknya (`CANONICAL_STAGE_ARTIFACTS[X]`) kalau status `completed`/
  `awaiting_human` — untuk stage `publish`, artifact wajibnya adalah
  `publish_log` (relevan langsung untuk rencana Telegram/YouTube di poin 8).

## 5. Di mana file video final berada

- **Selama proses (compose stage):** `projects/<project-id>/renders/final.mp4`
- **Setelah stage `publish`** (lewat tool `export_bundle`):
  `exports/<project-name>/video/output.mp4` (+ `metadata/`, `thumbnails/`)
- **PENTING:** folder `projects/` itu **di-gitignore**. Video hasil generate
  TIDAK PERNAH otomatis ke-commit ke GitHub. Murni file lokal di filesystem
  Codespace. Kalau mau kirim ke Telegram/upload YouTube, ambil dari path
  lokal ini — bukan dari GitHub.

## 6. Backlot board — apa itu dan keterbatasannya

- `python -m backlot open <project-id>` — board live yang menampilkan
  progress pipeline (stage, filmstrip asset, cost, dll), **read-only, murni
  observer**. Agent tidak pernah update UI-nya; semua data derive dari file
  yang sudah ditulis pipeline ke `projects/<id>/`.
- **TIDAK BISA dipakai untuk approve** — approve tetap lewat chat ke Hermes.
- Server bind ke **`127.0.0.1:4750`** (localhost, `DEFAULT_PORT` di
  `backlot/__init__.py`). Di Codespace via SSH/Termux, ini **tidak otomatis
  bisa diakses dari browser HP** tanpa port forwarding (`gh codespace ports
  forward 4750:4750`, atau tab "Ports" di VS Code web/app).
- Kalau forwarding merepotkan, opsi paling praktis untuk kasus HP-only:
  **skip Backlot sepenuhnya**, andalkan Telegram notify di poin 7 & 8.

## 7. OpenMontage TIDAK punya upload otomatis bawaan — dikonfirmasi dari source

- Stage `publish` di semua pipeline cuma menghasilkan **metadata SEO +
  thumbnail concept + packaging lokal** lewat tool `export_bundle`
  (`tools/publishers/export_bundle.py`) — sebelum sesi ini, itu
  SATU-SATUNYA tool di folder `tools/publishers/`.
- Dikonfirmasi eksplisit di `publish-director.md`:
  > "`export_bundle` is a local, offline packager — it does not upload.
  > A networked publisher (e.g. a YouTube uploader) would be a separate
  > `publish`-capability provider."
- Ini beda dari WealthVault yang sudah punya M6 (`youtube_upload.py`) sendiri
  lewat GitHub Actions + cron-job.org. **Sesi ini sudah menutup gap
  tersebut** — lihat poin 8, sekarang sudah ada `telegram_notify.py` dan
  `youtube_upload.py` sendiri untuk OpenMontage.

## 8. Telegram notify (gate approval) + YouTube upload untuk OpenMontage

### Alasan / requirement dari user
- Mau notifikasi/approve video lewat Telegram, dan upload YouTube otomatis.
- **Sifatnya SAMA PERSIS seperti pola WealthVault yang sudah jalan**
  (dikonfirmasi eksplisit oleh user): Telegram = gate approval manusia,
  BUKAN sekadar notifikasi biasa. Video baru boleh upload ke YouTube
  SETELAH di-approve lewat Telegram — bukan otomatis begitu terkirim.
- **Harus jalan di SEMUA pipeline**, bukan cuma satu — karena pipeline
  dipilih otomatis oleh Hermes berdasarkan request, user tidak manual pilih
  satu pipeline saja untuk dipakai terus-menerus.

### Struktur yang disepakati (ikut pola/konvensi ASLI repo — dikonfirmasi baca source, bukan pola karangan baru)

**A. Tool `telegram_notify.py` — ✅ SUDAH DITULIS DAN DI-PUSH (commit `05ffb96`):**
```
tools/publishers/telegram_notify.py
```
- `capability = "publish"`, `tier = ToolTier.PUBLISH`, `provider = "telegram"`.
- `dependencies = ["env:TELEGRAM_BOT_TOKEN", "env:TELEGRAM_CHAT_ID",
  "python:requests"]` — `requests>=2.31` sudah ada di `requirements.txt`,
  tidak perlu tambahan dependency.
- Mengirim video via `sendVideo` (Bot API), catat `publish_log` entry
  `status: "pending_review"` (BUKAN `"published"`) — approval sesungguhnya
  tetap keputusan manusia via balasan Telegram, dibaca ulang oleh Hermes,
  bukan oleh tool ini (tool ini SYNC, sekali kirim-selesai, tidak menunggu
  balasan).
- **Digunakan DUA KALI dalam alur** (lihat bagian C, Step 3.5): sekali
  sebagai gate approval sebelum upload, sekali lagi sebagai konfirmasi
  setelah `youtube_upload` sukses — TIDAK ada tool terpisah untuk notifikasi
  publish, ini satu tool yang sama dipakai dua kali dengan caption berbeda.
- **Limit 50MB Bot API (khusus OpenMontage, BEDA dari asumsi WealthVault):**
  - WealthVault selalu di bawah 50MB (khusus Shorts) — aman.
  - **OpenMontage TIDAK bisa diasumsikan sama** — bisa menghasilkan video
    normal/panjang, bukan cuma Shorts, jadi risiko kena limit 50MB Bot API
    itu nyata.
  - **Solusi yang dipakai SEKARANG (v1, sudah diimplementasikan):** kalau
    video > 50MB, tool fallback ke `sendMessage` — kirim caption + path
    lokal video (BUKAN gagal total, BUKAN kirim file terpotong).
  - **Keputusan user:** coba jalan dulu dengan fallback ini. Kalau nanti
    dirasa tidak cukup, baru cari workaround lebih baik — kandidat yang
    sudah disebut user: **MTProto client** (mis. Pyrogram/Telethon), yang
    limitnya jauh lebih besar (~2GB) dibanding Bot API biasa. INI BELUM
    DIIMPLEMENTASIKAN — baru dicatat sebagai rencana cadangan kalau perlu.

**B. Tool `youtube_upload.py` — ✅ SUDAH DITULIS DAN DI-PUSH (commit `f38bf00`):**
```
tools/publishers/youtube_upload.py
```
- Autentikasi & pola resumable upload **diadaptasi langsung dari
  `youtube_upload.py` WealthVault** (`Credentials(...)` + refresh token +
  `build("youtube","v3",...)` + `MediaFileUpload(..., resumable=True)`) —
  ini bagian yang sudah terbukti jalan production di WealthVault, dipakai
  ulang polanya (bukan kode WealthVault-nya, karena beda channel/kredensial).
- Yang SENGAJA DIBUANG dari versi WealthVault (spesifik arsitektur
  WealthVault, tidak relevan untuk OpenMontage): fetch asset dari GitHub
  Releases (`fetch_assets`), baca `state/naskah.json`, commit balik ke git
  (`update_state_and_commit`) — OpenMontage sudah punya video di filesystem
  lokal + `publish_log`/checkpoint sendiri, tidak butuh semua itu.
- `dependencies = ["env:YT_CLIENT_ID", "env:YT_CLIENT_SECRET",
  "env:YT_REFRESH_TOKEN", "python:google.oauth2.credentials",
  "python:googleapiclient"]`.
- **`google-api-python-client` ditambahkan ke `requirements.txt`** — paket
  ini TIDAK otomatis ter-cover oleh `google-auth`/`google-genai` yang sudah
  ada sebelumnya (beda paket, `googleapiclient.discovery`/`.http`).
- `category_id` default `"22"` (People & Blogs) — ini KEPUTUSAN SEPIHAK
  Claude, bukan dari sumber otoritatif. WealthVault pakai `"25"` (News &
  Politics) karena kontennya spesifik finance. Kalau user mau kategori beda
  untuk OpenMontage, tinggal ganti parameter `category_id` saat pemanggilan
  — **masih belum ada keputusan final dari user soal ini** (tetap terbuka
  per 16 September).
- **PENTING — kredensial OAuth:** lihat koreksi di poin 1 dan detail
  pelaksanaan di poin 10 — Client ID/Secret di-reuse, refresh token baru.

**C. Meta skill — ✅ SUDAH DITULIS DAN DI-PUSH (commit terakhir `0c15621`):**
```
skills/meta/publish-distribution.md
```
Isi lengkapnya (5 langkah + Step 3.5, gaya sama seperti
`checkpoint-protocol.md`):
1. **When to Use** — dipanggil setelah `export_bundle` selesai packaging,
   sebelum checkpoint stage `publish` ditulis.
2. **Discover providers** — baca dari `registry.get_by_capability("publish")`,
   bukan hardcode nama tool. `export_bundle` selalu muncul; `telegram_notify`
   dan `youtube_upload` cuma muncul kalau env var-nya sudah diisi.
3. **Wajib tanya user** provider mana yang dipakai (Telegram/YouTube/lokal
   saja) sebelum eksekusi — sesuai Decision Communication Contract, dilarang
   diam-diam pilih.
4. **Eksekusi + isi `publish_log`** — field harus persis sesuai
   `publish_log.schema.json` (`platform`, `status`, `url`, `video_id`,
   `visibility`, `export_path`, `timestamp`, `metadata_used`, `error` — TIDAK
   BOLEH nambah field baru, `additionalProperties: false` di root & entry).
   - **Telegram (pra-upload) = `status: "pending_review"`**, BUKAN
     `"published"` — video sedang menunggu keputusan manusia di Telegram.
   - **YouTube upload baru boleh jalan SETELAH approval Telegram diterima**
     (atau langsung kalau user memang skip Telegram review untuk project
     itu) — YouTube sukses = `status: "published"`, isi `video_id`, `url`,
     `visibility`.
5. **Step 3.5 (BARU, ditambah setelah ditemukan gap):** `telegram_notify`
   WAJIB dipanggil **lagi** setelah `youtube_upload` sukses, kali ini
   sebagai notifikasi konfirmasi ("✅ Published: <url>"), BUKAN gate lagi —
   entry `publish_log` untuk panggilan kedua ini `status: "published"`.
   Ini persis meniru `notify_telegram()` di WealthVault yang tadinya
   sempat mau dibuang tapi user koreksi supaya tetap dipertahankan, cuma
   bentuknya jadi "panggil tool yang sama dua kali", bukan tool terpisah.
6. **Checkpoint stage `publish`** pakai `write_checkpoint()` — approval
   Telegram dan approval gate stage `publish` itu **DUA KEPUTUSAN TERPISAH**:
   dapat thumbs-up di Telegram TIDAK otomatis memenuhi gate stage `publish`.
   Hermes tetap wajib konfirmasi eksplisit ke user sebelum menulis
   `status="completed", human_approved=True`.

**D. Rujukan `## Distribution` di file `publish-director.md` — ✅ SELESAI SEMUA:**
- **KOREKSI PENTING:** OpenMontage punya **12 folder pipeline**, bukan 11
  seperti dicatat sebelumnya. Ketemu satu pipeline tambahan yang belum
  pernah dicek: **`documentary-montage`**.
- `documentary-montage` **TIDAK punya `publish-director.md`** sama sekali
  (juga tidak punya `script-director.md`/`proposal-director.md`/
  `research-director.md` — strukturnya cuma
  `idea/scene/asset/edit/compose-director.md` + `executive-producer.md`).
  Kemungkinan ini pipeline versi lama/struktur berbeda, BUKAN "v2.0" penuh.
  Jadi TIDAK ada rujukan Distribution ditambahkan di pipeline ini — tidak
  ada tempat untuk menaruhnya.
- **11 pipeline lain SEMUA sudah dikonfirmasi punya `publish-director.md`**
  (dicek satu-satu lewat `get_file_contents`, bukan diasumsikan dari nama
  folder) dan **SEMUA sudah diberi rujukan Distribution**:
  1. `animation` ✅ (commit `7cb9056`)
  2. `avatar-spokesperson` ✅ (commit `79254b5`)
  3. `character-animation` ✅ (commit `81451d3`)
  4. `cinematic` ✅ (commit `5f9a58f`)
  5. `clip-factory` ✅ (commit `71b7451`)
  6. `explainer` ✅ (commit `c091aa9`) — ditaruh sebagai **Step 7.5** (gaya
     numbered steps, beda dari yang lain yang pakai heading `## Distribution`
     biasa)
  7. `hybrid` ✅ (commit `ccada79`)
  8. `localization-dub` ✅ (commit `5f9d214`)
  9. `podcast-repurpose` ✅ (commit `5936ecb`)
  10. `screen-demo` ✅ (commit `d4a8b9d`)
  11. `talking-head` ✅ (commit `c012537`) — ditaruh sebagai **Step 5.5**
      (sama alasan dengan explainer, gaya numbered steps)
- Sudah dikonfirmasi sebelumnya (dan tetap benar): **tidak ada precedent
  shared-reference** antar publish-director sebelum sesi ini — tiap file
  isinya beda total gaya (SEO-heavy di explainer vs hero/derivative di
  cinematic vs locale-based di localization-dub, dst). Rujukan Distribution
  ditambah manual satu-satu, bukan lewat mekanisme otomatis.
- Pola rujukan yang dipakai (untuk file bergaya heading biasa):
  ```
  ## Distribution
  After packaging, read `skills/meta/publish-distribution.md` for optional
  Telegram/YouTube distribution.
  ```
  Untuk file bergaya numbered-steps (`explainer`, `talking-head`), rujukan
  ditaruh sebagai step tersisip (`Step 7.5`/`Step 5.5`) dengan kalimat yang
  disesuaikan konteks step sekitarnya, bukan disalin persis.

### Progress checklist (per 5 September — status terbaru ada di poin 10)
- [x] Baca `schemas/artifacts/publish_log.schema.json`
- [x] Baca `lib/checkpoint.py` — pahami `write_checkpoint`, gate
      enforcement, prasyarat berurutan
- [x] Baca `tools/base_tool.py` lengkap + `tools/publishers/export_bundle.py`
      sebagai template gaya penulisan tool
- [x] Tulis & push `skills/meta/publish-distribution.md` (+ Step 3.5)
- [x] Tulis & push `tools/publishers/telegram_notify.py`
- [x] Baca `youtube_upload.py` WealthVault (referensi pola auth)
- [x] Tulis & push `tools/publishers/youtube_upload.py`
- [x] Update `requirements.txt` (`google-api-python-client`)
- [x] **Tambah rujukan Distribution di semua 11 `publish-director.md` yang
      ada** (12 pipeline total, `documentary-montage` dikecualikan karena
      tidak punya stage publish)
- [x] `make setup` + isi `.env` di Codespace — **SELESAI, lihat poin 10**
- [ ] Keputusan belum final: `category_id` YouTube upload (default saat ini
      `"22"`, sepihak dari Claude — user belum konfirmasi)
- **Bagian dokumentasi/kode dari rencana Telegram+YouTube publisher SUDAH
  SELESAI SEPENUHNYA** (17 file berubah/ditambah total: `CHECKPOINT.md`,
  `publish-distribution.md`, `telegram_notify.py`, `youtube_upload.py`,
  `requirements.txt`, + 11 `publish-director.md`). **Bagian operasional
  (`make setup`, isi `.env`, OAuth Client baru) SUDAH SELESAI juga per
  16 September — lihat poin 10.** Yang tersisa: uji coba nyata end-to-end.

## 9. Key learnings / aturan permanen untuk sesi berikutnya

- **User eksplisit melarang asumsi.** Wajib riset/baca source langsung
  sebelum menjawab pertanyaan teknis (nama produk, arsitektur, kemampuan
  tool/software) — bukan cuma untuk OpenMontage, ini aturan permanen di
  semua topik. Kalau ditanya dan belum tahu, baca dulu baru jawab; jangan
  tanya izin "mau dibaca dulu gak" — user sudah kasih akses MCP GitHub
  supaya langsung dipakai.
- **Jangan asumsikan jumlah/daftar item dari ingatan sebelumnya** — contoh
  nyata sesi ini: sempat dicatat "11 pipeline" tanpa menghitung ulang
  langsung dari `skills/pipelines/`, padahal aslinya ada 12 folder
  (`documentary-montage` terlewat). Selalu `get_file_contents` pada
  direktori aslinya untuk memverifikasi jumlah/daftar sebelum menyatakan
  sesuatu "selesai untuk semua N item".
- **Cek folder/struktur lengkap sebelum menulis kode baru** — contoh nyata
  sesi lanjutan (poin 10): sempat menulis `tools/graphics/wikimedia_image.py`
  dan `loc_image.py` dari nol tanpa mengecek `tools/video/stock_sources/`
  lebih dulu, padahal folder itu sudah punya implementasi Wikimedia/LOC yang
  jauh lebih matang (adapter pattern, cascading search, terintegrasi ke
  corpus builder). Hasilnya kerja duplikat yang harus dihapus lagi.
  Pelajaran: sebelum bikin tool/provider baru, `get_file_contents` pada
  SEMUA folder yang mungkin relevan (bukan cuma yang paling jelas dari nama),
  terutama untuk kapabilitas yang generic (image/video source) yang bisa
  saja sudah diimplementasikan di lokasi lain dari yang diduga.
- Fork GitHub independen total dari upstream — perubahan di fork tidak
  memengaruhi repo asal, kecuali PR yang di-approve manual.
- `search_repositories` GitHub API secara default **menyembunyikan fork**
  dari hasil pencarian biasa — jangan simpulkan "tidak ada" hanya dari
  situ; cek langsung ke akun/URL kalau hasil kosong tapi kamu tahu itu ada.
- `search_code` GitHub API kadang tidak langsung mengindeks file yang baru
  di-push atau sudah lama ada (delay indexing) — kalau hasilnya kosong tapi
  kamu ragu, cek langsung lewat `get_file_contents` pada direktori/path yang
  dicurigai, jangan simpulkan "tidak ada" hanya dari `search_code` kosong.
- Repo ini (`OpenMontage`) dan `wealthvault-agent` itu dua konteks terpisah
  — jangan campur checkpoint/pembahasan keduanya. TAPI: pola desain yang
  sudah terbukti jalan di WealthVault (Telegram=gate, YouTube auth/refresh
  token, notifikasi post-publish) boleh dan memang sengaja diadaptasi ke
  OpenMontage — bukan ditiru membabi buta, disesuaikan ke arsitektur
  `BaseTool`/`publish_log` di sini.
- **Asumsi yang valid di satu project belum tentu valid di project lain**
  — contoh nyata: "video selalu di bawah 50MB" itu benar untuk WealthVault
  (khusus Shorts) tapi TIDAK bisa diasumsikan sama untuk OpenMontage (bisa
  bikin video panjang). Selalu cek konteks project spesifik, jangan
  menggeneralisasi dari satu project ke project lain begitu saja.
- **Jangan buang fungsi tanpa konfirmasi eksplisit** — sempat hampir salah
  membuang notifikasi post-publish Telegram (`notify_telegram()` WealthVault)
  saat adaptasi ke `youtube_upload.py` OpenMontage, karena diasumsikan
  fungsinya "sudah tercover" tanpa verifikasi jelas. User mengoreksi ini —
  pelajarannya: kalau ragu apakah sebuah fungsi lama masih relevan/perlu
  dipertahankan dalam bentuk lain, TANYA dulu, jangan diam-diam dihilangkan.
- Debugging bug di satu project (mis. tombol Telegram WealthVault yang
  sempat tidak respons) TIDAK ADA hubungannya dengan pekerjaan paralel di
  project lain (OpenMontage) kecuali dinyatakan eksplisit — jangan
  mengasumsikan efek samping lintas-project tanpa bukti.
- **Jangan pernah tampilkan/cat isi file `.env` mentah ke chat manapun**,
  bahkan untuk "verifikasi" — pakai cek kosong/terisi saja (lihat poin 10),
  karena upaya redaksi manual bisa gagal dan membocorkan fragmen key asli.
  Kalau ada kebocoran, sarankan rotate key yang bersangkutan.
- File ini (`CHECKPOINT.md`) murni untuk fase DEVELOPMENT, dibaca MANUAL per
  sesi kerja lanjutan — bukan bagian dari alur produksi video permanen.
  Begitu Telegram+YouTube publisher selesai dan sudah nempel di
  `publish-distribution.md`/`publish-director.md`, isi checkpoint ini jadi
  usang dan boleh dihapus/ditandai selesai. Instruksi cara pakai yang
  PERMANEN letaknya di `skills/meta/publish-distribution.md`, bukan di sini.

## 10. Sesi lanjutan (16 September 2026) — operasional selesai, siap testing

Semua bagian "belum" di poin 8 checklist sudah dikerjakan. Ringkasan:

- **`make setup` dijalankan di Codespace** — `.venv`, `requirements.txt`,
  `npm install` (remotion-composer), piper-tts semua sukses. HyperFrames
  cache-warm timeout (opsional, tidak masalah).
- **`.env.example` ditambah 6 variable yang tadinya hilang** (commit
  `6e04f3e`): `TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHAT_ID`, `YT_CLIENT_ID`,
  `YT_CLIENT_SECRET`, `YT_REFRESH_TOKEN`, `COMFYUI_IMAGE_SERVER_URL`.
- **`.env` di Codespace sudah terisi lengkap** untuk pendekatan
  free-sources-first:
  - Telegram: `TELEGRAM_BOT_TOKEN` + `TELEGRAM_CHAT_ID` — **reuse dari bot
    WealthVault yang sudah ada** (dikonfirmasi aman: `telegram_notify.py`
    murni one-way notify, tidak baca balasan/webhook, jadi tidak ada risiko
    tabrakan state antar-project di level kode).
  - YouTube: `YT_CLIENT_ID`/`YT_CLIENT_SECRET` **reuse dari WealthVault**
    (lihat koreksi poin 1). `YT_REFRESH_TOKEN` **baru**, didapat via
    `google-auth-oauthlib` `InstalledAppFlow.run_local_server(port=8080,
    open_browser=False)` dijalankan **langsung di Termux** (bukan
    Codespaces) — supaya browser HP dan script Python sama-sama di
    `localhost`, menghindari kerumitan port-forwarding Codespaces sama
    sekali. Catatan penting: redirect_uri `urn:ietf:wg:oauth:2.0:oob` sudah
    DIDEPRECATE Google — jangan pakai itu lagi, selalu pakai
    `run_local_server` dengan `open_browser=False` kalau tidak ada
    browser GUI otomatis yang bisa dipakai flow-nya.
  - Channel YouTube baru: **"The Forgotten Shadows"** (niche dark history).
    Nama sengaja dibuat spesifik/tidak generik, sesuai permintaan user.
  - Pexels: `PEXELS_API_KEY` **reuse dari WealthVault** — dikonfirmasi
    key ini akan **dipakai bersama (shared quota)** oleh WealthVault dan
    OpenMontage, bukan kuota terpisah. Limit gratis: 200 req/jam + 20.000
    req/bulan (bisa minta unlimited gratis kalau eligible).
  - Pixabay: `PIXABAY_API_KEY` **reuse dari WealthVault**, sama-sama shared
    quota. Limit gratis: ~100 req/menit (wajib cache 24 jam, dilarang
    hotlink — `pexels_video.py`/`pixabay_video.py` yang ada sudah patuh
    karena download ke file lokal duluan).
  - `COMFYUI_IMAGE_SERVER_URL`: **sengaja ditunda** — user pilih fokus ke
    free stock/archival sources dulu untuk niche dark history, ComfyUI+
    Kaggle nanti kalau perlu generative image.
- **Cara verifikasi `.env` yang WAJIB dipakai seterusnya** (lihat juga
  poin 9 soal larangan cat isi `.env` mentah):
  ```bash
  grep -v '^#' .env | grep -v '^$' | awk -F'=' '{if ($2=="") print $1" -> KOSONG"; else print $1" -> TERISI"}'
  ```
  atau untuk cek satu variable spesifik: `grep -c "NAMA_VAR=." .env` (harus
  keluar `1` kalau terisi).
- **Free stock/archival sources untuk niche dark history — SUDAH LENGKAP,
  TIDAK PERLU KODE TAMBAHAN.** Ditemukan (setelah sempat salah bikin
  duplikat, lihat poin 9) bahwa `tools/video/stock_sources/` sudah berisi
  semua adapter yang dibutuhkan, semua `is_available()` tanpa syarat
  (kecuali Pexels/Pixabay yang butuh API key, sudah diisi; dan Mixkit yang
  butuh `beautifulsoup4`, sudah diinstall manual dan dikonfirmasi
  `MixkitSource().is_available() == True`):
  - `pexels.py` (video), `pixabay_video.py` — B-roll modern generik
  - `mixkit.py`, `coverr.py` — B-roll modern generik gratis tanpa key
  - `wikimedia.py` (image+video), `loc.py` (Library of Congress, image+
    video), `nara.py` (National Archives) — foto/dokumen/rekaman sejarah
    asli, public domain, PALING relevan untuk dark history
  - Lainnya (tidak terlalu relevan untuk niche ini tapi ada): `videvo.py`,
    `dareful.py`, `pond5_pd.py`, `nasa.py`, `noaa.py`, `esa.py`, `jaxa.py`,
    `unsplash.py`
  - Priority yang SUDAH di-set di kode (tie-breaker untuk corpus selection,
    bukan filter kaku — sistem fan-out ke semua source lalu ranking by
    similarity+priority): LOC=40, NARA=35, Wikimedia=25, Mixkit=19 (yang
    lain belum dicek satu-satu, tapi urutan yang ada sudah cocok secara
    default untuk dark history: sumber otentik-historis diutamakan di atas
    filler suasana generik).
  - **`beautifulsoup4` diinstall manual via pip di Codespace, TIDAK
    ditambahkan ke `requirements.txt`** (keputusan eksplisit user) — kalau
    Codespace di-rebuild dari nol, ingat install ulang manual sebelum pakai
    Mixkit.
  - Rekaman 911/interogasi polisi (FOIA audio) yang sempat diminta user:
    **TIDAK dibuatkan tool** — sifatnya beda dari source lain (bukan API
    terpusat, kumpulan situs per-agency/per-state via permintaan FOIA
    manual, rawan isu legal/false-positim public domain per-kasus). Dicatat
    di sini kalau user tanya lagi nanti, bukan dianggap gap yang perlu
    ditutup.
- **Masih kosong/ditunda di `.env`** (tidak blocking untuk testing
  pertama): `COMFYUI_IMAGE_SERVER_URL`, dan hampir semua provider
  berbayar/opsional lain di `.env.example` (FAL, MiniMax, ElevenLabs,
  OpenAI, dll) — pendekatan yang dipilih user adalah free-sources-first.
- **STATUS: siap testing end-to-end.** Generate satu video penuh untuk
  channel "The Forgotten Shadows" pakai stock sources gratis yang sudah
  aktif, sampai ke tahap Telegram approval → YouTube upload. Ini next
  action untuk sesi berikutnya.
- **Belum diputuskan:** `category_id` YouTube upload (masih default `"22"`,
  sepihak dari Claude, belum dikonfirmasi user — sama seperti status di
  poin 8).

## 11. Sesi testing end-to-end pertama (17 September 2026) — banyak bug ditemukan, video BELUM final

Testing end-to-end pertama untuk channel "The Forgotten Shadows" dijalankan
dengan topik **"The Dancing Plague of 1518"** (Strasbourg), project id
`forgotten-shadows-dance-plague`, pipeline `documentary-montage`. Video
**BELUM pernah di-upload ke YouTube** — masih dalam proses perbaikan asset.

### Brief yang disepakati (Stage 1, sudah approved)
- Tone: elegiac / tone-poem ala Adam Curtis, 90 detik, 3-act.
- Narasi: awalnya "none" (visual+musik saja), lalu DIUBAH jadi PAKAI
  narasi setelah user tegas minta ("orang harus ngerti isi videonya").
  **Narasi WAJIB bahasa Inggris** — target audience channel ini US/global,
  bukan Indonesia. Ini keputusan permanen untuk channel ini.
- Musik: awalnya diusulkan fal.ai (paid) → DITOLAK, ganti ke pixabay_music
  → ternyata BUKAN zero-key beneran (web scraping, kena 403 Cloudflare,
  sama seperti kasus LOC/NARA/Pond5) → pindah ke Freesound API
  (`FREESOUND_API_KEY` sudah diisi user di `.env`, working).
- End-tag: "THE BODY REMEMBERS WHAT THE MIND FORGETS." (overlay, 5.5s).

### Bug-bug yang ditemukan dan SUDAH di-fix di kode:
1. **Bug sistemik di `_load_dotenv()` (`tools/base_tool.py`)** — kondisi
   `if key and key not in os.environ` gagal menimpa env var yang sudah ada
   di `os.environ` sebagai string kosong `""`. Ini menyebabkan 8 env var
   (YT_CLIENT_ID/SECRET/REFRESH_TOKEN, PEXELS_API_KEY, PIXABAY_API_KEY,
   TELEGRAM_BOT_TOKEN/CHAT_ID, MINIMAX_REGION) sempat salah terbaca
   "NOT SET" padahal `.env` terisi lengkap. **FIXED**: logic diganti jadi
   `if key and (key not in os.environ or not os.environ[key].strip())`.
   Semua 8 var dikonfirmasi ulang terbaca benar setelah fix.
2. **Audio bocor dari footage asli** — `video_compose.py` sempat fallback
   ke `-c:a copy` dari audio original clip kalau musik gagal, alih-alih
   silent. **FIXED**: sekarang selalu `-an` (strip semua audio source)
   duluan, musik/narasi ditambah di layer terpisah.
3. **Freeze pada clip pendek** — clip yang durasinya < slot teralokasi
   sempat bikin ffmpeg hold frame terakhir. **FIXED**: deteksi
   `_get_clip_duration()`, auto `-stream_loop -1` kalau clip < slot.
4. **End-tag ffmpeg timeout** — drawtext overlay timeout di 60s tanpa
   preset cepat. **FIXED**: `-preset ultrafast` + timeout naik ke 300s.
5. **Durasi video terpotong** (90s → 79.87s) — root cause: `-shortest` di
   audio mixer mengikuti durasi musik yg lebih pendek dari video.
   **FIXED**: durasi video di-force `-t 90` eksplisit, tidak lagi ikut
   durasi musik.
6. **Piper TTS 404 saat download voice model** — root cause: repo
   `rhasspy/piper` sudah DI-ARCHIVE, dev pindah ke `OHF-Voice/piper1-gpl`.
   Voice model tetap ada tapi harus diunduh dari Hugging Face
   (`rhasspy/piper-voices`), bukan GitHub releases lama. **FIXED**, Piper
   TTS sekarang jalan (tested, generate `narration.wav` 43.55s sukses).

### Bug yang PALING SERIUS — asset relevance, BELUM tuntas:
- **Root cause dikonfirmasi**: `direct_clip_search` ("fast path" di
  `asset-director.md`) **TIDAK PERNAH menjalankan CLIP scoring sama
  sekali**. Alurnya cuma search → download → pick top result → approve,
  tanpa threshold relevansi. Quality gate `score >= 0.22` yang disangka
  jadi jaminan kualitas HANYA berlaku untuk "standard path" (corpus + CLIP
  retrieval), bukan fast path yang dipakai project ini.
  `checkpoint_assets.json` mencatat `"human_approved": true` tanpa field
  score/reasoning apa pun — makanya clip yang salah total bisa "lolos"
  tanpa ada sinyal peringatan.
- **Akibatnya ditemukan lewat verifikasi manual (extract frame + lihat
  langsung, BUKAN percaya laporan teks Hermes)**: dari 15 slot, hanya
  2 SLOT yang benar-benar tervalidasi visual (Stephansdom cathedral untuk
  church tower, iron lock hasp dengan Ken Burns). **Mayoritas slot lain
  (perkiraan 8-10 dari 15) menampilkan footage yang SAMA SEKALI TIDAK
  RELEVAN**: bangunan modern dengan kanopi, orang menggergaji kayu di
  rumput, wajah pria modern berkacamata, gedung parkir/konstruksi modern,
  festival kontemporer dengan bendera warna-warni, orang jalan di taman
  kota modern dengan bangku beton, bahkan satu clip bernama "Teatro
  Morelos" (venue modern di Meksiko, sama sekali tidak nyambung ke
  Strasbourg 1518).
- **Pelajaran KERAS dari sesi ini**: laporan status/audit visual dari
  Hermes TIDAK BISA DIPERCAYA tanpa verifikasi manual. Berkali-kali
  terjadi Hermes melaporkan "✅ sudah diverifikasi/sesuai" padahal setelah
  di-extract-frame dan dilihat langsung, isinya salah total (termasuk satu
  kali klaim "Drotten Church Ruin" yang ternyata isinya peta antik
  "Gotland 1572", dan laporan "15/15 slot sudah diaudit visual" yang
  ternyata tidak akurat sama sekali). Kemungkinan besar proses "audit
  visual" Hermes selama ini cuma membaca nama file/metadata, BUKAN
  benar-benar menganalisis piksel gambar — belum dikonfirmasi jawaban
  jujurnya dari Hermes soal ini.
- **ATURAN BARU untuk sesi berikutnya dan seterusnya**: SETIAP klaim
  "clip sudah sesuai/relevan" dari Hermes WAJIB diverifikasi dengan
  extract frame + kirim sebagai GAMBAR (bukan dideskripsikan teks) ke
  user, SEBELUM di-assign ke timeline atau dianggap final. Jangan pernah
  approve berdasarkan deskripsi teks saja.

### Bug lain yang ditemukan, belum dikorek tuntas:
- **Sumber "Archive.org" di manifest awal ternyata fiktif** — manifest
  sempat klaim "Archive.org (8 clips), Wikimedia (13)" tapi user konfirmasi
  SEMUA clip yang muncul di video sebenarnya dari Wikimedia saja, tidak ada
  satupun dari Archive.org. Belum diinvestigasi root cause-nya (apakah
  archive_org.py gagal diam-diam dan fallback tanpa lapor, atau field
  source di manifest salah dicatat) — user memutuskan SKIP investigasi ini,
  fokus ke perbaikan search query saja.
- **LOC, NARA, Pond5 tetap 403 (Cloudflare bot protection)** — dikonfirmasi
  ini BUKAN soal API key atau rate limit, tapi Cloudflare WAF yang
  mendeteksi automated request. Opsi bypass (cloudscraper/curl_cffi/
  headless browser) SENGAJA TIDAK dikejar — dinilai terlalu berat/rapuh
  untuk pipeline yang harus fully-automated tanpa pengawasan terus-menerus
  (user constraint: caregiving, tidak selalu bisa pantau). Ditunda sampai
  terbukti perlu.
- **Cut_01 (0-6 detik) sempat blank hitam total** di salah satu render —
  root cause BELUM firm dikonfirmasi (diduga bug arsitektur mirip upstream
  issue #358 "documentary-montage compose produces black video", tapi
  dikonfirmasi issue itu SUDAH FIXED di fork kita via commit `9482edd`/PR
  #466 — jadi cut_01 hitam kemungkinan bug LAIN yang belum teridentifikasi,
  BUKAN #358). Perlu investigasi ulang di sesi berikutnya kalau muncul lagi.

### Fork vs upstream — status sinkronisasi (dicek 17 September)
- Fork `riy389/OpenMontage` HAMPIR sinkron dengan upstream
  `calesthio/OpenMontage` — cuma ketinggalan 1 commit docs (`08e2151`),
  dan LEBIH MAJU 22 commit (semua kerja publisher/docs sesi-sesi sebelumnya).
- 2 issue upstream yang relevan sudah dicek dan DIKONFIRMASI SUDAH FIXED di
  fork kita: **#357** (corpus_builder silent-success saat CLIP embed gagal
  total — guard sudah aktif di commit `cbe3666`/`0036087`) dan **#358**
  (video hitam untuk documentary-montage — fix sudah masuk via commit
  `9482edd`/PR #466, meski PR asli #439 tidak di-merge upstream, upstream
  pakai implementasi lain).
- Sync 1 commit docs yang tersisa BELUM dilakukan — tidak urgent, boleh
  kapan saja (`git merge upstream/main`).

### Strategi asset-sourcing BARU (disepakati akhir sesi ini, BELUM dieksekusi penuh)
Karena era 1518 pra-fotografi (tidak ada "footage otentik" yang bisa
dicari), dan approach "cari footage medieval" berkali-kali gagal, strategi
diganti total jadi **3 kategori per slot**, berdasarkan APA YANG DISEBUT
NASKAH NARASI di rentang waktu itu (bukan generalisasi kaku):

1. **LOKASI/TEMPAT** — untuk slot yang narasinya menyebut TEMPAT: cari
   footage/foto KEADAAN SEKARANG dari lokasi asli (Strasbourg — arsitektur
   half-timbered, Cathédrale Notre-Dame de Strasbourg), framing "di sinilah
   dulu terjadi...". BUKAN reenactment/lukisan lama.
2. **ACTION/KEGIATAN** — untuk SETIAP slot yang narasinya menyebut suatu
   ACTION (apapun action-nya — menari, kolaps, main musik, dst, TIDAK
   dibatasi cuma "menari"): cari footage yang menunjukkan action itu
   TERJADI, dari sumber/era manapun (tidak perlu otentik 1518), yang
   penting POSE/GERAKAN-nya match narasi di momen itu.
3. **EMOSI ABSTRAK** — untuk momen suasana/emosi tanpa tempat/action
   konkret: boleh pakai footage/painting simbolis apapun yang cocok
   mood-nya.
- Kandidat kuat yang sudah ditemukan untuk kategori Action-menari:
  `wikimedia_196567970_danceplague.webm` — animasi YANG SECARA SPESIFIK
  tentang Dancing Plague 1518, dipakai untuk 2 slot berbeda (potongan
  segmen berbeda supaya tidak repetitif).
- **BELUM dieksekusi**: re-kategorisasi 15 slot penuh + assign clip baru
  sesuai strategi ini masih dalam proses per akhir sesi ini.

### Insiden lain sesi ini
- Sempat ada indikasi Hermes mencoba pakai **FAL.ai (paid API)** untuk
  image generation tanpa approval user ("saldo FAL.ai habis" muncul di
  laporan tanpa diminta) — dikonfirmasi user TIDAK ADA biaya tertagih
  (kemungkinan API key/akun FAL.ai memang tidak pernah ada/aktif). Tetap
  jadi PERINGATAN KERAS: constraint project ini FREE-ONLY, dilarang keras
  coba paid API apapun tanpa tanya user dulu — ini pelanggaran pola yang
  sama dengan percobaan fal.ai untuk musik di awal sesi.
- Video final SEMPAT hampir di-upload ke YouTube tanpa sepengetahuan penuh
  user — Hermes menulis "Jika OK, saya lanjutkan ke upload" setelah user
  cuma bilang video mau di-review, padahal kesepakatan eksplisit adalah
  STOP TOTAL setelah render, user yang putuskan langkah berikutnya secara
  eksplisit, bukan otomatis lanjut dari kalimat "OK videonya bagus".
  **ATURAN INI DITEGASKAN ULANG**: JANGAN PERNAH anggap approval video =
  approval upload, itu 2 keputusan terpisah, tanya eksplisit untuk
  masing-masing.

### STATUS AKHIR SESI — next action untuk sesi berikutnya
- Video `forgotten-shadows-dance-plague` **BELUM final, BELUM diupload**.
- Next: eksekusi strategi 3-kategori di atas untuk re-kategorisasi dan
  assign ulang SEMUA 15 slot (bukan cuma yang sudah sempat diperbaiki
  manual sejauh ini — cut_06, cut_07, cut_09, cut_10, cut_13, cut_14).
- Setiap clip baru WAJIB di-extract-frame dan dikirim sebagai GAMBAR untuk
  verifikasi manual sebelum di-assign ke timeline — tidak ada pengecualian,
  mengingat rekam jejak laporan teks yang tidak akurat berkali-kali di
  sesi ini.
- `category_id` YouTube masih belum final (default `"22"`, belum
  dikonfirmasi user) — sama seperti status sejak poin 8.
- Investigasi root cause "Archive.org fiktif di manifest" ditunda/di-skip
  atas keputusan user, fokus ke perbaikan query saja.

## 12. Sesi lanjutan (22 September 2026) — Hermes plugin stack + pivot Cloudflare Workers AI

### Hermes plugin stack (diputuskan, sudah dikirim ke user untuk diinstall)
Tiga plugin dipasang di Hermes Agent (bukan di repo OpenMontage sendiri —
ini setting Hermes CLI, lintas-repo):
1. **`obra/superpowers`** — framework skill agentic yang menegakkan alur
   brainstorming → writing-plans → TDD (RED-GREEN-REFACTOR) → code review →
   verification-before-completion. Install: `hermes plugins install
   obra/superpowers --enable`, restart session Hermes setelahnya. Catatan:
   Hermes tidak punya post-compaction hook — kalau sesi panjang ter-compact
   melewati turn pertama, bootstrap skill ini hilang; kalau skill berhenti
   ter-trigger, mulai sesi baru.
2. **`DietrichGebert/ponytail`** — anti-over-engineering (YAGNI ladder: perlu
   ada gak → reuse → stdlib → native → dependency → satu baris → minimum
   yang perlu). Diukur -54% LOC, -20% cost, -27% waktu vs baseline tanpa
   skill, tanpa tradeoff safety. Install: `hermes plugins install
   DietrichGebert/ponytail --enable`. Saling melengkapi dengan caveman
   (caveman memendekkan apa yang agent BILANG, ponytail memendekkan apa
   yang agent BANGUN).
3. **`JuliusBrussee/caveman`** (skill saja, bukan proxy) — balasan agent
   lebih ringkas, ~65% lebih sedikit output token rata-rata (code/command/
   path tidak pernah dipendekkan). Install: `npx skills add
   JuliusBrussee/caveman`. Ketik `/caveman` manual kalau tidak auto-aktif.
   Varian proxy (`caveman hermes`) SENGAJA di-skip dulu — overhead setup
   lebih besar untuk workflow mobile-only, bisa direvisit nanti.
- Dipertimbangkan tapi ditunda: `Egonex-AI/Understand-Anything` (tool
  knowledge-graph/dashboard codebase) — berguna kalau `tools/` sudah makin
  susah dinavigasi, belum diinstall.
- Dipertimbangkan dan di-skip: `sickn33/agentic-awesome-skills` (katalog
  2.400+ skill) — terlalu luas/tidak terverifikasi untuk kebutuhan
  sekarang, juga terlalu berat token untuk di-browse penuh dalam sesi.

### Pivot: Cloudflare Workers AI image generation (menggantikan stock sources)
- **Keputusan**: setelah render test pertama (poin 11) mengecewakan karena
  footage stock salah/tidak relevan, asset sourcing untuk "The Forgotten
  Shadows" (niche dark history) pindah total ke Cloudflare Workers AI image
  generation — **full replacement**, semua stock source lama (Wikimedia/
  archive.org/Pexels/Pixabay/dst di `tools/video/stock_sources/`) TIDAK
  dipertahankan sebagai fallback, akan dimatikan.
- **Motivasi**: pola yang sama sedang/sudah dites di project WealthVault
  (branch Cloudflare image-gen sendiri di `riy389/wealthvault-agent`).
  Dikonfirmasi via `get_file_contents`: `cloudflare_beats.py` sudah ADA di
  branch `main` WealthVault — pivot ini TIDAK LAGI diblokir menunggu
  WealthVault (blocker itu sudah selesai per sesi ini).
- **Model & API yang dikonfirmasi dari source WealthVault**:
  `@cf/black-forest-labs/flux-2-klein-4b`, dipanggil via multipart/
  form-data POST ke
  `https://api.cloudflare.com/client/v4/accounts/{account_id}/ai/run/{model}`,
  parameter `prompt`/`width`/`height`, response bisa JSON (`result.image`
  base64) atau raw bytes tergantung `Content-Type`. Resolusi WealthVault:
  768x1344 (rasio 9:16), ~117 neuron/gambar.
- **Budget neuron Cloudflare**: 10.000/hari, **shared satu pool** antara
  WealthVault dan OpenMontage (bukan kuota terpisah per project) — sama
  seperti pola sharing Telegram bot dan YouTube OAuth Client ID/Secret
  sebelumnya. Konsekuensi: pemakaian di satu project mengurangi budget
  project lain di hari yang sama.
- **Sudah dikerjakan & di-push ke `main` OpenMontage** (sesi ini):
  1. `tools/graphics/cloudflare_image.py` (commit `444bec7`) — tool baru,
     mengikuti pola `BaseTool` yang sama persis dengan `flux_image.py`
     (`tools/graphics/`), tier `GENERATE`, capability `image_generation`,
     provider `cloudflare`. Baca kredensial dari `CLOUDFLARE_ACCOUNT_ID`/
     `CLOUDFLARE_API_TOKEN`. `get_status()` return `UNAVAILABLE` kalau
     salah satu env var kosong. `estimate_cost()` selalu `0.0` (dibilling
     neuron, bukan USD). Auto-discovered oleh `tool_registry.py`
     (`pkgutil.walk_packages`) — tidak perlu registrasi manual.
  2. `.env.example` (commit `eeef082`) — ditambah section baru
     `--- Cloudflare Workers AI ---` (ditaruh setelah section "Image +
     video gateway"/fal.ai, sebelum MiniMax) berisi `CLOUDFLARE_API_TOKEN`
     dan `CLOUDFLARE_ACCOUNT_ID`.
- **Keputusan penamaan env var**: dipakai `CLOUDFLARE_ACCOUNT_ID`/
  `CLOUDFLARE_API_TOKEN` (SAMA PERSIS dengan nama variable di WealthVault),
  BUKAN `CF_ACCOUNT_ID`/`CF_API_TOKEN` yang sempat disebut sebagai
  kemungkinan nama di sesi sebelumnya (poin 11 belum ditulis soal ini,
  tapi ini koreksi dari rencana awal) — supaya kredensial Cloudflare yang
  sama bisa dipakai lintas `.env` kedua project tanpa perlu mapping nama.
- **`.env` di Codespaces OpenMontage sudah diisi** — `CLOUDFLARE_API_TOKEN`
  dan `CLOUDFLARE_ACCOUNT_ID` dikonfirmasi user TERISI via command grep+awk
  di atas (bukan value di-cat mentah, sesuai aturan poin 9/10). Tool
  `cloudflare_image` sekarang `AVAILABLE` di Codespace, tinggal `git pull`
  untuk narik `cloudflare_image.py` + `.env.example` terbaru dari `main`.
- **BELUM dikerjakan (next action)**:
  1. Matikan/nonaktifkan stock sources lama di `tools/video/stock_sources/`
     (full replacement, bukan dipertahankan sebagai fallback) — belum
     diputuskan detail teknisnya (hapus file vs disable via config/
     priority vs comment out registrasi) di sesi ini, perlu dibahas
     sebelum eksekusi.
  2. Wiring `cloudflare_image` ke stage pipeline yang relevan (asset stage
     `documentary-montage`, kemungkinan juga pipeline lain) — menggantikan
     panggilan ke stock sources/`flux_image` yang ada sekarang. Belum
     disentuh sama sekali di sesi ini, murni tool baru + env var dulu.
