# Fusion 360 Bridge API Reference

Complete reference for all available commands.

## Connection Commands

### ping
Test the bridge connection.
```json
{"id": 1, "action": "ping", "params": {}}
```

### message
Display a message box in Fusion 360.
```json
{"id": 2, "action": "message", "params": {"text": "Hello!"}}
```

---

## Session Export (Design Data)

### export_session
**Export complete design data to a timestamped session folder.**

This single command replaces all individual query commands. It exports everything the AI needs to understand the current design state.

```json
{"id": 3, "action": "export_session", "params": {}}
```

Optional parameters:
| Param | Type | Default | Description |
|-------|------|---------|-------------|
| name | string | "" | Custom session name suffix |

**Returns:**
```json
{
  "session_path": "/path/to/ClaudeBridge/sessions/2024-01-15_14-30-22",
  "session_name": "2024-01-15_14-30-22",
  "files": ["manifest.json", "design_info.json", ...],
  "summary": {"components": 1, "bodies": 2, "sketches": 3, ...}
}
```

**Exported Files:**

| File | Contents |
|------|----------|
| `manifest.json` | Session metadata, file list, summary counts |
| `design_info.json` | Design overview: components, bodies, sketches, features, parameters |
| `bodies.json` | Detailed body info: volume, area, face types, bounding box, circular edges |
| `features.json` | Timeline features with suppression status |
| `parameters.json` | User parameters + model parameters (d1, d2, etc.) with source info |
| `construction_planes.json` | All construction planes |
| `sketches/overview.json` | Summary of all sketches with curve counts |
| `sketches/sketch_N.json` | Full geometry for sketch N (circles, lines, arcs, ellipses with coordinates) |

**Example Session Folder:**
```
sessions/2024-01-15_14-30-22/
  manifest.json
  design_info.json
  bodies.json
  features.json
  parameters.json
  construction_planes.json
  sketches/
    overview.json
    sketch_0.json
    sketch_1.json
```

**Workflow:**
1. Call `export_session` once to export all design data
2. Read the JSON files you need directly from the session folder
3. No need for multiple round-trip commands

---

## Construction Geometry

### create_offset_plane
Create a construction plane offset from a base plane. Essential for creating geometry at different Z heights.
```json
{"id": 10, "action": "create_offset_plane", "params": {
  "plane": "xy",
  "offset": 5.0
}}
```
| Param | Type | Default | Description |
|-------|------|---------|-------------|
| plane | string | "xy" | Base plane (`"xy"`, `"xz"`, `"yz"`) |
| offset | float | 1.0 | Distance in cm (positive = along normal) |
| name | string | auto | Optional custom name |

**Returns:** `plane_index` for use with `create_sketch`

### create_plane_at_angle
Create a construction plane at an angle from a base plane.
```json
{"id": 11, "action": "create_plane_at_angle", "params": {
  "plane": "xy",
  "axis": "x",
  "angle": 45
}}
```
| Param | Type | Default | Description |
|-------|------|---------|-------------|
| plane | string | "xy" | Base plane |
| axis | string | "x" | Rotation axis (`"x"`, `"y"`, `"z"`) |
| angle | float | 45 | Angle in degrees |
| name | string | auto | Optional custom name |

---

## Sketch Commands

### create_sketch
Create a new sketch on a construction plane or offset plane.
```json
{"id": 10, "action": "create_sketch", "params": {"plane": "xy"}}
```
**Or on an offset plane:**
```json
{"id": 11, "action": "create_sketch", "params": {"plane_index": 0}}
```
| Param | Type | Default | Description |
|-------|------|---------|-------------|
| plane | string | "xy" | Base plane (`"xy"`, `"xz"`, `"yz"`) - used if plane_index not set |
| plane_index | int | null | Index of construction plane (from `create_offset_plane`) |

### create_sketch_on_face
Create a sketch on an existing body face. Useful for adding cuts or features to existing geometry.
```json
{"id": 12, "action": "create_sketch_on_face", "params": {
  "body_index": 0,
  "use_top_face": true
}}
```
| Param | Type | Default | Description |
|-------|------|---------|-------------|
| body_index | int | 0 | Which body |
| face_index | int | 0 | Which face (if use_top_face is false) |
| use_top_face | bool | false | Auto-find topmost planar face |

**Example workflow for cutting into top of a body:**
```json
// 1. Create sketch on top face
{"id": 1, "action": "create_sketch_on_face", "params": {"body_index": 0, "use_top_face": true}}
// 2. Draw shape to cut
{"id": 2, "action": "draw_circle", "params": {"x": 0, "y": 0, "radius": 1}}
// 3. Cut through body
{"id": 3, "action": "extrude", "params": {"height": -2, "operation": "cut"}}
```

### draw_circle
```json
{"id": 11, "action": "draw_circle", "params": {
  "sketch_index": 0, "x": 0, "y": 0, "radius": 2.5
}}
```

