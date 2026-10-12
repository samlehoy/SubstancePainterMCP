import json

import pytest

from substance_painter_mcp.install import (
    NAME, clean_path, has_json_entry, remove_json_entry, write_json_config,
)


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
