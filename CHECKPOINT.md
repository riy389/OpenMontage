# 📍 CHECKPOINT — Baca file ini duluan di chat baru

Ini bukan dokumentasi resmi OpenMontage. Ini catatan pribadi user (riy389) —
ringkasan lengkap semua yang sudah dibahas/diputuskan sampai 5 September 2026,
supaya chat baru tidak perlu baca ulang AGENT_GUIDE.md dkk dari nol untuk
hal-hal yang sudah dipahami. Cukup baca file ini.

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

## 2. Status fork ini per 5 September 2026

- Branch aktif: `main`.
- **Perubahan kode yang SUDAH masuk ke repo ini** (lihat poin 8 untuk detail):
  - `CHECKPOINT.md` (file ini)
  - `skills/meta/publish-distribution.md` — SUDAH di-push
- **Belum `make setup`, belum `.env` diisi.** Repo baru sejauh ini baru
  disentuh lewat GitHub API (baca file + tulis dokumentasi), belum pernah
  benar-benar dijalankan `make setup` di Codespace.
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
  (stage `publish` ada di semua pipeline versi "v2.0" — mayoritas pipeline).
- **12 pipeline** ada di `pipeline_defs/*.yaml`. **Hermes yang memilih**
  pipeline berdasarkan permintaan user — user TIDAK wajib tahu nama pipeline
  duluan. Kalau ambigu, Hermes yang tanya balik.
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
  lewat GitHub Actions + cron-job.org. OpenMontage sengaja tidak menyediakan
  ini secara default — sesi ini sedang membangunnya (lihat poin 8).

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

**A. Tool baru — BELUM DITULIS, rencana ditulis SEKALI, otomatis kedeteksi ke SEMUA pipeline:**
```
tools/publishers/telegram_notify.py   # belum ada
tools/publishers/youtube_upload.py    # belum ada
```
- Alasan cukup sekali tulis: `tool_registry.py` melakukan auto-discovery
  lewat `pkgutil.walk_packages()` yang scan seluruh isi folder `tools/` —
  tidak perlu didaftarkan manual di file lain mana pun. Begitu file ada dan
  class-nya inherit `BaseTool`, otomatis tersedia untuk semua pipeline.
- Keduanya WAJIB inherit `tools/base_tool.py` → `BaseTool`, dengan minimal:
  - `capability = "publish"`
  - `dependencies = ["env:TELEGRAM_BOT_TOKEN", "env:TELEGRAM_CHAT_ID"]`
    (untuk Telegram) atau env var YouTube yang setara untuk `youtube_upload`
  - Field `dependencies` dengan prefix `env:` ini otomatis membuat sistem
    preflight (`provider_menu_summary()`) mendeteksi & menawarkan setup ke
    user kalau env var belum diisi — tidak perlu logic manual tambahan.

**B. Meta skill — ✅ SUDAH DITULIS DAN DI-PUSH:**
```
skills/meta/publish-distribution.md   # SUDAH ADA — commit e6fd16a
```
Isi lengkapnya (5 langkah, gaya sama seperti `checkpoint-protocol.md`):
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
   - **Telegram = `status: "pending_review"`**, BUKAN `"published"` — video
     sedang menunggu keputusan manusia di Telegram.
   - **YouTube upload baru boleh jalan SETELAH approval Telegram diterima**
     (atau langsung kalau user memang skip Telegram review untuk project
     itu) — YouTube sukses = `status: "published"`, isi `video_id`, `url`,
     `visibility`.
   - Field platform-spesifik yang tidak masuk skema (misal `chat_id`,
     `message_id`) TIDAK boleh ditaruh di `entries[]` — kalau perlu disimpan,
     masuk ke `metadata` di root artifact (itu bagian yang tidak dibatasi
     skema).
