# Substance Painter MCP

[![Tests](https://github.com/samlehoy/SubstancePainterMCP/actions/workflows/test.yml/badge.svg)](https://github.com/samlehoy/SubstancePainterMCP/actions/workflows/test.yml)
[![Painter 12.1+](https://img.shields.io/badge/Painter-12.1%2B-99E83F)](https://www.adobe.com/products/substance3d/apps/painter.html)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

**English** · [Bahasa Indonesia](#bahasa-indonesia)

## English

Let AI assistants such as Claude Code, Claude Desktop, Antigravity, and OpenCode work in your open Adobe Substance 3D Painter project: inspect it, build layers, bake, and export textures.

> Independent community project, not affiliated with or endorsed by Adobe.

### Install

You need **Substance 3D Painter 12.1 or newer** and **[uv](https://docs.astral.sh/uv/)**:

```bash
brew install uv              # macOS
winget install astral-sh.uv  # Windows
```

**1. Run the installer.**

```bash
uvx --from git+https://github.com/samlehoy/SubstancePainterMCP substance-painter-mcp install
```

This always runs the newest installer, and it pins your assistants to that exact release. Run it again later to upgrade.

It first asks for a language (English or Bahasa Indonesia), then walks you through three steps:

- **Assistants**: move with ↑/↓, press Space to select each assistant you use, then press Enter.
- **Work folder**: drag the folder with your meshes and reference images from Finder or File Explorer into the terminal window, then press Enter. You can also type a path (Tab completes). Projects, backups, and exports are saved there too.
- **Review**: check the changes and press Y. Existing config files are backed up first, and only the `substance-painter` entry is changed.

<details>
<summary>Example session (macOS)</summary>

```text
╭───────────────────────────────────────────╮
│  Substance Painter MCP · installer 1.1.1  │
╰───────────────────────────────────────────╯
✔ Painter 12.1.5 found

Step 1 of 3 · Assistants
? Which assistants should use Substance Painter? (↑↓ move · space select · enter confirm)
   ● Claude Code
   ○ Claude Desktop  not detected
 » ● Antigravity
   ○ OpenCode
```

After selecting, then dragging a folder in and pressing Y:

```text
Step 1 of 3 · Assistants
  ✔ Claude Code, Antigravity

Step 2 of 3 · Work folder
  The assistant can only read and write files inside this folder:
  meshes, reference images, projects, backups, and exports.

  Tip: drag the folder from Finder into this window, then press Enter.
       Or type a path (Tab completes). Leave it empty for ~/SubstanceProjects.
  ✔ ~/Documents/project/My Forge · 1 mesh, 4 images

Step 3 of 3 · Review
  Claude Code    claude mcp add -s user
  Antigravity    ~/.gemini/config/mcp_config.json (backed up first)
  Work folder    ~/Documents/project/My Forge

  ✔ Claude Code
  ✔ Antigravity  backup: mcp_config.json.bak-20261013-113701

Next steps
  1. Quit Painter completely, then start it with remote scripting:
     open -a "/Applications/Adobe Substance 3D Painter/Adobe Substance 3D Painter.app" --args --enable-remote-scripting
  2. Restart your assistant and ask: "Check the Substance Painter status."
```

</details>

**2. Start Painter with remote scripting.** Quit Painter completely first; if it is already running, the flag is ignored.

```bash
# macOS
open -a "/Applications/Adobe Substance 3D Painter/Adobe Substance 3D Painter.app" --args --enable-remote-scripting
```

```powershell
# Windows (or add the flag to your Painter shortcut's Target field)
& "C:\Program Files\Adobe\Adobe Substance 3D Painter\Adobe Substance 3D Painter.exe" --enable-remote-scripting
```

**3. Restart your assistant and try it:** *"Check the Substance Painter status."*

<details>
<summary>Set up an assistant by hand instead</summary>

Every MCP client runs the same command; only the config format differs.

**Claude Code**

```bash
claude mcp add substance-painter -s user \
  -e SP_MCP_EXPORT_ROOTS="$HOME/SubstanceProjects" \
  -e SP_MCP_PROJECT_ROOTS="$HOME/SubstanceProjects" \
  -- uvx --from git+https://github.com/samlehoy/SubstancePainterMCP@v1.1.0 substance-painter-mcp
```

**Claude Desktop, Cursor, Antigravity** (`mcpServers` format; Antigravity uses `~/.gemini/config/mcp_config.json`)

```json
{
  "mcpServers": {
    "substance-painter": {
      "command": "uvx",
      "args": ["--from", "git+https://github.com/samlehoy/SubstancePainterMCP@v1.1.0", "substance-painter-mcp"],
      "env": {
        "SP_MCP_EXPORT_ROOTS": "/path/to/SubstanceProjects",
        "SP_MCP_PROJECT_ROOTS": "/path/to/SubstanceProjects"
      }
    }
  }
}
```

**OpenCode** (`opencode.json`)

```json
{
  "$schema": "https://opencode.ai/config.json",
  "mcp": {
    "substance-painter": {
      "type": "local",
      "command": ["uvx", "--from", "git+https://github.com/samlehoy/SubstancePainterMCP@v1.1.0", "substance-painter-mcp"],
      "environment": {
        "SP_MCP_EXPORT_ROOTS": "/path/to/SubstanceProjects",
        "SP_MCP_PROJECT_ROOTS": "/path/to/SubstanceProjects"
      },
      "timeout": 60000
    }
  }
}
```

If a GUI app cannot find `uvx`, use its absolute path (`which uvx` / `where uvx`). The first run downloads the package and can take about 10 seconds, so raise short client timeouts as in the OpenCode example, or run the command once in a terminal first.

</details>

### Uninstall

```bash
uvx --from git+https://github.com/samlehoy/SubstancePainterMCP substance-painter-mcp uninstall
```

It finds `substance-painter` in Claude Code (user scope), Claude Desktop, Antigravity, and OpenCode, shows what it will remove, and asks for confirmation. Only that entry is removed, config files are backed up first, and your work folder and projects are not touched. To also delete the cached package, run `uv cache clean substance-painter-mcp`. If you added the server to a single Claude Code project instead, run `claude mcp remove substance-painter -s local` in that folder.

### What it can do

79 tools, including:

- **Inspect**: project info, layer tree, Texture Sets, resources, export presets, project audit.
- **Build layers**: Fill, Paint, and Group layers, channels, masks, Smart Materials and Smart Masks, procedural parameters, and multi-layer recipes with bitmaps and bitmap masks that roll back if a step fails.
- **Batch work**: import several images, set several channels (bitmaps or values), or delete several layers in one call.
- **Bake**: inspect and configure bakers, assign high-poly meshes, preflight, and batch-bake with cancellation.
- **Export**: preview exact file names, then export textures with presets or engine profiles (Unity, Unreal, Blender, VRChat).
- **Manage projects**: create from a mesh, open, save, back up, reload meshes, import images as resources.

See the [full tool list](docs/TOOLS.md).

### Safety

- **Work folders.** The server reads and writes files only inside the folders you approve (`SP_MCP_*_ROOTS`). Features without an approved folder stay off.
- **Confirmation.** Baking, saving, importing, and opening or creating projects require explicit confirmation. Switching away from a project with unsaved work requires a backup first.
- **No arbitrary code.** Running raw Python inside Painter is disabled unless you set `SP_MCP_ALLOW_EXECUTE_PYTHON=1`.
- **Local only.** Never expose Painter's remote-scripting port (`60041`) to other machines.

Details: [Configuration and safety](docs/CONFIGURATION.md).

### Troubleshooting

| Problem | Fix |
|---|---|
| "Cannot connect to Painter at localhost:60041" | Quit Painter completely and start it with `--enable-remote-scripting` (step 2). |
| The assistant shows no Painter tools | Restart the assistant after installing. |
| Geometry masks, snapshots, or recipes fail | Update Painter to 12.1 or newer. |
| "Path is outside SP_MCP_…_ROOTS" | Move the file into your work folder, or run the installer again with another folder. |

To check that Painter is listening, run `lsof -nP -iTCP:60041 -sTCP:LISTEN` (macOS) or `Get-NetTCPConnection -LocalPort 60041` (PowerShell).

### Learn more

- [Tool reference](docs/TOOLS.md) · [Configuration and safety](docs/CONFIGURATION.md) · [Development and testing](docs/DEVELOPMENT.md)
- Guides: [layer recipes](docs/RECIPES.md) (with a [VRChat outfit example](examples/recipes/vrchat_outfit.json)), [procedural sources and baking](docs/PROCEDURAL_AND_BAKING.md), [production baking](docs/PRODUCTION_BAKING.md), [resource imports](docs/RESOURCE_INGESTION.md), [project lifecycle](docs/PROJECT_LIFECYCLE.md)
- [Changelog](CHANGELOG.md) · [Roadmap](docs/ROADMAP.md)

Tested live with Painter 12.1.1 on Windows and 12.1.5 on macOS (Apple silicon). Automated tests run on Windows and macOS for every push.

### License

MIT. See [LICENSE](LICENSE).

---

## Bahasa Indonesia

[English](#english) · **Bahasa Indonesia**

Biarkan asisten AI seperti Claude Code, Claude Desktop, Antigravity, dan OpenCode bekerja langsung di project Adobe Substance 3D Painter yang sedang terbuka: memeriksa project, membuat layer, bake, dan export texture.

> Proyek komunitas independen, tidak berafiliasi dengan Adobe dan tidak didukung oleh Adobe.

### Instalasi

Yang dibutuhkan: **Substance 3D Painter 12.1 atau yang lebih baru** dan **[uv](https://docs.astral.sh/uv/)**:

```bash
brew install uv              # macOS
winget install astral-sh.uv  # Windows
```

**1. Jalankan installer.**

```bash
uvx --from git+https://github.com/samlehoy/SubstancePainterMCP substance-painter-mcp install
```

Perintah ini selalu menjalankan installer terbaru, dan installer mengunci asisten Anda ke rilis tersebut. Jalankan lagi nanti untuk update.

Installer menanyakan bahasa dulu (English atau Bahasa Indonesia), lalu memandu Anda lewat tiga langkah:

- **Asisten**: pindah dengan ↑/↓, tekan Spasi untuk memilih setiap asisten yang Anda pakai, lalu tekan Enter.
- **Folder kerja**: seret folder berisi mesh dan gambar referensi Anda dari Finder atau File Explorer ke jendela terminal, lalu tekan Enter. Anda juga bisa mengetik path-nya (Tab melengkapi). Project, backup, dan hasil export juga disimpan di folder ini.
- **Tinjau**: periksa perubahannya, lalu tekan Y. File config yang sudah ada di-backup dulu, dan hanya entry `substance-painter` yang diubah.

<details>
<summary>Contoh sesi (macOS)</summary>

```text
╭───────────────────────────────────────────╮
│  Substance Painter MCP · instalasi 1.1.1  │
╰───────────────────────────────────────────╯
✔ Painter 12.1.5 ditemukan

Langkah 1 dari 3 · Asisten
? Asisten mana yang akan memakai Substance Painter? (↑↓ pindah · spasi pilih · enter lanjut)
   ● Claude Code
   ○ Claude Desktop  tidak terdeteksi
 » ● Antigravity
   ○ OpenCode
```

Setelah memilih asisten, menyeret folder, lalu menekan Y:

```text
Langkah 1 dari 3 · Asisten
  ✔ Claude Code, Antigravity

Langkah 2 dari 3 · Folder kerja
  Asisten hanya bisa membaca dan menulis file di dalam folder ini:
  mesh, gambar referensi, project, backup, dan hasil export.

  Tips: seret folder dari Finder ke jendela ini, lalu tekan Enter.
        Atau ketik path-nya (Tab melengkapi). Kosongkan untuk memakai ~/SubstanceProjects.
  ✔ ~/Documents/project/My Forge · 1 mesh, 4 gambar

Langkah 3 dari 3 · Tinjau
  Claude Code    claude mcp add -s user
  Antigravity    ~/.gemini/config/mcp_config.json (di-backup dulu)
  Folder kerja   ~/Documents/project/My Forge

  ✔ Claude Code
  ✔ Antigravity  backup: mcp_config.json.bak-20261013-113701

Langkah berikutnya
  1. Tutup Painter sepenuhnya, lalu buka lagi dengan remote scripting:
     open -a "/Applications/Adobe Substance 3D Painter/Adobe Substance 3D Painter.app" --args --enable-remote-scripting
  2. Restart asisten Anda, lalu minta: "Cek status Substance Painter."
```

</details>

**2. Buka Painter dengan remote scripting.** Tutup Painter sepenuhnya dulu; kalau Painter masih berjalan, flag ini diabaikan.

```bash
# macOS
open -a "/Applications/Adobe Substance 3D Painter/Adobe Substance 3D Painter.app" --args --enable-remote-scripting
```

```powershell
# Windows (atau tambahkan flag ini ke kolom Target pada shortcut Painter)
& "C:\Program Files\Adobe\Adobe Substance 3D Painter\Adobe Substance 3D Painter.exe" --enable-remote-scripting
```

**3. Restart asisten Anda, lalu coba:** *"Cek status Substance Painter."*

<details>
<summary>Atau atur asisten secara manual</summary>

Semua MCP client menjalankan perintah yang sama; yang berbeda hanya format config-nya.

**Claude Code**

```bash
claude mcp add substance-painter -s user \
  -e SP_MCP_EXPORT_ROOTS="$HOME/SubstanceProjects" \
  -e SP_MCP_PROJECT_ROOTS="$HOME/SubstanceProjects" \
  -- uvx --from git+https://github.com/samlehoy/SubstancePainterMCP@v1.1.0 substance-painter-mcp
```

**Claude Desktop, Cursor, Antigravity** (format `mcpServers`; Antigravity memakai `~/.gemini/config/mcp_config.json`)

```json
{
  "mcpServers": {
    "substance-painter": {
      "command": "uvx",
      "args": ["--from", "git+https://github.com/samlehoy/SubstancePainterMCP@v1.1.0", "substance-painter-mcp"],
      "env": {
        "SP_MCP_EXPORT_ROOTS": "/path/to/SubstanceProjects",
        "SP_MCP_PROJECT_ROOTS": "/path/to/SubstanceProjects"
      }
    }
  }
}
```

**OpenCode** (`opencode.json`)

```json
{
  "$schema": "https://opencode.ai/config.json",
  "mcp": {
    "substance-painter": {
      "type": "local",
      "command": ["uvx", "--from", "git+https://github.com/samlehoy/SubstancePainterMCP@v1.1.0", "substance-painter-mcp"],
      "environment": {
        "SP_MCP_EXPORT_ROOTS": "/path/to/SubstanceProjects",
        "SP_MCP_PROJECT_ROOTS": "/path/to/SubstanceProjects"
      },
      "timeout": 60000
    }
  }
}
```

Kalau aplikasi GUI tidak menemukan `uvx`, pakai path absolutnya (`which uvx` / `where uvx`). Run pertama mengunduh paket dan bisa makan waktu sekitar 10 detik. Karena itu, naikkan timeout client yang terlalu pendek seperti pada contoh OpenCode, atau jalankan perintahnya sekali di terminal lebih dulu.

</details>

### Hapus instalasi

```bash
uvx --from git+https://github.com/samlehoy/SubstancePainterMCP substance-painter-mcp uninstall
```

Perintah ini mencari `substance-painter` di Claude Code (scope user), Claude Desktop, Antigravity, dan OpenCode, menampilkan apa yang akan dihapus, lalu meminta konfirmasi. Hanya entry itu yang dihapus, file config di-backup dulu, dan folder kerja serta project Anda tidak disentuh. Untuk menghapus paket dari cache juga, jalankan `uv cache clean substance-painter-mcp`. Kalau Anda menambahkan server hanya ke satu project Claude Code, jalankan `claude mcp remove substance-painter -s local` di folder project tersebut.

### Kemampuan

79 tool, di antaranya:

- **Periksa**: info project, struktur layer, Texture Set, resource, preset export, dan audit project.
- **Bangun layer**: layer Fill, Paint, dan Group, channel, mask, Smart Material dan Smart Mask, parameter procedural, serta recipe multi-layer dengan bitmap dan mask bitmap yang otomatis dibatalkan kalau ada langkah yang gagal.
- **Kerja batch**: import beberapa gambar, atur beberapa channel (bitmap atau nilai), atau hapus beberapa layer dalam satu panggilan.
- **Bake**: periksa dan atur baker, pasang mesh high-poly, preflight, dan batch bake yang bisa dibatalkan.
- **Export**: lihat dulu nama file yang akan dibuat, lalu export texture dengan preset atau profil engine (Unity, Unreal, Blender, VRChat).
- **Kelola project**: buat project dari mesh, buka, simpan, backup, muat ulang mesh, dan import gambar sebagai resource.

Lihat [daftar lengkap tool](docs/TOOLS.md).

### Keamanan

- **Folder kerja.** Server hanya membaca dan menulis file di dalam folder yang Anda izinkan (`SP_MCP_*_ROOTS`). Fitur yang foldernya belum diizinkan tetap nonaktif.
- **Konfirmasi.** Bake, simpan, import, serta membuka atau membuat project butuh konfirmasi eksplisit. Sebelum pindah dari project yang punya perubahan belum disimpan, backup wajib dibuat dulu.
- **Tanpa kode bebas.** Menjalankan Python mentah di dalam Painter dinonaktifkan, kecuali Anda mengatur `SP_MCP_ALLOW_EXECUTE_PYTHON=1`.
- **Hanya lokal.** Jangan pernah membuka port remote scripting Painter (`60041`) ke komputer lain.

Detail: [Konfigurasi dan keamanan](docs/CONFIGURATION.md).

### Mengatasi masalah

| Masalah | Solusi |
|---|---|
| "Cannot connect to Painter at localhost:60041" | Tutup Painter sepenuhnya, lalu buka dengan `--enable-remote-scripting` (langkah 2). |
| Asisten tidak menampilkan tool Painter | Restart asisten setelah instalasi. |
| Geometry mask, snapshot, atau recipe gagal | Update Painter ke 12.1 atau yang lebih baru. |
| "Path is outside SP_MCP_…_ROOTS" | Pindahkan file ke folder kerja Anda, atau jalankan installer lagi dengan folder lain. |

Untuk mengecek apakah Painter sudah menerima koneksi, jalankan `lsof -nP -iTCP:60041 -sTCP:LISTEN` (macOS) atau `Get-NetTCPConnection -LocalPort 60041` (PowerShell).

### Pelajari lebih lanjut

Dokumentasi lanjutan tersedia dalam bahasa Inggris:

- [Referensi tool](docs/TOOLS.md) · [Konfigurasi dan keamanan](docs/CONFIGURATION.md) · [Pengembangan dan pengujian](docs/DEVELOPMENT.md)
- Panduan: [layer recipe](docs/RECIPES.md) (dengan [contoh outfit VRChat](examples/recipes/vrchat_outfit.json)), [sumber procedural dan baking](docs/PROCEDURAL_AND_BAKING.md), [baking untuk produksi](docs/PRODUCTION_BAKING.md), [import resource](docs/RESOURCE_INGESTION.md), [siklus hidup project](docs/PROJECT_LIFECYCLE.md)
- [Changelog](CHANGELOG.md) · [Roadmap](docs/ROADMAP.md)

Sudah diuji langsung dengan Painter 12.1.1 di Windows dan 12.1.5 di macOS (Apple silicon). Test otomatis berjalan di Windows dan macOS untuk setiap push.

### Lisensi

MIT. Lihat [LICENSE](LICENSE).
