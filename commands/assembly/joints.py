"""
Assembly joint commands.

Commands:
- list_joints: List all joints in the design
- create_joint: Create a joint between two components using geometry
- create_as_built_joint: Create a joint from current component positions
"""

import adsk.core
import adsk.fusion

from ...utils import write_result
from ..helpers import (
    get_occurrence_by_index,
    get_occurrence_by_name,
    get_joint_direction,
    get_joint_type_setter,
    create_joint_geometry_from_spec,
)


def _get_joint_type_name(joint):
    """Get the joint type name from a joint's motion."""
    if joint.jointMotion is None:
        return "Unknown"

    obj_type = joint.jointMotion.objectType

    if "Rigid" in obj_type:
        return "Rigid"
    elif "Revolute" in obj_type:
        return "Revolute"
    elif "Slider" in obj_type:
        return "Slider"
    elif "Cylindrical" in obj_type:
        return "Cylindrical"
    elif "PinSlot" in obj_type:
        return "PinSlot"
    elif "Planar" in obj_type:
        return "Planar"
    elif "Ball" in obj_type:
        return "Ball"
    else:
        return obj_type.split("::")[-1]


def _get_occurrence_name(occ):
    """Get occurrence name safely."""
    if occ is None:
        return "Ground"
    return occ.name


def list_joints(command_id, params, ctx):
    """
    List all joints in the design.

    Returns information about all joints including type, connected
    occurrences, and motion parameters.
    """
    root = ctx.root
    if root is None:
        return write_result(command_id, False, None, "No active design")

    joints_data = []

    # Get regular joints
    all_joints = root.allJoints
    for i in range(all_joints.count):
        joint = all_joints.item(i)
        try:
            joint_info = {
                "index": i,
                "name": joint.name,
                "type": _get_joint_type_name(joint),
                "occurrence_one": _get_occurrence_name(joint.occurrenceOne),
                "occurrence_two": _get_occurrence_name(joint.occurrenceTwo),
                "is_suppressed": joint.isSuppressed,
                "is_locked": joint.isLocked,
                "joint_kind": "joint",
            }
            joints_data.append(joint_info)
        except Exception as e:
            joints_data.append({
                "index": i,
                "error": str(e),
                "joint_kind": "joint",
            })

    # Get as-built joints
    as_built_joints = root.allAsBuiltJoints
    as_built_offset = all_joints.count
    for i in range(as_built_joints.count):
        joint = as_built_joints.item(i)
        try:
            joint_info = {
                "index": as_built_offset + i,
                "as_built_index": i,
                "name": joint.name,
                "type": _get_joint_type_name(joint),
                "occurrence_one": _get_occurrence_name(joint.occurrenceOne),
                "occurrence_two": _get_occurrence_name(joint.occurrenceTwo),
                "is_suppressed": joint.isSuppressed,
                "is_locked": joint.isLocked,
                "joint_kind": "as_built",
            }
            joints_data.append(joint_info)
        except Exception as e:
            joints_data.append({
                "index": as_built_offset + i,
                "as_built_index": i,
                "error": str(e),
                "joint_kind": "as_built",
            })

    write_result(command_id, True, {
        "joints": joints_data,
        "count": len(joints_data),
        "joint_count": all_joints.count,
        "as_built_joint_count": as_built_joints.count,
    })


