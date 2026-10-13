from contextlib import contextmanager
import json
import sys
from pathlib import Path
from string import Formatter

import pytest

from substance_painter_mcp.install import (
    NAME, Console, clean_path, folder_summary, has_json_entry, is_broad, remove_json_entry,
    write_json_config,
)
from substance_painter_mcp.install_messages import MESSAGES


COMMAND = ["/opt/homebrew/bin/uvx", "--from", "git+https://example.com/repo@v1", "substance-painter-mcp"]
ENV = {"SP_MCP_EXPORT_ROOTS": "/work"}


def test_merge_keeps_other_servers_and_replaces_own_entry(tmp_path):
    path = tmp_path / "mcp_config.json"
    path.write_text(json.dumps({
        "theme": "dark",
        "mcpServers": {"other": {"command": "node"}, NAME: {"command": "old"}},
    }))
    backup = write_json_config(path, "antigravity", COMMAND, ENV)
    config = json.loads(path.read_text())
    assert config["theme"] == "dark"
    assert config["mcpServers"]["other"] == {"command": "node"}
    assert config["mcpServers"][NAME] == {"command": COMMAND[0], "args": COMMAND[1:], "env": ENV}
    assert json.loads(backup.read_text())["mcpServers"][NAME] == {"command": "old"}


def test_server_command_pins_the_installed_commit(monkeypatch):
    from substance_painter_mcp import install

    class Distribution:
        def __init__(self, info):
            self.info = info

        def read_text(self, name):
            return json.dumps(self.info)

    commit = "a1a42e4891a49f9db81b64ee4efe7e1832ac7678"
    info = {"url": "https://github.com/me/fork", "vcs_info": {"vcs": "git", "commit_id": commit}}
    monkeypatch.setattr(install.metadata, "distribution", lambda name: Distribution(info))
    assert install.server_command("uvx")[2] == f"git+https://github.com/me/fork@{commit}"
    # Local and editable installs have no commit to pin, so the release tag is used.
    local = {"url": "file:///src", "dir_info": {"editable": True}}
    monkeypatch.setattr(install.metadata, "distribution", lambda name: Distribution(local))
    assert install.server_command("uvx")[2] == f"git+{install.REPO}@v{install.__version__}"


def test_opencode_entry_uses_local_command_array(tmp_path):
    path = tmp_path / "opencode" / "opencode.json"
    assert write_json_config(path, "opencode", COMMAND, ENV) is None
    entry = json.loads(path.read_text())["mcp"][NAME]
    assert entry == {"type": "local", "command": COMMAND, "environment": ENV, "timeout": 60000}


@pytest.mark.parametrize("text", ['{"mcpServers": {}, // comment\n}', "[]"])
def test_unreadable_config_is_left_untouched(tmp_path, text):
    path = tmp_path / "claude_desktop_config.json"
    path.write_text(text)
    with pytest.raises(ValueError):
        write_json_config(path, "claude-desktop", COMMAND, ENV)
    assert path.read_text() == text
    assert list(tmp_path.iterdir()) == [path]


def test_opencode_jsonc_is_not_shadowed(tmp_path):
    (tmp_path / "opencode.jsonc").write_text("{}")
    with pytest.raises(ValueError, match="opencode.jsonc"):
        write_json_config(tmp_path / "opencode.json", "opencode", COMMAND, ENV)
    assert not (tmp_path / "opencode.json").exists()


@pytest.mark.parametrize(("typed", "expected"), [
    ("/Users/me/My\\ Work\\ \\(v2\\) ", "/Users/me/My Work (v2)"),  # Finder drag into Terminal
    ("'/Users/me/My Work' ", "/Users/me/My Work"),                   # terminals that quote instead
    ("/Users/me/My Work", "/Users/me/My Work"),                      # typed by hand
    ("/Users/me/Bob's Stuff", "/Users/me/Bob's Stuff"),              # unbalanced quote typed by hand
    ("~/Documents/project/Forge", "~/Documents/project/Forge"),
])
def test_clean_path_accepts_macos_input(typed, expected):
    assert clean_path(typed, windows=False) == expected


@pytest.mark.parametrize(("typed", "expected"), [
    ('"C:\\Users\\me\\My Work"', "C:\\Users\\me\\My Work"),  # Explorer drag adds quotes
    ("D:\\Substance\\Forge ", "D:\\Substance\\Forge"),        # backslashes are kept
])
def test_clean_path_accepts_windows_input(typed, expected):
    assert clean_path(typed, windows=True) == expected


