"""Interactive installer that registers this server with MCP clients, or removes it.

Run with: uvx --from git+https://github.com/samlehoy/SubstancePainterMCP substance-painter-mcp install
(or `uninstall`).
"""

from __future__ import annotations

from importlib import metadata
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
from .install_messages import MESSAGES


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
    "claude-code": "Claude Code",
    "claude-desktop": "Claude Desktop",
    "antigravity": "Antigravity",
    "opencode": "OpenCode",
}
MAC_APPS = {
    "claude-desktop": Path("/Applications/Claude.app"),
    "antigravity": Path("/Applications/Antigravity.app"),
}
MESH_EXTENSIONS = {
    ".fbx", ".obj", ".dae", ".ply", ".abc", ".usd", ".usda", ".usdc", ".usdz", ".gltf", ".glb",
}
IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".tga", ".tif", ".tiff", ".exr", ".bmp", ".psd", ".hdr"}
FILE_MANAGERS = {"darwin": "Finder", "win32": "File Explorer"}
MAC_PAINTER = Path("/Applications/Adobe Substance 3D Painter/Adobe Substance 3D Painter.app")
WINDOWS_PAINTER = Path(
    r"C:\Program Files\Adobe\Adobe Substance 3D Painter\Adobe Substance 3D Painter.exe"
)


def package_source() -> str:
    """The git source uvx installed this package from, pinned to its exact commit.

    A commit pin lets uvx start from its cache without fetching the tag again (about
    1.3 s faster, and it works offline). Other installs fall back to this release's tag.
    """
    try:
        text = metadata.distribution("substance-painter-mcp").read_text("direct_url.json")
    except metadata.PackageNotFoundError:
        text = None
    info = json.loads(text or "{}")
    vcs = info.get("vcs_info") or {}
    if vcs.get("vcs") == "git" and vcs.get("commit_id"):
        return f"git+{info['url']}@{vcs['commit_id']}"
    return f"git+{REPO}@v{__version__}"


def server_command(uvx: str) -> list[str]:
    return [uvx, "--from", package_source(), "substance-painter-mcp"]


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


def display(path: Path | str) -> str:
    """Shorten the home directory to ~ (macOS/Linux) for readability."""
    text, home = str(path), str(Path.home())
    if sys.platform != "win32" and (text == home or text.startswith(home + os.sep)):
        return "~" + text[len(home):]
    return text


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


def folder_summary(folder: Path, limit: int = 5000) -> tuple[int, int, bool]:
    """Count meshes and images in a folder; the bool says the scan stopped at `limit` files."""
    meshes = images = seen = 0
    for _, dirs, files in os.walk(folder):
        dirs[:] = [name for name in dirs if not name.startswith(".")]
        for name in files:
            suffix = os.path.splitext(name)[1].lower()
            meshes += suffix in MESH_EXTENSIONS
            images += suffix in IMAGE_EXTENSIONS
        seen += len(files)
        if seen >= limit:
            return meshes, images, True
    return meshes, images, False


def is_broad(folder: Path) -> bool:
    """Whether approving the folder would expose the whole home directory or a drive."""
    home = Path.home().resolve()
    return folder == home or folder in home.parents or folder == Path(folder.anchor)


def client_options() -> list[tuple[str, str, str | None, bool, str | None]]:
    """(client, label, note key, installed, disabled-reason key) for every supported client."""
    options = []
    for client, label in CLIENTS.items():
        disabled = None
        if client == "claude-code":
            installed = claude_code_has_entry()
            detected = shutil.which("claude") is not None
            disabled = None if detected else "note.no_claude"
        else:
            path = json_config_path(client)
            try:
                installed = has_json_entry(path, client)
            except ValueError:  # unreadable config; installing reports why
                installed = False
            detected = (
                path.parent.exists()
                or (sys.platform == "darwin" and client in MAC_APPS and MAC_APPS[client].exists())
                or (client == "opencode" and shutil.which("opencode") is not None)
            )
        note = "note.installed" if installed else None if detected else "note.not_detected"
        options.append((client, label, note, installed, disabled))
    return options


