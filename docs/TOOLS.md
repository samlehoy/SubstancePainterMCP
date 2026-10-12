# Tool reference

All 79 MCP tools, grouped by purpose. Tools that change the project or write files require approved folders (see [CONFIGURATION.md](CONFIGURATION.md)), and the riskier ones also require `confirm=true`.

## Inspection and diagnostics

| Tool | Purpose |
|---|---|
| `painter_status` | Check the connection, Painter/API versions, and whether a project is open. |
| `get_project_info` | Return the project path and Texture Sets. |
| `plan_project_creation` | Validate all new-project inputs, typed settings, output, backup, and current-context impact. |
| `get_project_creation_job` | Poll asynchronous project creation, recovery state, and output-file verification. |
| `get_shelf_refresh_job` | Poll the latest explicit shelf refresh and its crawling state. |
| `get_capabilities` | Probe channels, blend modes, and version-dependent runtime features. |
| `audit_project` | Report resolution, channels, layer hygiene, and outdated resources. |
| `inspect_baking` | Inspect enabled bakers, UV tiles, and mesh-map assignments without baking. |
| `inspect_baking_parameters` | Inspect typed common properties or one baker, including ranges and enum labels. |
| `preflight_bake` | Validate project state, mesh inputs, bakers, UV tiles, and expected maps for one or more Texture Sets. |
| `get_bake_job` | Read progress and terminal status for an asynchronous bake. |
| `get_mesh_reload_job` | Read completion status and Texture Set changes for a mesh reload. |
| `list_layers` | Return a recursive UID-based layer tree. |
| `find_layers` | Search by name, type, or visibility and include parent paths. |
| `snapshot_layer_tree` | Capture layers, masks, effects, active channels, and a deterministic digest. |
| `diff_layer_snapshots` | Compare snapshots by UID and report added, removed, or changed nodes. |
| `get_geometry_mask` | Inspect Mesh/UDIM mask state and available geometry elements. |
| `get_fill_parameters` | Inspect procedural values, editor metadata, ranges, enums, and presets. |
| `get_procedural_inputs` | Inspect bitmap, color, or Anchor sources used by procedural image inputs. |
| `list_anchor_points` | Discover Anchor Points with Texture Set, stack, and owner context. |
| `list_export_presets` | List built-in and shelf export presets. |
| `inspect_export_preset` | Resolve a preset and preview its exact map names without writing. |
| `list_export_profiles` | List curated VRChat, Blender, Unity, Unreal, and generic profiles. |
| `list_project_resources` | List resources referenced by the current project. |
| `list_shelves` | List configured shelves, paths, write capability, and current crawling state. |
| `search_resources` | Search resources by query, usage, URL, or type. |
| `find_outdated_resources` | Build a read-only replacement plan for outdated project resources. |

## Layer editing

| Tool | Purpose |
|---|---|
| `create_fill_layer` | Create a Fill layer with an optional base color. |
| `create_paint_layer` | Create a Paint layer. |
| `create_group` | Create a layer group. |
| `plan_layer_recipe` | Validate a recipe, resolve channels, and preview backup/mutation scope. |
| `create_layer_recipe` | Create nested structures atomically, optionally after an `.spp` backup. |
| `set_geometry_mask` | Apply inclusion/exclusion masks using mesh names or UDIM numbers. |
| `insert_smart_material` | Apply a Smart Material at stack top or inside a group. |
| `apply_smart_mask` | Apply a Smart Mask with transactional cleanup on failure. |
| `set_fill_base_color` | Convert an sRGB input color into Painter's working color space. |
| `set_fill_channels` | Set multiple uniform channels, including Roughness, Metallic, and Emission aliases. |
| `get_fill_projection` | Inspect Fill projection mode and common UV transforms. |
| `set_fill_projection` | Set Fill, UV, or Triplanar projection and transforms transactionally. |
| `get_fill_sources` | Inspect material-mode or per-channel Fill sources. |
| `set_fill_resource` | Assign a `resource://` asset to one channel, a complete Fill material, or a mask Fill effect. |
| `set_fill_parameters` | Transactionally update typed procedural Substance parameters. |
| `set_procedural_input` | Connect a verified resource to a procedural image input or reset its default. |
| `apply_fill_preset` | Apply a named preset exposed by the current procedural source. |
| `set_fill_anchor_source` | Bind an Anchor Point to one Fill channel or the complete material. |
| `set_fill_projection_advanced` | Configure UV, Triplanar, Planar, Spherical, or Cylindrical projection details. |
| `set_active_channels` | Replace a Fill or Paint layer's active channel set. |
| `set_layer_mask` | Add, replace, or remove a White/Black mask. |
| `insert_mask_effect` | Insert procedural or paint effects into a layer's mask stack. |
| `set_layer_properties` | Set visibility and channel-specific opacity or blend mode. |
| `rename_layer` | Rename a layer by UID. |
| `select_layers` | Select one or more layers by UID. |
| `delete_layer` | Delete a layer by UID. |

Layer names are not unique in Painter. All mutation tools therefore use the UIDs returned by `list_layers` or `find_layers`.

## Export and advanced access

| Tool | Purpose |
|---|---|
| `plan_texture_export` | Resolve expected output files and conflicts without writing anything. |
| `export_textures` | Export within approved roots and verify every generated file and size. |
| `plan_profile_export` | Preview a curated engine-profile export. |
| `export_with_profile` | Export with a curated profile and verify generated files. |
| `save_project_copy` | Write a verified `.spp` backup without relocating the current project. |
| `create_project` | Back up the current context, asynchronously create/save a project, and recover on failure. |
| `open_project` | Switch to an approved `.spp`, requiring a backup when the current project is dirty. |
| `save_project` | Explicitly overwrite and verify the current saved project after `confirm=true`. |
| `export_smart_material` | Export a Group as a verified `.spsm` file. |
| `export_smart_mask` | Export a layer mask as a verified `.spmsk` file. |
| `replace_outdated_resources` | Apply Painter's atomic resource replacement after `confirm=true`. |
| `import_project_resource` | Import and verify a safe visual resource inside the open project after `confirm=true`. |
| `import_session_resource` | Import and verify a safe visual resource for the current Painter session after `confirm=true`. |
| `import_shelf_resource` | Persist and verify a safe visual resource in a writable Painter shelf after `confirm=true`. |
| `start_shelf_refresh` | Refresh one configured shelf and bridge Painter crawling events into a persistent job. |
| `start_bake` | Start an asynchronous bake after `confirm=true`, optionally creating a project copy first. |
| `cancel_bake` | Request cooperative cancellation of a running bake job. |
| `configure_baking` | Transactionally configure Texture Set enablement, bakers, UDIMs, curvature, and typed properties after `confirm=true`. |
| `set_baking_mesh_inputs` | Assign or clear sandboxed high-poly/cage files, Low as High, and Cage Mode transactionally. |
| `set_baking_resource_input` | Set or clear a Resource-typed common/per-baker property transactionally. |
| `capture_baking_preset` | Capture portable common, baker, UDIM, curvature, and enablement settings without file-backed values. |
| `apply_baking_preset` | Validate and transactionally apply a captured baking preset after `confirm=true`. |
| `start_batch_bake` | Preflight and asynchronously bake multiple Texture Sets with restoration and a per-map result manifest. |
| `plan_mesh_reload` | Validate an approved mesh path and preview backup/current Texture Set scope. |
| `start_mesh_reload` | Optionally back up, then asynchronously reload a mesh after `confirm=true`. |
| `execute_python` | Run arbitrary Painter Python only when explicitly enabled. |