def create_as_built_joint(command_id, params, ctx):
    """
    Create an as-built joint between two components at their current positions.

    As-built joints are created based on the current position of components,
    making them simpler to set up than regular joints.

    Params:
        occurrence_one_index (int): Index of first occurrence
        occurrence_two_index (int): Index of second occurrence
        joint_type (str): Type of joint motion:
            - "rigid": No movement (fixed)
            - "revolute": Rotation around one axis
            - "slider": Linear movement along one axis
            - "cylindrical": Rotation + linear along same axis
            - "ball": Rotation in all directions
            - "planar": Movement in a plane
            - "pin_slot": Pin-slot constraint
        direction (str, optional): Axis for motion ("x", "y", "z"), default "z"

    Alternative params:
        occurrence_one_name (str): Name of first occurrence
        occurrence_two_name (str): Name of second occurrence
    """
    root = ctx.root
    if root is None:
        return write_result(command_id, False, None, "No active design")

    # Get occurrences
    occ_one_index = params.get("occurrence_one_index")
    occ_two_index = params.get("occurrence_two_index")
    occ_one_name = params.get("occurrence_one_name")
    occ_two_name = params.get("occurrence_two_name")

    # Find first occurrence
    occ1 = None
    if occ_one_index is not None:
        occ1, error = get_occurrence_by_index(root, occ_one_index)
        if error:
            return write_result(command_id, False, None, f"Occurrence one: {error}")
    elif occ_one_name is not None:
        occ1, error = get_occurrence_by_name(root, occ_one_name)
        if error:
            return write_result(command_id, False, None, f"Occurrence one: {error}")
    else:
        return write_result(command_id, False, None,
                            "Provide occurrence_one_index or occurrence_one_name")

    # Find second occurrence
    occ2 = None
    if occ_two_index is not None:
        occ2, error = get_occurrence_by_index(root, occ_two_index)
        if error:
            return write_result(command_id, False, None, f"Occurrence two: {error}")
    elif occ_two_name is not None:
        occ2, error = get_occurrence_by_name(root, occ_two_name)
        if error:
            return write_result(command_id, False, None, f"Occurrence two: {error}")
    else:
        return write_result(command_id, False, None,
                            "Provide occurrence_two_index or occurrence_two_name")

    # Get joint type and direction
    joint_type = params.get("joint_type", "rigid")
    direction = params.get("direction", "z")

    # Validate joint type
    setter_method, error = get_joint_type_setter(joint_type)
    if error:
        return write_result(command_id, False, None, error)

    # Validate direction
    joint_direction, error = get_joint_direction(direction)
    if error:
        return write_result(command_id, False, None, error)

    # Create as-built joint input
    as_built_joints = root.asBuiltJoints
    joint_input = as_built_joints.createInput(occ1, occ2, None)

    if joint_input is None:
        return write_result(command_id, False, None, "Failed to create joint input")

    # Set joint motion type
    try:
        if joint_type == "rigid":
            joint_input.setAsRigidJointMotion()
        elif joint_type == "revolute":
            joint_input.setAsRevoluteJointMotion(joint_direction)
        elif joint_type == "slider":
            joint_input.setAsSliderJointMotion(joint_direction)
        elif joint_type == "cylindrical":
            joint_input.setAsCylindricalJointMotion(joint_direction)
        elif joint_type == "ball":
            joint_input.setAsBallJointMotion()
        elif joint_type == "planar":
            joint_input.setAsPlanarJointMotion(joint_direction)
        elif joint_type == "pin_slot":
            joint_input.setAsPinSlotJointMotion(joint_direction, joint_direction)
    except Exception as e:
        return write_result(command_id, False, None, f"Failed to set joint motion: {str(e)}")

    # Create the joint
    try:
        joint = as_built_joints.add(joint_input)
    except Exception as e:
        return write_result(command_id, False, None, f"Failed to create joint: {str(e)}")

    if joint is None:
        return write_result(command_id, False, None, "Joint creation returned None")

    # Get joint index
    joint_index = as_built_joints.count - 1

    write_result(command_id, True, {
        "message": f"Created {joint_type} as-built joint '{joint.name}'",
        "joint_index": joint_index,
        "joint_name": joint.name,
        "joint_type": joint_type,
        "occurrence_one": occ1.name,
        "occurrence_two": occ2.name,
    })