def test_uninstall_removes_only_own_entry(tmp_path):
    path = tmp_path / "mcp_config.json"
    path.write_text(json.dumps({"theme": "dark", "mcpServers": {"other": {"command": "node"}}}))
    write_json_config(path, "antigravity", COMMAND, ENV)
    assert has_json_entry(path, "antigravity")
    backup = remove_json_entry(path, "antigravity")
    assert json.loads(path.read_text()) == {"theme": "dark", "mcpServers": {"other": {"command": "node"}}}
    assert NAME in json.loads(backup.read_text())["mcpServers"]
    assert not has_json_entry(path, "antigravity")


def test_uninstall_detection_ignores_missing_and_other_formats(tmp_path):
    assert not has_json_entry(tmp_path / "missing.json", "claude-desktop")
    path = tmp_path / "opencode.json"
    write_json_config(path, "opencode", COMMAND, ENV)
    assert has_json_entry(path, "opencode")
    assert not has_json_entry(path, "claude-desktop")  # opencode uses "mcp", not "mcpServers"


def test_folder_summary_counts_meshes_and_images(tmp_path):
    assert folder_summary(tmp_path) == (0, 0, False)
    for name in ("model.obj", "ref.PNG", "sub/high.fbx", "sub/base.jpg", ".cache/skip.png", "notes.txt"):
        (tmp_path / name).parent.mkdir(parents=True, exist_ok=True)
        (tmp_path / name).write_text("x")
    assert folder_summary(tmp_path) == (2, 2, False)
    assert Console(fancy=False).folder_text(2, 2, False) == "2 meshes, 2 images"
    assert Console(fancy=False, lang="id").folder_text(1, 2, False) == "1 mesh, 2 gambar"


def test_broad_folders_are_flagged(tmp_path):
    assert is_broad(Path.home().resolve())
    assert is_broad(Path(tmp_path.anchor))
    assert not is_broad(tmp_path)


DOWN, ENTER = "\x1b[B", "\r"


def paste(text):
    return f"\x1b[200~{text}\x1b[201~"  # bracketed paste, as when dragging a folder in


@contextmanager
def interactive_console(keys):
    from prompt_toolkit.input import create_pipe_input
    from prompt_toolkit.output import DummyOutput

    with create_pipe_input() as pipe:
        pipe.send_text(keys)
        yield Console(fancy=True, input=pipe, output=DummyOutput())


def test_interactive_client_picker_uses_arrow_keys_and_space():
    options = [
        ("claude-code", "Claude Code", None, False, None),
        ("claude-desktop", "Claude Desktop", "note.not_detected", False, None),
        ("antigravity", "Antigravity", "note.installed", True, None),
        ("opencode", "OpenCode", None, False, None),
    ]
    # Select Claude Code, move down to OpenCode and select it; Antigravity starts checked.
    with interactive_console(" " + DOWN * 3 + " " + ENTER) as console:
        assert console.choose_clients(options) == ["claude-code", "antigravity", "opencode"]


def test_interactive_folder_accepts_dragged_path_and_empty_default(tmp_path):
    forge = tmp_path / "My Forge (v2)"
    forge.mkdir()
    dragged = f'"{forge}" ' if sys.platform == "win32" else str(forge).replace(" ", "\\ ").replace("(", "\\(").replace(")", "\\)") + " "
    with interactive_console(paste(dragged) + ENTER) as console:
        assert console.ask_folder(tmp_path / "unused") == forge.resolve()
    # Empty input uses the suggestion, after confirming it may be created.
    with interactive_console(ENTER + "y") as console:
        assert console.ask_folder(tmp_path / "New Folder") == (tmp_path / "New Folder").resolve()
    assert (tmp_path / "New Folder").is_dir()


def test_every_message_has_both_languages_with_the_same_placeholders():
    fields = lambda text: {name for _, name, _, _ in Formatter().parse(text) if name}
    for key, (english, indonesian) in MESSAGES.items():
        assert english and indonesian, key
        assert fields(english) == fields(indonesian), key


def test_interactive_language_choice_switches_text():
    with interactive_console(DOWN + ENTER) as console:
        console.choose_language()
    assert console.lang == "id"
    assert console.t("step", number=2) == "Langkah 2 dari 3"
    with interactive_console(ENTER) as console:
        console.choose_language()
    assert console.lang == "en"
