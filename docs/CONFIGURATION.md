# Configuration and safety

The interactive installer sets every `SP_MCP_*_ROOTS` variable to one work folder. Set them individually to separate inputs from outputs.

## Environment variables

| Variable | Default | Description |
|---|---:|---|
| `SP_MCP_HOST` | `localhost` | Painter remote-scripting host. |
| `SP_MCP_PORT` | `60041` | Painter remote-scripting port. |
| `SP_MCP_TIMEOUT` | `30` | HTTP timeout in seconds. |
| `SP_MCP_ALLOW_EXECUTE_PYTHON` | unset | Set to `1` to expose arbitrary Python execution. |
| `SP_MCP_EXPORT_ROOTS` | unset | Approved export roots. Separate multiple paths with `;` on Windows or `:` on macOS. |
| `SP_MCP_PROJECT_ROOTS` | unset | Approved roots for `.spp` project copies. |
| `SP_MCP_MESH_ROOTS` | unset | Approved input roots for FBX, OBJ, DAE, PLY, and USD mesh reloads. |
| `SP_MCP_BAKE_MESH_ROOTS` | unset | Approved roots for high-poly and cage meshes used by baking. |
| `SP_MCP_RESOURCE_ROOTS` | unset | Approved input roots for project/session/shelf resource imports. |

Exports are disabled until `SP_MCP_EXPORT_ROOTS` is configured. `plan_texture_export` performs a read-only preflight. `export_textures` repeats the validation and refuses existing targets unless `overwrite=true` is explicitly supplied.

Project copying is independently disabled until `SP_MCP_PROJECT_ROOTS` is configured. `save_project_copy` uses Painter's `save_as_copy`, verifies the resulting file, and confirms that the current project path did not change.

Mesh reload and project creation are independently disabled until `SP_MCP_MESH_ROOTS` is configured. `plan_mesh_reload` is read-only; `start_mesh_reload` additionally requires `confirm=true` and accepts typed Auto UV or USD settings. Project creation also requires an output under `SP_MCP_PROJECT_ROOTS`; optional templates and mesh maps come from `SP_MCP_RESOURCE_ROOTS`. A backup path under `SP_MCP_PROJECT_ROOTS` is mandatory before replacing an open project.

High-poly and cage assignment is independently disabled until `SP_MCP_BAKE_MESH_ROOTS` is configured. `set_baking_mesh_inputs` accepts only existing mesh files below those roots. `preflight_bake` then validates the effective Painter settings before `start_batch_bake` changes any mesh maps.

Resource import is independently disabled until `SP_MCP_RESOURCE_ROOTS` is configured. Project, session, and shelf imports require `confirm=true`, reject executable/script-like extensions and unsafe script/shader usages, and verify the returned `resource://` identity through Painter before returning it. Shelf imports additionally require a configured writable shelf; refresh jobs report Painter's actual crawling events instead of guessing from request completion.

## Safety model

- User values such as names, colors, and UIDs are serialized as base64-encoded JSON instead of being interpolated into Python source.
- Results are returned directly; the server no longer relies on a shared `C:\temp` result file that could become stale or collide across requests.
- Failed connections stop at the configured timeout instead of hanging for an hour.
- Connection, HTTP, and Painter script failures are reported as distinct error types.
- Layer mutations use UIDs to avoid editing the wrong layer when names are duplicated.
- Project creation separates preflight from execution, requires confirmation and a verified backup before replacing an open context, runs through Painter events, and attempts recovery on failure.
- New-project output, current-project, backup, and open-target paths are checked for collisions before context switching.
- Texture exports require approved roots, a preflight plan, explicit overwrite consent, and post-export file verification.
- Baking and mesh reload require explicit confirmation, expose persistent job state, and never depend on a long-lived HTTP request.
- Mesh inputs are restricted to approved roots and Painter-supported extensions.
- Generic procedural/baker parameter setters reject file and resource widgets; filesystem-backed inputs require dedicated sandboxed tools instead of accepting arbitrary paths.
- Resource imports use an independent approved-root policy, a safe usage allowlist, script/executable rejection, and post-import retrieval verification.
- Shelf writes require explicit confirmation and a writable configured shelf; shelf refresh state is retained in Painter and driven by crawling events.
- Procedural and baking resource setters accept only existing `resource://` identities and restore the original source/property if Painter rejects an update.
- Baking configuration reports every linked Texture Set affected by shared common or per-baker parameters and rolls the touched state back if any update fails.
- Batch baking restores every Texture Set's original bake-enabled state after success, cancellation, launch failure, or Painter failure.
- Baking presets omit file/resource widgets by design, keeping machine-specific paths out of portable configuration payloads.
- Arbitrary Python is opt-in and disabled by default.

The server is designed for local use. Do not expose Painter's remote-scripting port to untrusted networks.

## Compatibility

| Component | Supported / validated |
|---|---|
| Adobe Substance 3D Painter | Live-tested with 12.1.1 (Windows) and 12.1.5 (macOS, Apple silicon). 12.0.x lacks the geometry-mask API used by snapshots, geometry masks, and recipes. |
| Painter Python API | Runtime reported 0.3.5 in the validated build |
| Python | 3.10 or newer |
| MCP Python SDK | `mcp>=1.28,<2` |
| Transport | MCP stdio to Painter HTTP remote scripting |
| Painter endpoint | `localhost:60041` by default |

Painter builds may expose newer features while reporting an older API version string. `get_capabilities` therefore probes the running application for supported channels, blend modes, OpenPBR behavior, and version-specific features.

With `--enable-remote-scripting`, Painter also behaves as if `--disable-modal-popup` were set, so some confirmation dialogs do not appear. Save your work manually.
