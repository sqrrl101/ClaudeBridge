---
name: fusion360
description: Control Autodesk Fusion 360 CAD software via the Claude Bridge add-in. Create sketches, draw shapes, extrude 3D objects, and build complex models interactively.
---

# Fusion 360 Interactive Control

This skill enables Claude to control Autodesk Fusion 360 through the Claude Bridge add-in. You can create 3D models by sending commands that are automatically executed in Fusion 360.

## Prerequisites

1. **Fusion 360** must be running with a design open
2. **ClaudeBridge add-in** must be active (Shift+S → Add-Ins → ClaudeBridge → Run)

## How It Works

Claude sends commands by writing JSON to:
```
<ClaudeBridge-directory>/commands.json
```

The bridge polls every second and executes commands. Results appear in:
```
<ClaudeBridge-directory>/results.json
```

## Sending Commands

To send a command, write a JSON file with this structure:

```json
{
  "id": <incrementing_number>,
  "action": "<command_name>",
  "params": { <parameters> }
}
```

**Important**: The `id` must be higher than the previous command, or it will be ignored.

## Workflow Pattern

1. **Check the last command ID** by reading `results.json`
2. **Send command** with incremented ID
3. **Read results** to confirm success
4. **Repeat** for next command

## Available Commands

See [reference.md](./reference.md) for the complete API reference.

Quick reference:
- `ping` - Test connection
- `get_info` - Get design information
- `get_full_design` - Complete design snapshot (bodies, sketches, features, parameters)
- `get_bodies_detailed` - Detailed body geometry info
- `get_all_parameters` - All parameters including sketch dimensions (d1, d2, etc.)
- `get_sketch_geometry` - Full curve coordinates (circles, lines, arcs with positions)
- `get_construction_planes` - List all construction planes
- `create_offset_plane` - Create plane at Z offset (for multi-level geometry)
- `create_plane_at_angle` - Create angled construction plane
- `create_sketch` - Create sketch on plane (supports plane_index for offset planes)
- `create_sketch_on_face` - Create sketch on existing body face
- `draw_circle` - Draw a circle
- `draw_rectangle` - Draw a rectangle
- `draw_line` - Draw a line
- `draw_arc` / `draw_arc_sweep` / `draw_arc_three_points` - Draw arcs
- `list_profiles` - List profiles in a sketch
- `extrude` - Extrude a profile into 3D
- `revolve` - Revolve a profile around an axis
- `fillet` - Round edges
- `chamfer` - Bevel edges
- `shell` - Hollow out a body
- `set_parameter` - Create/update a user parameter
- `message` - Display a message in Fusion 360

## Example: Create a Box

See [examples.md](./examples.md) for complete workflow examples.

## Units

All dimensions are in **centimeters** (Fusion 360's internal unit):
- 1 cm = 10 mm
- To create a 50mm object, use `5` (cm)

## Tips

- Always create a sketch before drawing shapes
- Use `list_profiles` to find the correct profile index before extruding
- If a command fails, check `results.json` for error details