### draw_rectangle
```json
{"id": 12, "action": "draw_rectangle", "params": {
  "sketch_index": 0, "x": 0, "y": 0, "width": 4, "height": 3
}}
```

### draw_line
```json
{"id": 13, "action": "draw_line", "params": {
  "sketch_index": 0, "x1": 0, "y1": 0, "x2": 5, "y2": 3
}}
```

### draw_arc
Draw an arc defined by center, start point, and end point. Arc is drawn counter-clockwise from start to end.
```json
{"id": 14, "action": "draw_arc", "params": {
  "sketch_index": 0,
  "center_x": 0, "center_y": 0,
  "start_x": 2, "start_y": 0,
  "end_x": 0, "end_y": 2
}}
```

| Param | Type | Default | Description |
|-------|------|---------|-------------|
| sketch_index | int | last | Which sketch |
| center_x, center_y | float | 0, 0 | Center point |
| start_x, start_y | float | 1, 0 | Start point (defines radius) |
| end_x, end_y | float | 0, 1 | End point |

### draw_arc_three_points
Draw an arc passing through three points.
```json
{"id": 15, "action": "draw_arc_three_points", "params": {
  "sketch_index": 0,
  "start_x": 0, "start_y": 0,
  "mid_x": 1, "mid_y": 1,
  "end_x": 2, "end_y": 0
}}
```

| Param | Type | Default | Description |
|-------|------|---------|-------------|
| sketch_index | int | last | Which sketch |
| start_x, start_y | float | 0, 0 | Start point of arc |
| mid_x, mid_y | float | 0.5, 0.5 | Point along the arc (determines curvature) |
| end_x, end_y | float | 1, 0 | End point of arc |

### draw_arc_sweep
Draw an arc defined by center, start point, and sweep angle.
```json
{"id": 16, "action": "draw_arc_sweep", "params": {
  "sketch_index": 0,
  "center_x": 0, "center_y": 0,
  "start_x": 2, "start_y": 0,
  "sweep_angle": 90
}}
```

| Param | Type | Default | Description |
|-------|------|---------|-------------|
| sketch_index | int | last | Which sketch |
| center_x, center_y | float | 0, 0 | Center point |
| start_x, start_y | float | 1, 0 | Start point (defines radius) |
| sweep_angle | float | 90 | Sweep angle in degrees (positive = counter-clockwise) |

**Arc Examples:**
```json
// Quarter circle (90°) - use draw_arc_sweep
{"id": 1, "action": "draw_arc_sweep", "params": {
  "center_x": 0, "center_y": 0, "start_x": 3, "start_y": 0, "sweep_angle": 90
}}

// Semicircle (180°)
{"id": 2, "action": "draw_arc_sweep", "params": {
  "center_x": 0, "center_y": 0, "start_x": 3, "start_y": 0, "sweep_angle": 180
}}

// Arc connecting two points with specific curvature - use draw_arc_three_points
{"id": 3, "action": "draw_arc_three_points", "params": {
  "start_x": -2, "start_y": 0, "mid_x": 0, "mid_y": 1.5, "end_x": 2, "end_y": 0
}}
```

### list_profiles
List profiles in a sketch (for extrusion).
```json
{"id": 10, "action": "list_profiles", "params": {"sketch_index": 0}}
```

---

## 3D Operations

### extrude
Extrude a sketch profile.
```json
{"id": 14, "action": "extrude", "params": {
  "sketch_index": 0,
  "profile_index": 0,
  "height": 5,
  "operation": "new"
}}
```
| Param | Type | Default | Description |
|-------|------|---------|-------------|
| sketch_index | int | last | Sketch containing profile |
| profile_index | int | 0 | Which profile (use `list_profiles`) |
| height | float | 1 | Height in cm |
| operation | string | "new" | `"new"`, `"join"`, `"cut"` |

### revolve
Revolve a sketch profile around an axis to create rotational geometry.
```json
{"id": 15, "action": "revolve", "params": {
  "sketch_index": 0,
  "profile_index": 0,
  "axis": "x",
  "angle": 360,
  "operation": "new"
}}
```
| Param | Type | Default | Description |
|-------|------|---------|-------------|
| sketch_index | int | last | Sketch containing profile |
| profile_index | int | 0 | Which profile (use `list_profiles`) |
| axis | string | "x" | `"x"`, `"y"`, `"z"` for construction axes, or `"line"` for sketch line |
| axis_line_index | int | 0 | Index of sketch line to use as axis (when axis="line") |
| angle | float | 360 | Degrees to revolve (360 = full revolution) |
| operation | string | "new" | `"new"`, `"join"`, `"cut"` |