class Console:
    """Arrow-key prompts and colors in an interactive terminal; plain text otherwise."""

    def __init__(self, fancy: bool | None = None, lang: str = "en", **io: Any):
        if fancy is None:
            fancy = sys.stdin.isatty() and sys.stdout.isatty()
        self.fancy = fancy
        self.lang = lang
        # prompt_toolkit input/output overrides (tests). Answered prompts are erased and
        # replaced by translated summary lines, since questionary's own are English-only.
        self.io = {**io, "erase_when_done": True}
        if fancy:
            try:
                import questionary
            except ImportError:
                self.fancy = False
                return
            self.style = questionary.Style([
                ("qmark", "fg:ansigreen bold"),
                ("question", "bold"),
                ("answer", "fg:ansigreen bold"),
                ("pointer", "fg:ansigreen bold"),
                ("highlighted", "fg:ansigreen bold"),
                ("selected", "fg:ansigreen"),
                ("instruction", "fg:ansibrightblack"),
                ("disabled", "fg:ansibrightblack italic"),
                ("accent", "fg:ansigreen bold"),
                ("title", "bold"),
                ("dim", "fg:ansibrightblack"),
                ("ok", "fg:ansigreen bold"),
                ("warn", "fg:ansiyellow bold"),
                ("fail", "fg:ansired bold"),
                ("code", "fg:ansicyan"),
            ])

    def t(self, key: str, **values: Any) -> str:
        english, indonesian = MESSAGES[key]
        return (indonesian if self.lang == "id" else english).format(**values)

    def say(self, *parts: str | tuple[str, str]) -> None:
        """Print one line; a (style, text) part is colored in an interactive terminal."""
        if not self.fancy:
            print("".join(part if isinstance(part, str) else part[1] for part in parts))
            return
        from prompt_toolkit import print_formatted_text
        from prompt_toolkit.formatted_text import FormattedText

        tokens = [("", part) if isinstance(part, str) else (f"class:{part[0]}", part[1])
                  for part in parts]
        print_formatted_text(FormattedText(tokens), style=self.style, output=self.io.get("output"))

    def choose_language(self) -> None:
        if self.fancy:
            import questionary

            self.lang = questionary.select(
                "Language / Bahasa",
                choices=[questionary.Choice("English", "en"),
                         questionary.Choice("Bahasa Indonesia", "id")],
                instruction="(↑↓ · enter)",
                style=self.style,
                **self.io,
            ).unsafe_ask()
            return
        self.say("Language / Bahasa:  1) English  2) Bahasa Indonesia")
        self.lang = "id" if self.ask("1/2", "1") in {"2", "id"} else "en"

    def header(self, title_key: str) -> None:
        text = f"Substance Painter MCP · {self.t(title_key)} {__version__}"
        if not self.fancy:
            self.say(text)
            return
        bar = "─" * (len(text) + 4)
        self.say(("accent", f"╭{bar}╮"))
        self.say(("accent", "│  "), ("title", text), ("accent", "  │"))
        self.say(("accent", f"╰{bar}╯"))

    def step(self, number: int, title_key: str) -> None:
        self.say()
        self.say(("accent", self.t("step", number=number)), ("dim", " · "), ("title", self.t(title_key)))

    def ask(self, prompt: str, default: str = "") -> str:
        suffix = f" [{default}]" if default else ""
        return input(f"{prompt}{suffix}: ").strip() or default

    def confirm(self, question: str, default: bool) -> bool:
        if self.fancy:
            import questionary

            return questionary.confirm(
                question, default=default, style=self.style, **self.io
            ).unsafe_ask()
        answer = input(f"{question} ({'Y/n' if default else 'y/N'}): ").strip().lower()
        return answer.startswith("y") if answer else default

    def choose_clients(
        self, options: list[tuple[str, str, str | None, bool, str | None]]
    ) -> list[str]:
        if self.fancy:
            import questionary

            choices = [
                questionary.Choice(
                    title=[("class:text", label)]
                    + ([("class:dim", f"  {self.t(note)}")] if note else []),
                    value=client,
                    checked=installed and not disabled,
                    disabled=self.t(disabled) if disabled else None,
                )
                for client, label, note, installed, disabled in options
            ]
            return questionary.checkbox(
                self.t("clients.question"),
                choices=choices,
                instruction=self.t("clients.instruction"),
                validate=lambda picked: bool(picked) or self.t("clients.none"),
                style=self.style,
                **self.io,
            ).unsafe_ask()
        for number, (_, label, note, _, disabled) in enumerate(options, 1):
            extra = disabled or note
            self.say(f"  {number}) {label}" + (f" ({self.t(extra)})" if extra else ""))
        allowed = {str(number): option[0] for number, option in enumerate(options, 1)
                   if not option[4]}
        while True:
            picked = [item.strip() for item in self.ask(self.t("clients.numbers")).split(",")
                      if item.strip()]
            if picked and all(item in allowed for item in picked):
                return [allowed[item] for item in dict.fromkeys(picked)]
            self.say(self.t("clients.invalid", numbers=", ".join(allowed)))

    def ask_folder(self, suggestion: Path) -> Path:
        """Ask for a folder (typed or dragged in); empty input uses the suggestion."""

        def check(text: str) -> bool | str:
            if not text.strip():
                return True
            folder = Path(clean_path(text)).expanduser()
            if folder.is_dir() or (not folder.exists() and folder.parent.is_dir()):
                return True
            return self.t("folder.is_file") if folder.exists() else self.t("folder.no_parent")

        while True:
            if self.fancy:
                import questionary

                answer = questionary.path(
                    self.t("folder.prompt"),
                    only_directories=True,
                    validate=check,
                    style=self.style,
                    # Start empty so a dragged-in path is not appended to a default.
                    placeholder=[("class:dim", display(suggestion))],
                    complete_while_typing=False,
                    **self.io,
                ).unsafe_ask()
            else:
                answer = self.ask(self.t("folder.prompt"), display(suggestion))
                problem = check(answer)
                if problem is not True:
                    self.say(f"  {problem}")
                    continue
            folder = Path(clean_path(answer) if answer.strip() else str(suggestion))
            folder = folder.expanduser().resolve()
            if not folder.exists():
                if not self.confirm(self.t("folder.create", folder=display(folder)), default=True):
                    continue
                folder.mkdir(parents=True)
            if is_broad(folder) and not self.confirm(
                self.t("folder.broad", folder=display(folder)), default=False
            ):
                continue
            return folder

    def folder_text(self, meshes: int, images: int, truncated: bool) -> str:
        if not meshes and not images:
            return self.t("folder.empty")
        more = "+" if truncated else ""
        if self.lang == "id":
            return f"{meshes}{more} mesh, {images}{more} gambar"
        return (f"{meshes}{more} mesh{'' if meshes == 1 else 'es'}, "
                f"{images}{more} image{'' if images == 1 else 's'}")


