"""
Component management commands for assembly operations.

Commands:
- list_components: List all components/occurrences in the design
- create_component: Create a new component
- activate_component: Activate a component for editing
- ground_component: Ground/unground a component
"""

import adsk.core
import adsk.fusion

from ...utils import write_result
from ..helpers import (
    get_occurrence_by_index,
    get_occurrence_by_name,
    create_transform_matrix,
)


def list_components(command_id, params, ctx):
    """
    List all components and occurrences in the design.

    Returns information about all component instances (occurrences) including
    their names, grounding status, and visibility.
    """
    root = ctx.root
    if root is None:
        return write_result(command_id, False, None, "No active design")

    components = []

    # Add root component info
    components.append({
        "index": -1,
        "name": root.name,
        "component": root.name,
        "is_root": True,
        "is_grounded": True,
        "is_visible": True,
        "body_count": root.bRepBodies.count,
    })

    # Add all occurrences
    all_occs = root.allOccurrences
    for i in range(all_occs.count):
        occ = all_occs.item(i)
        comp = occ.component

        components.append({
            "index": i,
            "name": occ.name,
            "component": comp.name if comp else "Unknown",
            "is_root": False,
            "is_grounded": occ.isGrounded,
            "is_visible": occ.isVisible,
            "body_count": comp.bRepBodies.count if comp else 0,
            "path": occ.fullPathName if hasattr(occ, 'fullPathName') else occ.name,
        })

    write_result(command_id, True, {
        "components": components,
        "count": len(components),
        "occurrence_count": all_occs.count,
    })


def create_component(command_id, params, ctx):
    """
    Create a new component (sub-assembly).

    Params:
        name (str, optional): Name for the new component
        x, y, z (float, optional): Translation position in cm
        rx, ry, rz (float, optional): Rotation angles in degrees

    Returns:
        occurrence_index: Index of the new occurrence
        component_name: Name of the new component
    """
    root = ctx.root
    if root is None:
        return write_result(command_id, False, None, "No active design")

    # Get parameters
    name = params.get("name")
    x = params.get("x", 0)
    y = params.get("y", 0)
    z = params.get("z", 0)
    rx = params.get("rx", 0)
    ry = params.get("ry", 0)
    rz = params.get("rz", 0)

    # Create transform matrix
    transform = create_transform_matrix(x, y, z, rx, ry, rz)

    # Create new component
    occurrences = root.occurrences
    new_occ = occurrences.addNewComponent(transform)

    if new_occ is None:
        return write_result(command_id, False, None, "Failed to create component")

    # Set name if provided
    if name:
        new_occ.component.name = name

    # Get the index of the new occurrence
    all_occs = root.allOccurrences
    occ_index = all_occs.count - 1

    write_result(command_id, True, {
        "message": f"Created component '{new_occ.component.name}'",
        "occurrence_index": occ_index,
        "component_name": new_occ.component.name,
        "occurrence_name": new_occ.name,
    })


def activate_component(command_id, params, ctx):
    """
    Activate a component for editing.

    When a component is activated, sketch and feature operations will
    be performed within that component's context.

    Params:
        occurrence_index (int, optional): Index of occurrence to activate
        name (str, optional): Name of component to activate
        activate_root (bool, optional): If True, activate root component

    Note: Provide either occurrence_index, name, or activate_root=True
    """
    design = ctx.design
    root = ctx.root

    if design is None or root is None:
        return write_result(command_id, False, None, "No active design")

    activate_root = params.get("activate_root", False)
    occurrence_index = params.get("occurrence_index")
    name = params.get("name")

    if activate_root:
        # Activate root component
        design.activateRootComponent()
        write_result(command_id, True, {
            "message": f"Activated root component '{root.name}'",
            "activated_component": root.name,
            "is_root": True,
        })
        return

    # Find the occurrence to activate
    occ = None
    if occurrence_index is not None:
        occ, error = get_occurrence_by_index(root, occurrence_index)
        if error:
            return write_result(command_id, False, None, error)
    elif name is not None:
        occ, error = get_occurrence_by_name(root, name)
        if error:
            return write_result(command_id, False, None, error)
    else:
        return write_result(command_id, False, None,
                            "Provide occurrence_index, name, or activate_root=True")

    # Activate the component
    comp = occ.component
    if comp is None:
        return write_result(command_id, False, None, "Occurrence has no component")

    design.activateComponent = comp

    write_result(command_id, True, {
        "message": f"Activated component '{comp.name}'",
        "activated_component": comp.name,
        "occurrence_name": occ.name,
        "is_root": False,
    })


def ground_component(command_id, params, ctx):
    """
    Ground or unground a component (fix it in place).

    A grounded component is fixed in position and cannot be moved by joints
    or assembly constraints.

    Params:
        occurrence_index (int): Index of occurrence to ground/unground
        grounded (bool, optional): True to ground, False to unground (default: True)

    Alternative params:
        name (str): Name of occurrence to ground/unground
    """
    root = ctx.root
    if root is None:
        return write_result(command_id, False, None, "No active design")

    grounded = params.get("grounded", True)
    occurrence_index = params.get("occurrence_index")
    name = params.get("name")

    # Find the occurrence
    occ = None
    if occurrence_index is not None:
        occ, error = get_occurrence_by_index(root, occurrence_index)
        if error:
            return write_result(command_id, False, None, error)
    elif name is not None:
        occ, error = get_occurrence_by_name(root, name)
        if error:
            return write_result(command_id, False, None, error)
    else:
        return write_result(command_id, False, None,
                            "Provide occurrence_index or name")

    # Set grounded state
    occ.isGrounded = grounded

    status = "grounded" if grounded else "ungrounded"
    write_result(command_id, True, {
        "message": f"Component '{occ.name}' is now {status}",
        "occurrence_name": occ.name,
        "component_name": occ.component.name if occ.component else "Unknown",
        "is_grounded": occ.isGrounded,
    })


COMMANDS = {
    "list_components": list_components,
    "create_component": create_component,
    "activate_component": activate_component,
    "ground_component": ground_component,
}
