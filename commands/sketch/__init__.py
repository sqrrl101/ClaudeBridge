"""
Sketch creation and drawing commands.

Sub-modules:
- create: Sketch creation (create_sketch)
- primitives: Basic shapes (draw_circle, draw_rectangle, draw_line, draw_polygon)
- curves: Advanced curves (draw_arc, draw_ellipse, draw_spline, draw_slot) [placeholder]
- text: Text commands (draw_text, emboss_text)
- operations: Sketch operations (project, offset, mirror) [placeholder]
- constraints: Geometric constraints [placeholder]
- dimensions: Parametric dimensions [placeholder]
"""

from .create import COMMANDS as CREATE_COMMANDS
from .primitives import COMMANDS as PRIMITIVE_COMMANDS

# Import text commands
try:
    from .text import COMMANDS as TEXT_COMMANDS
except ImportError:
    TEXT_COMMANDS = {}

# Import placeholder modules if they have commands
try:
    from .curves import COMMANDS as CURVE_COMMANDS
except ImportError:
    CURVE_COMMANDS = {}

try:
    from .operations import COMMANDS as OPERATION_COMMANDS
except ImportError:
    OPERATION_COMMANDS = {}

try:
    from .constraints import COMMANDS as CONSTRAINT_COMMANDS
except ImportError:
    CONSTRAINT_COMMANDS = {}

try:
    from .dimensions import COMMANDS as DIMENSION_COMMANDS
except ImportError:
    DIMENSION_COMMANDS = {}

# Merge all sketch commands
COMMANDS = {}
COMMANDS.update(CREATE_COMMANDS)
COMMANDS.update(PRIMITIVE_COMMANDS)
COMMANDS.update(TEXT_COMMANDS)
COMMANDS.update(CURVE_COMMANDS)
COMMANDS.update(OPERATION_COMMANDS)
COMMANDS.update(CONSTRAINT_COMMANDS)
COMMANDS.update(DIMENSION_COMMANDS)
