# Layer Recipes

Layer recipes create nested Group, Fill, and Paint structures as one transaction. A failed channel, mask, or insertion step removes every node created by that request.

## Recommended workflow

1. Call `plan_layer_recipe` with the complete recipe.
2. Review the target Texture Set, node counts, resolved OpenPBR channels, current snapshot digest, and optional backup path.
3. Call `create_layer_recipe` with the same arguments.
4. Capture a new `snapshot_layer_tree` and compare it with `diff_layer_snapshots`.

Pass `backup_path` to both plan and create calls when the operation should first create an `.spp` copy. The path must be inside `SP_MCP_PROJECT_ROOTS`. The copy is written through Painter's `save_as_copy` API and does not relocate the open project.

## Recipe fields

Every node accepts:

| Field | Type | Description |
|---|---|---|
| `type` | string | Required: `group`, `fill`, or `paint`. |
| `name` | string | Required non-empty layer name. |
| `visible` | boolean | Optional initial visibility. |
| `mask` | object | Optional `Black` or `White` mask, enabled state, and `fill` bitmap. |

Group nodes may contain a recursive `children` list. Fill nodes may contain `base_color`, `channels`, and `active_channels`. Paint nodes may contain `active_channels`.

A `channels` value is a number, an `[r, g, b]` list, or a `resource://` URL. Scalar values are expanded to RGB uniform values, and a URL assigns that bitmap, so imported texture maps need no separate `set_fill_resource` calls. `mask.fill` takes a `resource://` URL and adds a Fill effect with that bitmap to the mask; its UID is returned as `mask_fill_uid`. `plan_layer_recipe` checks that every referenced resource exists before anything is created. `Roughness`, `Metallic`, and `Emission` are resolved to the matching legacy or OpenPBR runtime channel.

## Example

The repository includes [a VRChat outfit starter recipe](../examples/recipes/vrchat_outfit.json). It is intentionally shader-neutral: review colors, mask content, and channel packing before final export.

```json
[
  {
    "type": "group",
    "name": "00_BASE",
    "children": [
      {
        "type": "fill",
        "name": "Base Material",
        "base_color": [0.5, 0.5, 0.5],
        "channels": {"Roughness": 0.5, "Metallic": 0.0}
      }
    ]
  }
]
```

A decal layer with a bitmap color and a bitmap-driven mask, using URLs returned by `import_project_resource`:

```json
[
  {
    "type": "fill",
    "name": "Chest Decal",
    "channels": {"BaseColor": "resource://project0/decal_color", "Roughness": 0.6},
    "mask": {"background": "Black", "fill": "resource://project0/decal_mask"}
  }
]
```

## Recovery guarantees

- Local schema errors stop before Painter is called.
- Runtime validation occurs before layer creation.
- A failure during layer creation deletes every node created by the transaction.
- A failure during post-creation snapshot verification deletes every newly created root group or layer.
- An optional backup remains available even if the recipe later fails.

The transaction does not modify or roll back pre-existing layers. Existing-layer movement is intentionally unavailable until Painter exposes a confirmed lossless move primitive.
