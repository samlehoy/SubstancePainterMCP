"""Interactive installer that registers this server with MCP clients, or removes it.

Run with: uvx --from git+https://github.com/samlehoy/SubstancePainterMCP@vX.Y.Z substance-painter-mcp install
(or `uninstall`).
"""

from __future__ import annotations

import json
import os
from pathlib import Path
import plistlib
import shlex
import shutil
import subprocess
import sys
import time
from typing import Any

from . import __version__
from .client import PainterRemote, PainterRemoteConfig, PainterRemoteError


REPO = "https://github.com/samlehoy/SubstancePainterMCP"
NAME = "substance-painter"
ROOT_VARS = (
    "SP_MCP_EXPORT_ROOTS",
    "SP_MCP_PROJECT_ROOTS",
    "SP_MCP_MESH_ROOTS",
    "SP_MCP_BAKE_MESH_ROOTS",
    "SP_MCP_RESOURCE_ROOTS",
)
CLIENTS = {
    "1": ("claude-code", "Claude Code"),
    "2": ("claude-desktop", "Claude Desktop"),
    "3": ("antigravity", "Antigravity"),
    "4": ("opencode", "OpenCode"),
}
MAC_PAINTER = Path("/Applications/Adobe Substance 3D Painter/Adobe Substance 3D Painter.app")
WINDOWS_PAINTER = Path(
    r"C:\Program Files\Adobe\Adobe Substance 3D Painter\Adobe Substance 3D Painter.exe"
)


def server_command(uvx: str) -> list[str]:
    return [uvx, "--from", f"git+{REPO}@v{__version__}", "substance-painter-mcp"]


def json_config_path(client: str) -> Path:
    home = Path.home()
    if client == "claude-desktop":
        if sys.platform == "darwin":
            return home / "Library" / "Application Support" / "Claude" / "claude_desktop_config.json"
        if sys.platform == "win32":
            return Path(os.environ["APPDATA"]) / "Claude" / "claude_desktop_config.json"
        return home / ".config" / "Claude" / "claude_desktop_config.json"
    if client == "antigravity":
        return home / ".gemini" / "config" / "mcp_config.json"
    if client == "opencode":
        return home / ".config" / "opencode" / "opencode.json"
    raise ValueError(f"Unknown client: {client}")


def servers_key(client: str) -> str:
    return "mcp" if client == "opencode" else "mcpServers"


def merge_server(
    config: dict[str, Any], client: str, command: list[str], env: dict[str, str]
) -> dict[str, Any]:
    """Add or replace only this server's entry; every other setting is kept."""
    key = servers_key(client)
    servers = config.setdefault(key, {})
    if not isinstance(servers, dict):
        raise ValueError(f'"{key}" in the existing config is not an object')
    if client == "opencode":
        # The first uvx run builds the package; OpenCode's default 5 s timeout is too short.
        servers[NAME] = {"type": "local", "command": command, "environment": env, "timeout": 60000}
    else:
        servers[NAME] = {"command": command[0], "args": command[1:], "env": env}
    return config


def read_json_config(path: Path) -> dict[str, Any]:
    """Return the config object ({} when missing); refuse anything that is not plain JSON."""
    if not path.exists():
        return {}
    text = path.read_text(encoding="utf-8")
    try:
        config = json.loads(text) if text.strip() else {}
    except json.JSONDecodeError as exc:
        raise ValueError(f"{path} is not plain JSON ({exc.msg}); edit it manually") from None
    if not isinstance(config, dict):
        raise ValueError(f"{path} does not contain a JSON object")
    return config