def create_joint(command_id, params, ctx):
    """
    Create a joint between two components using geometry specifications.

    This creates a joint by specifying the geometry (faces, edges) on each
    component that defines the joint location and orientation.

    Params:
        occurrence_one_index (int): Index of first occurrence
        occurrence_two_index (int): Index of second occurrence
        geometry_one (dict): Geometry specification for first occurrence:
            - type: "face" or "edge"
            - body_index: Index of body (default 0)
            - face_index: Index of face (for type="face")
            - edge_index: Index of edge (for type="edge")
            - key_point: "center", "start", "end", "middle" (optional)
        geometry_two (dict): Geometry specification for second occurrence
        joint_type (str): Type of joint motion (default "rigid")
        direction (str, optional): Axis for motion ("x", "y", "z")
        angle (float, optional): Angle offset in degrees
        offset (float, optional): Offset distance in cm
        is_flipped (bool, optional): Flip orientation

    Alternative params:
        occurrence_one_name (str): Name of first occurrence
        occurrence_two_name (str): Name of second occurrence
    """
    root = ctx.root
    if root is None:
        return write_result(command_id, False, None, "No active design")

    # Get occurrences
    occ_one_index = params.get("occurrence_one_index")
    occ_two_index = params.get("occurrence_two_index")
    occ_one_name = params.get("occurrence_one_name")
    occ_two_name = params.get("occurrence_two_name")

    # Find first occurrence
    occ1 = None
    if occ_one_index is not None:
        occ1, error = get_occurrence_by_index(root, occ_one_index)
        if error:
            return write_result(command_id, False, None, f"Occurrence one: {error}")
    elif occ_one_name is not None:
        occ1, error = get_occurrence_by_name(root, occ_one_name)
        if error:
            return write_result(command_id, False, None, f"Occurrence one: {error}")
    else:
        return write_result(command_id, False, None,
                            "Provide occurrence_one_index or occurrence_one_name")

    # Find second occurrence
    occ2 = None
    if occ_two_index is not None:
        occ2, error = get_occurrence_by_index(root, occ_two_index)
        if error:
            return write_result(command_id, False, None, f"Occurrence two: {error}")
    elif occ_two_name is not None:
        occ2, error = get_occurrence_by_name(root, occ_two_name)
        if error:
            return write_result(command_id, False, None, f"Occurrence two: {error}")
    else:
        return write_result(command_id, False, None,
                            "Provide occurrence_two_index or occurrence_two_name")

    # Get geometry specifications
    geometry_one = params.get("geometry_one")
    geometry_two = params.get("geometry_two")

    if geometry_one is None:
        return write_result(command_id, False, None, "geometry_one is required")
    if geometry_two is None:
        return write_result(command_id, False, None, "geometry_two is required")

    # Create joint geometries
    geo1, error = create_joint_geometry_from_spec(occ1, geometry_one)
    if error:
        return write_result(command_id, False, None, f"Geometry one: {error}")

    geo2, error = create_joint_geometry_from_spec(occ2, geometry_two)
    if error:
        return write_result(command_id, False, None, f"Geometry two: {error}")

    # Get joint parameters
    joint_type = params.get("joint_type", "rigid")
    direction = params.get("direction", "z")
    angle = params.get("angle", 0)
    offset = params.get("offset", 0)
    is_flipped = params.get("is_flipped", False)

    # Validate joint type and direction
    setter_method, error = get_joint_type_setter(joint_type)
    if error:
        return write_result(command_id, False, None, error)

    joint_direction, error = get_joint_direction(direction)
    if error:
        return write_result(command_id, False, None, error)

    # Create joint input
    joints = root.joints
    joint_input = joints.createInput(geo1, geo2)

    if joint_input is None:
        return write_result(command_id, False, None, "Failed to create joint input")

    # Set angle and offset if provided
    if angle != 0:
        import math
        angle_value = adsk.core.ValueInput.createByReal(math.radians(angle))
        joint_input.angle = angle_value

    if offset != 0:
        offset_value = adsk.core.ValueInput.createByReal(offset)
        joint_input.offset = offset_value

    if is_flipped:
        joint_input.isFlipped = True

    # Set joint motion type
    try:
        if joint_type == "rigid":
            joint_input.setAsRigidJointMotion()
        elif joint_type == "revolute":
            joint_input.setAsRevoluteJointMotion(joint_direction)
        elif joint_type == "slider":
            joint_input.setAsSliderJointMotion(joint_direction)
        elif joint_type == "cylindrical":
            joint_input.setAsCylindricalJointMotion(joint_direction)
        elif joint_type == "ball":
            joint_input.setAsBallJointMotion()
        elif joint_type == "planar":
            joint_input.setAsPlanarJointMotion(joint_direction)
        elif joint_type == "pin_slot":
            joint_input.setAsPinSlotJointMotion(joint_direction, joint_direction)
    except Exception as e:
        return write_result(command_id, False, None, f"Failed to set joint motion: {str(e)}")

    # Create the joint
    try:
        joint = joints.add(joint_input)
    except Exception as e:
        return write_result(command_id, False, None, f"Failed to create joint: {str(e)}")

    if joint is None:
        return write_result(command_id, False, None, "Joint creation returned None")

    # Get joint index
    joint_index = joints.count - 1

    write_result(command_id, True, {
        "message": f"Created {joint_type} joint '{joint.name}'",
        "joint_index": joint_index,
        "joint_name": joint.name,
        "joint_type": joint_type,
        "occurrence_one": occ1.name,
        "occurrence_two": occ2.name,
    })


COMMANDS = {
    "list_joints": list_joints,
    "create_joint": create_joint,
    "create_as_built_joint": create_as_built_joint,
}
