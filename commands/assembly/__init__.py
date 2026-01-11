"""
Component and assembly commands.

Sub-modules:
- components: Component management (create, activate, ground, list)
- joints: Assembly joints (create, create_as_built, list)

Commands:
- list_components: List all components/occurrences
- create_component: Create a new component
- activate_component: Activate a component for editing
- ground_component: Ground/unground a component
- list_joints: List all joints
- create_joint: Create a joint using geometry
- create_as_built_joint: Create a joint from current positions
"""

try:
    from .components import COMMANDS as COMPONENT_COMMANDS
except ImportError:
    COMPONENT_COMMANDS = {}

try:
    from .joints import COMMANDS as JOINT_COMMANDS
except ImportError:
    JOINT_COMMANDS = {}

# Merge all assembly commands
COMMANDS = {}
COMMANDS.update(COMPONENT_COMMANDS)
COMMANDS.update(JOINT_COMMANDS)
