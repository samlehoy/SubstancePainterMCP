# Development

## Editable installation

Use an editable checkout to work on the server; code edits apply after the MCP client restarts the server.

Windows:

```powershell
git clone https://github.com/samlehoy/SubstancePainterMCP.git
cd SubstancePainterMCP
python -m venv .venv
.venv\Scripts\python.exe -m pip install -e .
```

macOS (use a Python 3.10+ such as Homebrew's `python3`; the system `/usr/bin/python3` is too old):

```bash
git clone https://github.com/samlehoy/SubstancePainterMCP.git
cd SubstancePainterMCP
python3 -m venv .venv
.venv/bin/python -m pip install -e .
```

For development and tests:

```powershell
.venv\Scripts\python.exe -m pip install -e ".[dev]"
.venv\Scripts\python.exe -m pytest
```

On macOS, use `.venv/bin/python` in place of `.venv\Scripts\python.exe`.

## Connect a client to the checkout

Example for Claude Desktop on Windows:

```json
{
  "mcpServers": {
    "substance-painter": {
      "command": "C:\\Tools\\SubstancePainterMCP\\.venv\\Scripts\\python.exe",
      "args": ["-m", "substance_painter_mcp"],
      "env": {
        "SP_MCP_TIMEOUT": "120",
        "SP_MCP_EXPORT_ROOTS": "D:\\SubstanceExports",
        "SP_MCP_PROJECT_ROOTS": "D:\\SubstanceBackups",
        "SP_MCP_MESH_ROOTS": "D:\\Meshes",
        "SP_MCP_BAKE_MESH_ROOTS": "D:\\BakeMeshes",
        "SP_MCP_RESOURCE_ROOTS": "D:\\SubstanceResources"
      }
    }
  }
}
```

Replace the paths with your installation and export directories. You may also use `.venv\Scripts\substance-painter-mcp.exe` directly as the command.

On macOS, Claude Desktop reads `~/Library/Application Support/Claude/claude_desktop_config.json`; use `/path/to/SubstancePainterMCP/.venv/bin/python` as the command. For Claude Code:

```bash
claude mcp add substance-painter \
  -e SP_MCP_EXPORT_ROOTS="$HOME/SubstanceProjects" \
  -- /path/to/SubstancePainterMCP/.venv/bin/python -m substance_painter_mcp
```

Claude Code's default `local` scope registers the server for the current directory only; run the command from the folder you will work in, or add `-s user` to make it available everywhere.

## Tests and live validation

Run the automated suite:

```powershell
.venv\Scripts\python.exe -m pytest
```

The current suite covers request encoding, typed errors, timeout behavior, input isolation, color conversion, opacity validation, operation-level behavior, and the installer's config merging. GitHub Actions runs it on Windows and macOS with Python 3.10 and 3.14 for every push and pull request.

With Painter running and a disposable project open, use the live smoke test:

```powershell
# Read-only inspection
.venv\Scripts\python.exe scripts\live_smoke.py

# Reversible create -> edit -> verify -> delete round trip
.venv\Scripts\python.exe scripts\live_smoke.py --write

# Full v0.3 transaction, mask-effect, Smart asset, export, and backup validation
.venv\Scripts\python.exe scripts\live_features.py `
  --output-root D:\SubstanceMCPTest --texture-export --project-copy

# v0.4 geometry, recipe backup, projection, and Smart asset application
.venv\Scripts\python.exe scripts\live_v04.py `
  --output-root D:\SubstanceMCPTest --project-copy

# v0.5 Fill resources/projections plus optional bake and same-mesh reload jobs
$env:SP_MCP_MESH_ROOTS = "D:\Meshes"
.venv\Scripts\python.exe scripts\live_v05.py `
  --mesh D:\Meshes\sample.fbx --run-bake --run-mesh-reload

# v0.6 procedural parameters, presets, Anchor bindings, and baker config rollback
.venv\Scripts\python.exe scripts\live_v06.py

# v0.7 high-poly assignment, preset round trip, preflight, cancel/restore, and optional successful bake
$env:SP_MCP_BAKE_MESH_ROOTS = "D:\BakeMeshes"
.venv\Scripts\python.exe scripts\live_v07.py `
  --high-poly D:\BakeMeshes\sample_high.fbx --success

# v0.8 project/session imports, OffsetMap, Fill bitmap, and Generator image input round trips
$env:SP_MCP_RESOURCE_ROOTS = "D:\SubstanceResources"
.venv\Scripts\python.exe scripts\live_v08.py `
  --image D:\SubstanceResources\validation.png

# v0.9 backed-up async project creation, original reopen, and typed Auto UV mesh reload
$env:SP_MCP_MESH_ROOTS = "D:\Meshes"
$env:SP_MCP_PROJECT_ROOTS = "D:\SubstanceProjects"
.venv\Scripts\python.exe scripts\live_v09.py `
  --output D:\SubstanceProjects\mcp_created.spp `
  --backup D:\SubstanceProjects\before_creation.spp

# v1.0 persistent shelf import, crawl events, ResourceID verification, and cleanup
$env:SP_MCP_RESOURCE_ROOTS = "D:\SubstanceResources"
.venv\Scripts\python.exe scripts\live_v10.py `
  --source D:\SubstanceResources\validation.png `
  --shelf-path D:\SubstanceResources\mcp-validation-shelf `
  --shelf-name mcp-validation
```

## Validation history

The 1.0.0 validation run used Painter 12.1.1 and a saved three-Texture-Set test project. It verified all 79 FastMCP schemas and 64 automated tests. The lifecycle validation saved the current 955 MB project; created and verified a 21 MB 256px OpenGL project through a `ProjectEditionEntered` job; verified the backup and explicit Full save; reopened the exact original `.spp`; reloaded the same FBX using typed Auto UV settings while preserving strokes; and observed zero added or removed Texture Sets. The shelf validation then created a disposable writable shelf, imported a PNG as a versioned `SHELF` resource, observed real `ShelfCrawlingStarted` and `ShelfCrawlingEnded` events, re-retrieved the exact ResourceID after refresh, removed the shelf, and restored the original project. All generated project, backup, and shelf artifacts were removed after successful restoration.

The 1.0.1 validation ran on Painter 12.1.5 on macOS (Apple silicon) with 67 automated tests. In a disposable project created from an OBJ, it assigned four bitmaps to one Fill in sequence and kept all four. Repeating an identical `set_active_channels` call and adding the Height channel left them intact. A mask Fill effect accepted a bitmap, and an Anchor binding preserved the existing BaseColor bitmap. The run confirmed that `Roughness` and `Metallic` are enum aliases of `SpecularRoughness` and `BaseMetalness`, and that the export reported the skipped Emissive map.

See [CHANGELOG.md](../CHANGELOG.md) for the full validation notes of every release.