5. **Checkpoint stage `publish`** pakai `write_checkpoint()` — approval
   Telegram dan approval gate stage `publish` itu **DUA KEPUTUSAN TERPISAH**:
   dapat thumbs-up di Telegram TIDAK otomatis memenuhi gate stage `publish`.
   Hermes tetap wajib konfirmasi eksplisit ke user sebelum menulis
   `status="completed", human_approved=True`.

**C. Rujukan 1-2 baris di TIAP 11 file `publish-director.md` — BELUM DIKERJAKAN:**
- Lokasi: `skills/pipelines/<pipeline>/publish-director.md` — ADA SATU FILE
  TERPISAH PER PIPELINE (bukan satu file bersama). Sudah dibandingkan
  langsung: `explainer/publish-director.md` (fokus SEO+thumbnail+chapters,
  pakai `export_bundle`) vs `cinematic/publish-director.md` (fokus
  hero/derivative/teaser cut, TIDAK sebut `export_bundle` sama sekali) —
  strukturnya beda total per pipeline.
- **Tidak ada precedent shared-reference antar publish-director sebelum
  ini** — jadi baris rujukan baru ke `skills/meta/publish-distribution.md`
  ini perlu ditambah manual satu-satu di semua 11 file (bukan otomatis
  nyambung hanya dengan bikin meta skill-nya saja).
- Pola rujukannya rencana:
  ```
  ## Distribution
  After packaging, read `skills/meta/publish-distribution.md` for optional
  Telegram/YouTube distribution.
  ```

### Progress checklist (update per checkpoint ini)
- [x] Baca `schemas/artifacts/publish_log.schema.json`
- [x] Baca `lib/checkpoint.py` — pahami `write_checkpoint`, gate
      enforcement, prasyarat berurutan
- [x] Tulis & push `skills/meta/publish-distribution.md`
- [ ] Tulis `tools/publishers/telegram_notify.py`
- [ ] Tulis `tools/publishers/youtube_upload.py`
- [ ] Tambah rujukan Distribution di 11 file `publish-director.md`
- [ ] `make setup` + isi `.env` di Codespace (belum dilakukan sama sekali)
- Semua ini masih tahap **DISKUSI/PERENCANAAN + dokumentasi**. Baru dua file
  markdown (`CHECKPOINT.md`, `publish-distribution.md`) yang sudah masuk
  repo — belum ada satu pun file `.py` tool baru yang ditulis.

## 9. Key learnings / aturan permanen untuk sesi berikutnya

- **User eksplisit melarang asumsi.** Wajib riset/baca source langsung
  sebelum menjawab pertanyaan teknis (nama produk, arsitektur, kemampuan
  tool/software) — bukan cuma untuk OpenMontage, ini aturan permanen di
  semua topik. Kalau ditanya dan belum tahu, baca dulu baru jawab; jangan
  tanya izin "mau dibaca dulu gak" — user sudah kasih akses MCP GitHub
  supaya langsung dipakai.
- Fork GitHub independen total dari upstream — perubahan di fork tidak
  memengaruhi repo asal, kecuali PR yang di-approve manual.
- `search_repositories` GitHub API secara default **menyembunyikan fork**
  dari hasil pencarian biasa — jangan simpulkan "tidak ada" hanya dari
  situ; cek langsung ke akun/URL kalau hasil kosong tapi kamu tahu itu ada.
- Repo ini (`OpenMontage`) dan `wealthvault-agent` itu dua konteks terpisah
  — jangan campur checkpoint/pembahasan keduanya.
- File ini (`CHECKPOINT.md`) murni untuk fase DEVELOPMENT, dibaca MANUAL per
  sesi kerja lanjutan — bukan bagian dari alur produksi video permanen.
  Begitu Telegram+YouTube publisher selesai dan sudah nempel di
  `publish-distribution.md`/`publish-director.md`, isi checkpoint ini jadi
  usang dan boleh dihapus/ditandai selesai. Instruksi cara pakai yang
  PERMANEN letaknya di `skills/meta/publish-distribution.md`, bukan di sini.
