"""Installer text in English and Bahasa Indonesia, keyed by message id."""

MESSAGES: dict[str, tuple[str, str]] = {
    # key: (English, Bahasa Indonesia)
    "title.installer": ("installer", "instalasi"),
    "title.uninstaller": ("uninstaller", "hapus instalasi"),
    "step": ("Step {number} of 3", "Langkah {number} dari 3"),
    "step.assistants": ("Assistants", "Asisten"),
    "step.folder": ("Work folder", "Folder kerja"),
    "step.review": ("Review", "Tinjau"),
    "uv.missing": ("✘ uv is required. ", "✘ uv diperlukan. "),
    "uv.how": (
        "Install it with `brew install uv` (macOS) or `winget install astral-sh.uv` (Windows), "
        "then run this again.",
        "Pasang dengan `brew install uv` (macOS) atau `winget install astral-sh.uv` (Windows), "
        "lalu jalankan lagi.",
    ),
    "painter.missing": (
        "Substance 3D Painter was not detected; install 12.1 or newer.",
        "Substance 3D Painter tidak terdeteksi; pasang versi 12.1 atau yang lebih baru.",
    ),
    "painter.old": (
        "Painter {version} found; 12.1 or newer is required for every tool.",
        "Painter {version} ditemukan; semua tool butuh versi 12.1 atau yang lebih baru.",
    ),
    "painter.ok": ("Painter {version} found", "Painter {version} ditemukan"),
    "clients.question": (
        "Which assistants should use Substance Painter?",
        "Asisten mana yang akan memakai Substance Painter?",
    ),
    "clients.instruction": (
        "(↑↓ move · space select · enter confirm)",
        "(↑↓ pindah · spasi pilih · enter lanjut)",
    ),
    "clients.none": ("Select at least one with space", "Pilih minimal satu dengan spasi"),
    "clients.numbers": ("Numbers, e.g. 1,3", "Nomor, misalnya 1,3"),
    "clients.invalid": ("Enter numbers from: {numbers}", "Masukkan nomor dari: {numbers}"),
    "note.installed": ("installed", "terpasang"),
    "note.not_detected": ("not detected", "tidak terdeteksi"),
    "note.no_claude": ("claude command not found", "perintah claude tidak ditemukan"),
    "folder.explain": (
        "The assistant can only read and write files inside this folder:",
        "Asisten hanya bisa membaca dan menulis file di dalam folder ini:",
    ),
    "folder.contents": (
        "meshes, reference images, projects, backups, and exports.",
        "mesh, gambar referensi, project, backup, dan hasil export.",
    ),
    "folder.tip": ("Tip: ", "Tips: "),
    "folder.drag": (
        "drag the folder from {file_manager} into this window, then press Enter.",
        "seret folder dari {file_manager} ke jendela ini, lalu tekan Enter.",
    ),
    "folder.type": (
        "Or type a path (Tab completes). Leave it empty for {suggestion}.",
        "Atau ketik path-nya (Tab melengkapi). Kosongkan untuk memakai {suggestion}.",
    ),
    "folder.file_manager": ("your file manager", "pengelola file Anda"),
    "folder.prompt": ("Folder", "Folder"),
    "folder.is_file": ("That is a file; choose a folder", "Itu file, bukan folder"),
    "folder.no_parent": ("Its parent folder does not exist", "Folder induknya tidak ada"),
    "folder.create": ("Create {folder}?", "Buat folder {folder}?"),
    "folder.broad": (
        "The assistant could read and write everything in {folder}. Use it anyway?",
        "Asisten akan bisa membaca dan menulis semua isi {folder}. Tetap pakai folder ini?",
    ),
    "folder.empty": (
        "empty so far; put your meshes and images here",
        "masih kosong; taruh mesh dan gambar Anda di sini",
    ),
    "review.backed_up": ("backed up first", "di-backup dulu"),
    "review.new_file": ("new file", "file baru"),
    "review.folder": ("Work folder", "Folder kerja"),
    "review.confirm": ("Install now?", "Pasang sekarang?"),
    "nothing_changed": ("Nothing was changed.", "Tidak ada yang diubah."),
    "backup": ("backup: {name}", "backup: {name}"),
    "next.title": ("Next steps", "Langkah berikutnya"),
    "next.painter": (
        "1. Quit Painter completely, then start it with remote scripting:",
        "1. Tutup Painter sepenuhnya, lalu buka lagi dengan remote scripting:",
    ),
    "next.ask": (
        '2. Restart your assistant and ask: "Check the Substance Painter status."',
        '2. Restart asisten Anda, lalu minta: "Cek status Substance Painter."',
    ),
    "uninstall.none": (
        "substance-painter is not configured in Claude Code (user scope), Claude Desktop, "
        "Antigravity, or OpenCode.",
        "substance-painter tidak terpasang di Claude Code (scope user), Claude Desktop, "
        "Antigravity, maupun OpenCode.",
    ),
    "uninstall.found": ("Found substance-painter in:", "substance-painter ditemukan di:"),
    "uninstall.confirm": ("Remove it from these assistants?", "Hapus dari asisten-asisten ini?"),
    "uninstall.untouched": (
        "Your work folder and Painter projects were not touched. Restart your assistants.",
        "Folder kerja dan project Painter Anda tidak disentuh. Restart asisten Anda.",
    ),
    "uninstall.cache": (
        "To also delete the cached package: uv cache clean substance-painter-mcp",
        "Untuk menghapus paket dari cache juga: uv cache clean substance-painter-mcp",
    ),
    "cancelled": ("Cancelled; nothing further was changed.", "Dibatalkan; tidak ada perubahan lagi."),
}
