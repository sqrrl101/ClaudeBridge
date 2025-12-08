"""
Command handlers for Claude Bridge.

Each command is a function that takes (command_id, params, ctx) where ctx
is a context object with access to Fusion 360 objects.

Architecture:
    commands/
    ├── __init__.py          # This file - command registry
    ├── dispatcher.py        # Central command routing
    ├── context.py           # Fusion 360 API abstraction
    ├── basic.py             # ping, message
    ├── parameters.py        # set_parameter
    ├── helpers/             # Shared utilities
    │   ├── geometry.py      # Face/edge/body selection
    │   └── validation.py    # Parameter validation
    ├── queries/             # [DEPRECATED] Use export_session instead
    ├── sketch/              # Sketch operations
    │   ├── create.py        # create_sketch, create_sketch_on_face
    │   ├── primitives.py    # draw_circle, draw_rectangle, draw_line
    │   ├── curves.py        # draw_arc, draw_arc_sweep, draw_arc_three_points
    │   ├── operations.py    # [future] project, offset, mirror
    │   ├── constraints.py   # coincident, vertical, horizontal constraints
    │   └── dimensions.py    # [future] parametric dimensions
    ├── features/            # 3D feature creation
    │   ├── basic.py         # extrude, revolve, list_profiles
    │   ├── modify.py        # fillet, chamfer, shell
    │   ├── advanced.py      # loft, loft_rails
    │   ├── patterns.py      # [future] rectangular, circular, mirror
    │   └── body_ops.py      # [future] combine, split, move, scale
    ├── construction/        # Construction geometry
    │   └── planes.py        # create_offset_plane, create_plane_at_angle
    ├── timeline/            # [future] Delete, suppress, rollback
    ├── assembly/            # [future] Components and joints
    └── export/              # Export operations
        └── session.py       # export_session - exports all design data

To add a new command:
    1. Add handler function to appropriate sub-module
    2. Add to that module's COMMANDS dict
    3. The registry automatically merges all COMMANDS
"""

# Core modules (kept at root level)
from .basic import COMMANDS as BASIC_COMMANDS
from .parameters import COMMANDS as PARAM_COMMANDS

# Sub-module packages
from .queries import COMMANDS as QUERY_COMMANDS
from .sketch import COMMANDS as SKETCH_COMMANDS
from .features import COMMANDS as FEATURE_COMMANDS
from .construction import COMMANDS as CONSTRUCTION_COMMANDS
from .timeline import COMMANDS as TIMELINE_COMMANDS
from .assembly import COMMANDS as ASSEMBLY_COMMANDS
from .export import COMMANDS as EXPORT_COMMANDS

# Build the unified command registry
COMMAND_REGISTRY = {}
COMMAND_REGISTRY.update(BASIC_COMMANDS)
COMMAND_REGISTRY.update(PARAM_COMMANDS)
COMMAND_REGISTRY.update(QUERY_COMMANDS)
COMMAND_REGISTRY.update(SKETCH_COMMANDS)
COMMAND_REGISTRY.update(FEATURE_COMMANDS)
COMMAND_REGISTRY.update(CONSTRUCTION_COMMANDS)
COMMAND_REGISTRY.update(TIMELINE_COMMANDS)
COMMAND_REGISTRY.update(ASSEMBLY_COMMANDS)
COMMAND_REGISTRY.update(EXPORT_COMMANDS)


def get_handler(action: str):
    """Get the handler function for a given action."""
    return COMMAND_REGISTRY.get(action)


def list_actions():
    """Return list of all registered action names."""
    return list(COMMAND_REGISTRY.keys())


# Export the dispatcher for use by the main module
from .dispatcher import execute_command