def save_json_config(path: Path, config: dict[str, Any]) -> Path | None:
    """Back up an existing file, then write atomically. Returns the backup."""
    backup = None
    if path.exists():
        backup = path.with_name(f"{path.name}.bak-{time.strftime('%Y%m%d-%H%M%S')}")
        shutil.copy2(path, backup)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f"{path.name}.tmp")
    temporary.write_text(json.dumps(config, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    os.replace(temporary, path)
    return backup


def write_json_config(
    path: Path, client: str, command: list[str], env: dict[str, str]
) -> Path | None:
    """Merge the entry into a JSON config, backing up an existing file. Returns the backup."""
    if client == "opencode" and path.with_suffix(".jsonc").exists():
        raise ValueError(f"{path.with_suffix('.jsonc')} exists; add the server to it manually")
    config = read_json_config(path)
    merge_server(config, client, command, env)
    return save_json_config(path, config)


def has_json_entry(path: Path, client: str) -> bool:
    servers = read_json_config(path).get(servers_key(client))
    return isinstance(servers, dict) and NAME in servers


def remove_json_entry(path: Path, client: str) -> Path | None:
    """Remove only this server's entry, backing up the file first. Returns the backup."""
    config = read_json_config(path)
    del config[servers_key(client)][NAME]
    return save_json_config(path, config)


def claude_cli() -> str:
    claude = shutil.which("claude")
    if not claude:
        raise FileNotFoundError("Claude Code CLI (claude) was not found on PATH")
    return claude


def claude_code_has_entry() -> bool:
    """Whether Claude Code's user scope lists this server (read-only check)."""
    path = Path(os.environ.get("CLAUDE_CONFIG_DIR") or Path.home()) / ".claude.json"
    try:
        config = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return False
    servers = config.get("mcpServers") if isinstance(config, dict) else None
    return isinstance(servers, dict) and NAME in servers


def uninstall_claude_code() -> None:
    removed = subprocess.run(
        [claude_cli(), "mcp", "remove", NAME, "-s", "user"], capture_output=True, text=True
    )
    if removed.returncode:
        raise RuntimeError((removed.stderr or removed.stdout).strip())


def install_claude_code(command: list[str], env: dict[str, str]) -> None:
    claude = claude_cli()
    # Replace any earlier user-scope entry; a missing entry is not an error.
    subprocess.run([claude, "mcp", "remove", NAME, "-s", "user"], capture_output=True)
    args = [claude, "mcp", "add", NAME, "-s", "user"]
    for key, value in env.items():
        args += ["-e", f"{key}={value}"]
    added = subprocess.run([*args, "--", *command], capture_output=True, text=True)
    if added.returncode:
        raise RuntimeError((added.stderr or added.stdout).strip())


def painter_version() -> str | None:
    try:
        return PainterRemote(PainterRemoteConfig(timeout_seconds=3)).check_connection()
    except PainterRemoteError:
        pass
    plist = MAC_PAINTER / "Contents" / "Info.plist"
    if plist.is_file():
        with plist.open("rb") as handle:
            return plistlib.load(handle).get("CFBundleShortVersionString")
    return None


def launch_hint() -> str:
    if sys.platform == "darwin":
        return f'open -a "{MAC_PAINTER}" --args --enable-remote-scripting'
    return f'"{WINDOWS_PAINTER}" --enable-remote-scripting'


def ask(prompt: str, default: str = "") -> str:
    suffix = f" [{default}]" if default else ""
    return input(f"{prompt}{suffix}: ").strip() or default


def choose_clients() -> list[tuple[str, str]]:
    print("Install into which clients? (comma-separated)")
    for number, (_, label) in CLIENTS.items():
        print(f"  {number}) {label}")
    while True:
        picked = [item.strip() for item in ask("Numbers").split(",") if item.strip()]
        if picked and all(item in CLIENTS for item in picked):
            return [CLIENTS[item] for item in dict.fromkeys(picked)]
        print(f"Enter numbers from 1 to {len(CLIENTS)}, e.g. 1,3")


def clean_path(text: str, windows: bool = sys.platform == "win32") -> str:
    """Accept a path typed by hand or dragged in from Finder/Explorer."""
    text = text.strip()
    if windows:
        # Explorer drag-and-drop quotes paths with spaces; backslashes are separators.
        return text.strip('"')
    # Finder drag-and-drop escapes spaces (My\ Folder); some terminals quote instead.
    try:
        parts = shlex.split(text)
    except ValueError:  # e.g. a hand-typed apostrophe
        return text
    return parts[0] if len(parts) == 1 else text


def choose_folder() -> Path:
    print("Work folder: the only place the server may read meshes and images,")
    print("and write projects, backups, and exports.")
    while True:
        answer = clean_path(ask("Folder (type a path or drag a folder here)",
                                str(Path.home() / "SubstanceProjects")))
        folder = Path(answer).expanduser().resolve()
        if folder.is_dir():
            return folder
        if ask(f"{folder} does not exist. Create it? (y/N)").lower() == "y":
            folder.mkdir(parents=True)
            return folder


def run() -> int:
    print(f"Substance Painter MCP {__version__} installer\n")
    uvx = shutil.which("uvx")
    if not uvx:
        print("uv is required: install it with `brew install uv` (macOS) or "
              "`winget install astral-sh.uv` (Windows), then run this again.")
        return 1
    version = painter_version()
    if version is None:
        print("! Substance 3D Painter was not detected; install 12.1 or newer.")
    elif tuple(int(part) for part in version.split(".")[:2]) < (12, 1):
        print(f"! Painter {version} found; 12.1 or newer is required for every tool.")
    else:
        print(f"✔ Painter {version} found")
    print()
    clients = choose_clients()
    folder = choose_folder()
    command = server_command(uvx)
    env = {"SP_MCP_TIMEOUT": "120", **dict.fromkeys(ROOT_VARS, str(folder))}

    print("\nThis will write:")
    for client, label in clients:
        if client == "claude-code":
            target = "claude mcp add -s user"
        else:
            path = json_config_path(client)
            target = f"{path} ({'backed up first' if path.exists() else 'new file'})"
        print(f"  {label:<15} → {target}")
    print(f"  {'Server command':<15} → {' '.join(command)}")
    if ask("Continue? (y/N)").lower() != "y":
        print("Nothing was changed.")
        return 1

    failed = 0
    for client, label in clients:
        try:
            if client == "claude-code":
                install_claude_code(command, env)
                print(f"✔ {label}")
            else:
                backup = write_json_config(json_config_path(client), client, command, env)
                print(f"✔ {label}" + (f" (backup: {backup.name})" if backup else ""))
        except Exception as exc:  # report each client independently
            failed += 1
            print(f"✘ {label}: {exc}")

    print("\nNext steps:")
    print("  1. Quit Painter completely, then start it with remote scripting:")
    print(f"     {launch_hint()}")
    print("  2. Restart your MCP client and ask it to check the Painter status.")
    return 1 if failed else 0


def run_uninstall() -> int:
    print(f"Substance Painter MCP {__version__} uninstaller\n")
    found = []
    for client, label in CLIENTS.values():
        try:
            if client == "claude-code":
                present, target = claude_code_has_entry(), "claude mcp remove -s user"
            else:
                path = json_config_path(client)
                present, target = has_json_entry(path, client), f"{path} (backed up first)"
        except ValueError as exc:
            print(f"! {label}: {exc}")
            continue
        if present:
            found.append((client, label, target))
    if not found:
        print("substance-painter is not configured in Claude Code (user scope), "
              "Claude Desktop, Antigravity, or OpenCode.")
        return 0

    print("This will remove substance-painter from:")
    for _, label, target in found:
        print(f"  {label:<15} → {target}")
    if ask("Continue? (y/N)").lower() != "y":
        print("Nothing was changed.")
        return 1

    failed = 0
    for client, label, _ in found:
        try:
            if client == "claude-code":
                uninstall_claude_code()
                print(f"✔ {label}")
            else:
                backup = remove_json_entry(json_config_path(client), client)
                print(f"✔ {label} (backup: {backup.name})")
        except Exception as exc:  # report each client independently
            failed += 1
            print(f"✘ {label}: {exc}")

    print("\nYour work folder and Painter projects were not touched. Restart your MCP clients.")
    print("To also delete the cached package: uv cache clean substance-painter-mcp")
    return 1 if failed else 0


def main(command: str = "install") -> None:
    try:
        sys.exit(run_uninstall() if command == "uninstall" else run())
    except (EOFError, KeyboardInterrupt):
        print("\nCancelled; nothing further was changed.")
        sys.exit(1)