def run(console: Console) -> int:
    console.choose_language()
    console.header("title.installer")
    uvx = shutil.which("uvx")
    if not uvx:
        console.say(("fail", console.t("uv.missing")), console.t("uv.how"))
        return 1
    version = painter_version()
    if version is None:
        console.say(("warn", "! "), console.t("painter.missing"))
    elif tuple(int(part) for part in version.split(".")[:2]) < (12, 1):
        console.say(("warn", "! "), console.t("painter.old", version=version))
    else:
        console.say(("ok", "✔ "), console.t("painter.ok", version=version))

    console.step(1, "step.assistants")
    clients = console.choose_clients(client_options())
    console.say(("ok", "  ✔ "), ", ".join(CLIENTS[client] for client in clients))

    suggestion = Path.home() / "SubstanceProjects"
    tip = console.t("folder.tip")
    console.step(2, "step.folder")
    console.say(f"  {console.t('folder.explain')}")
    console.say(f"  {console.t('folder.contents')}")
    console.say()
    file_manager = FILE_MANAGERS.get(sys.platform) or console.t("folder.file_manager")
    console.say(("accent", f"  {tip}"), console.t("folder.drag", file_manager=file_manager))
    console.say(("dim", "  " + " " * len(tip) + console.t("folder.type", suggestion=display(suggestion))))
    folder = console.ask_folder(suggestion)
    console.say(("ok", "  ✔ "), display(folder),
                ("dim", f" · {console.folder_text(*folder_summary(folder))}"))

    command = server_command(uvx)
    env = {"SP_MCP_TIMEOUT": "120", **dict.fromkeys(ROOT_VARS, str(folder))}
    console.step(3, "step.review")
    for client in clients:
        if client == "claude-code":
            target = "claude mcp add -s user"
        else:
            path = json_config_path(client)
            state = console.t("review.backed_up" if path.exists() else "review.new_file")
            target = f"{display(path)} ({state})"
        console.say(f"  {CLIENTS[client]:<15}", ("dim", target))
    console.say(f"  {console.t('review.folder'):<15}", ("dim", display(folder)))
    if not console.confirm(console.t("review.confirm"), default=True):
        console.say(console.t("nothing_changed"))
        return 1

    console.say()
    failed = 0
    for client in clients:
        try:
            if client == "claude-code":
                install_claude_code(command, env)
                backup = None
            else:
                backup = write_json_config(json_config_path(client), client, command, env)
            console.say(("ok", "  ✔ "), CLIENTS[client],
                        ("dim", "  " + console.t("backup", name=backup.name)) if backup else "")
        except Exception as exc:  # report each client independently
            failed += 1
            console.say(("fail", "  ✘ "), f"{CLIENTS[client]}: {exc}")

    console.say()
    console.say(("title", console.t("next.title")))
    console.say(f"  {console.t('next.painter')}")
    console.say(("code", f"     {launch_hint()}"))
    console.say(f"  {console.t('next.ask')}")
    return 1 if failed else 0


