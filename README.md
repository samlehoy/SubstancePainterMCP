# Substance Painter MCP

[![Tests](https://github.com/samlehoy/SubstancePainterMCP/actions/workflows/test.yml/badge.svg)](https://github.com/samlehoy/SubstancePainterMCP/actions/workflows/test.yml)
[![Painter 12.1+](https://img.shields.io/badge/Painter-12.1%2B-99E83F)](https://www.adobe.com/products/substance3d/apps/painter.html)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

Let AI assistants such as Claude Code, Claude Desktop, Antigravity, and OpenCode work in your open Adobe Substance 3D Painter project: inspect it, build layers, bake, and export textures.

> Independent community project, not affiliated with or endorsed by Adobe.

## Install

You need **Substance 3D Painter 12.1 or newer** and **[uv](https://docs.astral.sh/uv/)**:

```bash
brew install uv              # macOS
winget install astral-sh.uv  # Windows
```

**1. Run the installer.** It asks which assistants to set up and which work folder the server may use, shows what it will change, and waits for your confirmation.

```bash
uvx --from git+https://github.com/samlehoy/SubstancePainterMCP@v1.0.3 substance-painter-mcp install
```

Answer three questions:

- **Numbers**: the assistants to set up, e.g. `1,3` for Claude Code and Antigravity.
- **Folder**: the folder with your meshes and reference images; projects, backups, and exports are saved there too. Type the path, or drag the folder from Finder or Explorer into the terminal window, then press Enter. Press Enter alone to use the suggested folder.
- **Continue?**: type `y`. Existing config files are backed up first, and only the `substance-painter` entry is changed.

<details>
<summary>Example session (macOS)</summary>

```text
$ uvx --from git+https://github.com/samlehoy/SubstancePainterMCP@v1.0.3 substance-painter-mcp install
Substance Painter MCP 1.0.3 installer

✔ Painter 12.1.5 found

Install into which clients? (comma-separated)
  1) Claude Code
  2) Claude Desktop
  3) Antigravity
  4) OpenCode
Numbers: 1,3
Work folder: the only place the server may read meshes and images,
and write projects, backups, and exports.
Folder (type a path or drag a folder here) [/Users/you/SubstanceProjects]: /Users/you/Documents/Forge

This will write:
  Claude Code     → claude mcp add -s user
  Antigravity     → /Users/you/.gemini/config/mcp_config.json (backed up first)
  Server command  → /opt/homebrew/bin/uvx --from git+https://github.com/samlehoy/SubstancePainterMCP@v1.0.3 substance-painter-mcp
Continue? (y/N): y
✔ Claude Code
✔ Antigravity (backup: mcp_config.json.bak-20261012-213000)

Next steps:
  1. Quit Painter completely, then start it with remote scripting:
     open -a "/Applications/Adobe Substance 3D Painter/Adobe Substance 3D Painter.app" --args --enable-remote-scripting
  2. Restart your MCP client and ask it to check the Painter status.
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
  -- uvx --from git+https://github.com/samlehoy/SubstancePainterMCP@v1.0.3 substance-painter-mcp
```

**Claude Desktop, Cursor, Antigravity** (`mcpServers` format; Antigravity uses `~/.gemini/config/mcp_config.json`)

```json
{
  "mcpServers": {
    "substance-painter": {
      "command": "uvx",
      "args": ["--from", "git+https://github.com/samlehoy/SubstancePainterMCP@v1.0.3", "substance-painter-mcp"],
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
      "command": ["uvx", "--from", "git+https://github.com/samlehoy/SubstancePainterMCP@v1.0.3", "substance-painter-mcp"],
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

## Uninstall

```bash
uvx --from git+https://github.com/samlehoy/SubstancePainterMCP@v1.0.3 substance-painter-mcp uninstall
```

It finds `substance-painter` in Claude Code (user scope), Claude Desktop, Antigravity, and OpenCode, shows what it will remove, and asks for confirmation. Only that entry is removed, config files are backed up first, and your work folder and projects are not touched. To also delete the cached package, run `uv cache clean substance-painter-mcp`. If you added the server to a single Claude Code project instead, run `claude mcp remove substance-painter -s local` in that folder.

## What it can do

79 tools, including:

- **Inspect**: project info, layer tree, Texture Sets, resources, export presets, project audit.
- **Build layers**: Fill, Paint, and Group layers, channels, masks, Smart Materials and Smart Masks, procedural parameters, and multi-layer recipes that roll back if a step fails.
- **Bake**: inspect and configure bakers, assign high-poly meshes, preflight, and batch-bake with cancellation.
- **Export**: preview exact file names, then export textures with presets or engine profiles (Unity, Unreal, Blender, VRChat).
- **Manage projects**: create from a mesh, open, save, back up, reload meshes, import images as resources.

See the [full tool list](docs/TOOLS.md).

## Safety

- **Work folders.** The server reads and writes files only inside the folders you approve (`SP_MCP_*_ROOTS`). Features without an approved folder stay off.
- **Confirmation.** Baking, saving, importing, and opening or creating projects require explicit confirmation. Switching away from a project with unsaved work requires a backup first.
- **No arbitrary code.** Running raw Python inside Painter is disabled unless you set `SP_MCP_ALLOW_EXECUTE_PYTHON=1`.
- **Local only.** Never expose Painter's remote-scripting port (`60041`) to other machines.

Details: [Configuration and safety](docs/CONFIGURATION.md).

## Troubleshooting

| Problem | Fix |
|---|---|
| "Cannot connect to Painter at localhost:60041" | Quit Painter completely and start it with `--enable-remote-scripting` (step 2). |
| The assistant shows no Painter tools | Restart the assistant after installing. |
| Geometry masks, snapshots, or recipes fail | Update Painter to 12.1 or newer. |
| "Path is outside SP_MCP_…_ROOTS" | Move the file into your work folder, or run the installer again with another folder. |

To check that Painter is listening, run `lsof -nP -iTCP:60041 -sTCP:LISTEN` (macOS) or `Get-NetTCPConnection -LocalPort 60041` (PowerShell).

## Learn more

- [Tool reference](docs/TOOLS.md) · [Configuration and safety](docs/CONFIGURATION.md) · [Development and testing](docs/DEVELOPMENT.md)
- Guides: [layer recipes](docs/RECIPES.md) (with a [VRChat outfit example](examples/recipes/vrchat_outfit.json)), [procedural sources and baking](docs/PROCEDURAL_AND_BAKING.md), [production baking](docs/PRODUCTION_BAKING.md), [resource imports](docs/RESOURCE_INGESTION.md), [project lifecycle](docs/PROJECT_LIFECYCLE.md)
- [Changelog](CHANGELOG.md) · [Roadmap](docs/ROADMAP.md)

Tested live with Painter 12.1.1 on Windows and 12.1.5 on macOS (Apple silicon). Automated tests run on Windows and macOS for every push.

## License

MIT. See [LICENSE](LICENSE).