**Example: Create a sphere by revolving a semicircle**
```json
// 1. Create sketch on XZ plane
{"id": 1, "action": "create_sketch", "params": {"plane": "xz"}}
// 2. Draw a semicircle profile (half circle + line for axis)
// 3. Revolve around the line
{"id": 3, "action": "revolve", "params": {"axis": "line", "axis_line_index": 0}}
```

### loft
Create a smooth transition between two or more profiles (sketches at different positions).
```json
{"id": 16, "action": "loft", "params": {
  "sections": [
    {"sketch_index": 0, "profile_index": 0},
    {"sketch_index": 1, "profile_index": 0}
  ],
  "operation": "join"
}}
```
| Param | Type | Default | Description |
|-------|------|---------|-------------|
| sections | array | required | List of {sketch_index, profile_index} objects |
| operation | string | "new" | `"new"`, `"join"`, `"cut"` |
| is_solid | bool | true | Create solid (true) or surface (false) |
| is_closed | bool | false | Connect last section back to first |

**Example: Create curved transition between two shapes**
```json
// 1. Create sketch on bottom plane with shape A
{"id": 1, "action": "create_sketch", "params": {"plane": "xy"}}
{"id": 2, "action": "draw_rectangle", "params": {"width": 4, "height": 4}}
// 2. Create offset plane and sketch with shape B
{"id": 3, "action": "create_offset_plane", "params": {"plane": "xy", "offset": 5}}
{"id": 4, "action": "create_sketch", "params": {"plane_index": 0}}
{"id": 5, "action": "draw_circle", "params": {"radius": 2}}
// 3. Loft between them
{"id": 6, "action": "loft", "params": {
  "sections": [
    {"sketch_index": 0, "profile_index": 0},
    {"sketch_index": 1, "profile_index": 0}
  ]
}}
```

### loft_rails
Loft with guide rails for more controlled shape transitions.
```json
{"id": 17, "action": "loft_rails", "params": {
  "sections": [
    {"sketch_index": 0, "profile_index": 0},
    {"sketch_index": 1, "profile_index": 0}
  ],
  "rails": [
    {"sketch_index": 2, "curve_index": 0}
  ],
  "operation": "new"
}}
```
| Param | Type | Default | Description |
|-------|------|---------|-------------|
| sections | array | required | Same as loft |
| rails | array | [] | List of {sketch_index, curve_index} for guide curves |
| operation | string | "new" | `"new"`, `"join"`, `"cut"` |
| is_solid | bool | true | Create solid or surface |

### fillet
Round edges of a body.
```json
{"id": 15, "action": "fillet", "params": {
  "body_index": 0,
  "radius": 0.2,
  "edge_indices": [0, 1, 2]
}}
```
| Param | Type | Default | Description |
|-------|------|---------|-------------|
| body_index | int | 0 | Which body |
| radius | float | 0.1 | Fillet radius (cm) |
| edge_indices | array | all | Specific edges (or omit for all) |

### chamfer
Bevel edges of a body.
```json
{"id": 16, "action": "chamfer", "params": {
  "body_index": 0,
  "distance": 0.1,
  "edge_indices": [0, 1]
}}
```

### shell
Hollow out a body.
```json
{"id": 17, "action": "shell", "params": {
  "body_index": 0,
  "thickness": 0.2,
  "remove_top": true
}}
```
| Param | Type | Default | Description |
|-------|------|---------|-------------|
| body_index | int | 0 | Which body |
| thickness | float | 0.1 | Wall thickness (cm) |
| face_index | int | null | Specific face to remove |
| remove_top | bool | true | Auto-find top face if face_index not set |

---

## Parameters

### set_parameter
Create or update a user parameter.
```json
{"id": 18, "action": "set_parameter", "params": {
  "name": "WallThickness",
  "value": 2,
  "unit": "mm"
}}
```

---

## Units

All dimensions are in **centimeters** (Fusion 360's internal unit):
- 1 cm = 10 mm
- For 50mm, use `5` (cm)
- For 2mm, use `0.2` (cm)

---

## Workflow: Understanding and Modifying a Design

1. **Export session data:**
   ```json
   {"id": 1, "action": "export_session", "params": {}}
   ```

2. **Read the exported files** from the session folder:
   - `design_info.json` for overview
   - `bodies.json` for detailed body geometry
   - `sketches/sketch_N.json` for specific sketch coordinates

3. **Make modifications:**
   - Add fillet/chamfer to existing bodies
   - Create new sketch and cut holes
   - Shell to hollow out
   - Add new features

4. **Export again** to verify changes:
   ```json
   {"id": 99, "action": "export_session", "params": {"name": "after_changes"}}
   ```

---

## File Paths

| File | Purpose |
|------|---------|
| `~/Documents/scripts/fusion_360/ClaudeBridge/commands.json` | Write commands |
| `~/Documents/scripts/fusion_360/ClaudeBridge/results.json` | Read results |
| `~/Documents/scripts/fusion_360/ClaudeBridge/sessions/` | Exported session data |