def run_uninstall(console: Console) -> int:
    console.choose_language()
    console.header("title.uninstaller")
    found = []
    for client, label in CLIENTS.items():
        try:
            if client == "claude-code":
                present, target = claude_code_has_entry(), "claude mcp remove -s user"
            else:
                path = json_config_path(client)
                present = has_json_entry(path, client)
                target = f"{display(path)} ({console.t('review.backed_up')})"
        except ValueError as exc:
            console.say(("warn", "! "), f"{label}: {exc}")
            continue
        if present:
            found.append((client, label, target))
    if not found:
        console.say(console.t("uninstall.none"))
        return 0

    console.say()
    console.say(("title", console.t("uninstall.found")))
    for _, label, target in found:
        console.say(f"  {label:<15}", ("dim", target))
    if not console.confirm(console.t("uninstall.confirm"), default=False):
        console.say(console.t("nothing_changed"))
        return 1

    console.say()
    failed = 0
    for client, label, _ in found:
        try:
            if client == "claude-code":
                uninstall_claude_code()
                backup = None
            else:
                backup = remove_json_entry(json_config_path(client), client)
            console.say(("ok", "  ✔ "), label,
                        ("dim", "  " + console.t("backup", name=backup.name)) if backup else "")
        except Exception as exc:  # report each client independently
            failed += 1
            console.say(("fail", "  ✘ "), f"{label}: {exc}")

    console.say()
    console.say(console.t("uninstall.untouched"))
    console.say(("dim", console.t("uninstall.cache")))
    return 1 if failed else 0


def main(command: str = "install") -> None:
    console = Console()
    try:
        sys.exit(run_uninstall(console) if command == "uninstall" else run(console))
    except (EOFError, KeyboardInterrupt):
        console.say()
        console.say(("warn", console.t("cancelled")))
        sys.exit(1)
