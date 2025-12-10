# ClaudeBridge

A Fusion 360 add-in that enables Claude to programmatically control Autodesk Fusion 360. Create 3D models through natural language by letting Claude send commands directly to Fusion 360.

## Features

- **File-based IPC**: Simple JSON command/response protocol
- **Comprehensive API**: Sketches, extrusions, revolves, fillets, chamfers, and more
- **Claude Code Integration**: Includes a skill for seamless Claude Code usage
- **Extensible**: Modular command architecture for easy customization

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/your-username/ClaudeBridge.git
```

### 2. Install the Add-in

1. Open Fusion 360
2. Create or open a design
3. Press `Shift+S` to open the Scripts and Add-Ins dialog
4. Go to the **Add-Ins** tab
5. Click the **+** button
6. Select **Script or add-in from device**
7. Navigate to and select the cloned `ClaudeBridge` repository folder
8. Select **ClaudeBridge** from the list and click **Run**

The add-in will now load directly from your repository folder, so any changes you make to the code will be reflected after restarting the add-in.

## How It Works

ClaudeBridge uses a file-based IPC (Inter-Process Communication) mechanism:

```
┌─────────────┐     writes      ┌─────────────────┐
│   Claude    │ ──────────────▶ │  commands.json  │
└─────────────┘                 └────────┬────────┘
                                         │ polls (1s)
                                         ▼
                                ┌─────────────────┐
                                │  ClaudeBridge   │
                                │   (Fusion 360)  │
                                └────────┬────────┘
                                         │ writes
                                         ▼
┌─────────────┐     reads       ┌─────────────────┐
│   Claude    │ ◀────────────── │  results.json   │
└─────────────┘                 └─────────────────┘
```

### Command Format

Write commands to `commands.json`:

```json
{
  "id": 1,
  "action": "create_sketch",
  "params": {"plane": "xy"}
}
```

**Important**: The `id` must increment with each command. Duplicate IDs are ignored.

### Response Format

Results appear in `results.json`:

```json
{
  "id": 1,
  "success": true,
  "result": {"sketch_index": 0, "message": "Created sketch on xy plane"},
  "error": null
}
```

## Claude Code Skill

ClaudeBridge includes a Claude Code skill in `.claude/skills/fusion360/` that enables Claude Code to control Fusion 360 interactively.

### Using the Skill

1. Ensure ClaudeBridge is running in Fusion 360
2. In Claude Code, the skill activates automatically when working in this repository
3. Ask Claude to create 3D models: *"Create a 5cm cube with rounded edges"*

The skill provides Claude with:
- Command reference documentation
- Example workflows
- Best practices for 3D modeling

## Available Commands

### Session Export
| Command | Description |
|---------|-------------|
| `export_session` | Export all design data to timestamped folder |

### Connection
| Command | Description |
|---------|-------------|
| `ping` | Test connection |
| `message` | Display message in Fusion 360 |

### Sketching
| Command | Description |
|---------|-------------|
| `create_sketch` | Create sketch on plane |
| `create_sketch_on_face` | Create sketch on body face |
| `draw_circle` | Draw a circle |
| `draw_rectangle` | Draw a rectangle |
| `draw_line` | Draw a line |
| `draw_polygon` | Draw a regular polygon |
| `draw_arc` / `draw_arc_sweep` / `draw_arc_three_points` | Draw arcs |
| `list_profiles` | List available profiles |

### Sketch Constraints
| Command | Description |
|---------|-------------|
| `add_constraint_midpoint` | Constrain point to line midpoint |
| `add_constraint_coincident` | Constrain point to curve |
| `add_constraint_coincident_points` | Constrain two points together |
| `add_constraint_vertical` | Make line vertical |
| `add_constraint_horizontal` | Make line horizontal |
| `get_sketch_constraints` | List all constraints |
| `delete_constraint` | Delete a constraint |

### 3D Features
| Command | Description |
|---------|-------------|
| `extrude` | Extrude a profile |
| `revolve` | Revolve around an axis |
| `loft` / `loft_rails` | Create smooth transitions |
| `fillet` | Round edges |
| `chamfer` | Bevel edges |
| `shell` | Hollow out a body |

### Construction
| Command | Description |
|---------|-------------|
| `create_offset_plane` | Create plane at Z offset |
| `create_plane_at_angle` | Create angled plane |

### Parameters
| Command | Description |
|---------|-------------|
| `set_parameter` | Create/update user parameter |

## Units

All dimensions are in **centimeters** (Fusion 360's internal unit):
- 1 cm = 10 mm
- For a 50mm dimension, use `5`

## Architecture

```
ClaudeBridge/
├── ClaudeBridge.py              # Entry point
├── config.py                    # File paths, settings
├── utils.py                     # JSON utilities
├── core/
│   ├── polling.py               # Background polling thread
│   └── event_handler.py         # Main thread event handler
├── commands/
│   ├── dispatcher.py            # Command routing
│   ├── context.py               # Fusion 360 API abstraction
│   ├── helpers/                 # Shared utilities
│   │   ├── geometry/            # Geometry helpers (bodies, sketches, edges, etc.)
│   │   ├── sketch_curves.py     # Curve accessors
│   │   └── command_utils.py     # Decorators
│   ├── queries/                 # [Deprecated] Use export_session
│   ├── sketch/
│   │   ├── create.py            # Sketch creation
│   │   ├── primitives.py        # Basic shapes
│   │   ├── curves.py            # Arcs
│   │   └── constraints/         # Geometric constraints
│   ├── features/                # 3D operations
│   ├── construction/            # Construction geometry
│   └── export/
│       └── session/             # Session export with collectors
└── .claude/skills/fusion360/    # Claude Code skill
```

See [docs/architecture.md](docs/architecture.md) for detailed architecture documentation.

## Adding New Commands

1. Choose the appropriate module in `commands/`
2. Create a handler function:

```python
def my_command(command_id, params, ctx):
    """Description of command."""
    # Implementation using ctx.design, ctx.root, etc.
    write_result(command_id, True, {"message": "Success"})

COMMANDS = {
    "my_command": my_command,
}
```

3. The command is automatically registered and available

## License

MIT License
