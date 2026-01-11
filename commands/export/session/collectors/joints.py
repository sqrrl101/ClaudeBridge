"""
Joint/assembly information collector for session export.
"""

import os
import adsk.fusion
from ..utils import write_json


def get_joint_type_from_motion(joint_motion):
    """Determine joint type from the jointMotion object type."""
    if joint_motion is None:
        return "Unknown"

    obj_type = joint_motion.objectType

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


def get_joint_motion_info(joint):
    """Extract motion-specific information from a joint."""
    motion_info = {}

    try:
        joint_motion = joint.jointMotion
        joint_type = get_joint_type_from_motion(joint_motion)

        if joint_type == "Revolute":
            motion_info["motion_type"] = "Revolute"
            motion_info["rotation_axis"] = get_vector_dict(joint_motion.rotationAxisVector)
            motion_info["rotation_value_deg"] = round(joint_motion.rotationValue * 180 / 3.14159265, 4)

            # Rotation limits
            if joint_motion.rotationLimits:
                limits = joint_motion.rotationLimits
                motion_info["rotation_limits"] = {
                    "is_minimum_enabled": limits.isMinimumValueEnabled,
                    "is_maximum_enabled": limits.isMaximumValueEnabled,
                    "minimum_deg": round(limits.minimumValue * 180 / 3.14159265, 4) if limits.isMinimumValueEnabled else None,
                    "maximum_deg": round(limits.maximumValue * 180 / 3.14159265, 4) if limits.isMaximumValueEnabled else None,
                }

        elif joint_type == "Slider":
            motion_info["motion_type"] = "Slider"
            motion_info["slide_axis"] = get_vector_dict(joint_motion.slideDirectionVector)
            motion_info["slide_value_cm"] = round(joint_motion.slideValue, 4)

        elif joint_type == "Cylindrical":
            motion_info["motion_type"] = "Cylindrical"
            motion_info["rotation_value_deg"] = round(joint_motion.rotationValue * 180 / 3.14159265, 4)
            motion_info["slide_value_cm"] = round(joint_motion.slideValue, 4)

        elif joint_type == "Ball":
            motion_info["motion_type"] = "Ball"
            motion_info["pitch_deg"] = round(joint_motion.pitchValue * 180 / 3.14159265, 4)
            motion_info["yaw_deg"] = round(joint_motion.yawValue * 180 / 3.14159265, 4)
            motion_info["roll_deg"] = round(joint_motion.rollValue * 180 / 3.14159265, 4)

        elif joint_type == "Rigid":
            motion_info["motion_type"] = "Rigid"
            motion_info["note"] = "No degrees of freedom"

        elif joint_type == "Planar":
            motion_info["motion_type"] = "Planar"
            motion_info["primary_slide_cm"] = round(joint_motion.primarySlideValue, 4)
            motion_info["secondary_slide_cm"] = round(joint_motion.secondarySlideValue, 4)
            motion_info["rotation_deg"] = round(joint_motion.rotationValue * 180 / 3.14159265, 4)

        else:
            motion_info["motion_type"] = joint_type

    except Exception as e:
        motion_info["error"] = str(e)

    return motion_info


def get_vector_dict(vector):
    """Convert a Vector3D to a dictionary."""
    if vector is None:
        return None
    return {
        "x": round(vector.x, 6),
        "y": round(vector.y, 6),
        "z": round(vector.z, 6)
    }


def get_point_dict(point):
    """Convert a Point3D to a dictionary."""
    if point is None:
        return None
    return {
        "x": round(point.x, 4),
        "y": round(point.y, 4),
        "z": round(point.z, 4)
    }


def get_occurrence_info(occurrence):
    """Get information about a joint occurrence (component instance)."""
    if occurrence is None:
        return {"name": "Ground", "component": "Ground", "is_grounded": True}

    try:
        return {
            "name": occurrence.name,
            "component": occurrence.component.name if occurrence.component else "Unknown",
            "is_grounded": occurrence.isGrounded,
            "is_visible": occurrence.isVisible,
            "path": occurrence.fullPathName if hasattr(occurrence, 'fullPathName') else occurrence.name
        }
    except:
        return {"name": str(occurrence), "component": "Unknown"}


def export_joints(root, session_dir):
    """
    Export all joint information from the design.

    Args:
        root: Root component of the design
        session_dir: Directory to write output files

    Returns:
        int: Number of joints exported
    """
    joints_data = []

    # Get all joints in the design
    all_joints = root.allJoints

    # Iterate using enumeration (JointList is directly iterable)
    for i, joint in enumerate(all_joints):
        try:
            # Get joint type from jointMotion object
            joint_type = get_joint_type_from_motion(joint.jointMotion)

            joint_info = {
                "index": i,
                "name": joint.name,
                "type": joint_type,
                "occurrence_one": get_occurrence_info(joint.occurrenceOne),
                "occurrence_two": get_occurrence_info(joint.occurrenceTwo),
                "is_suppressed": joint.isSuppressed,
                "is_locked": joint.isLocked,
            }

            # Get geometry origin if available
            try:
                geometry = joint.geometryOrOriginOne
                if geometry and hasattr(geometry, 'origin'):
                    joint_info["origin"] = get_point_dict(geometry.origin)
            except:
                pass

            # Get motion-specific info
            joint_info["motion"] = get_joint_motion_info(joint)

            joints_data.append(joint_info)

        except Exception as e:
            joints_data.append({
                "index": i,
                "error": str(e)
            })

    # Also collect joint origins (As-built joints use JointOrigins)
    joint_origins = []
    try:
        all_joint_origins = root.allJointOrigins
        for i, jo in enumerate(all_joint_origins):
            try:
                joint_origins.append({
                    "index": i,
                    "name": jo.name,
                    "component": jo.parentComponent.name if jo.parentComponent else "Unknown",
                    "origin": get_point_dict(jo.geometry.origin) if jo.geometry else None
                })
            except Exception as e:
                joint_origins.append({"index": i, "error": str(e)})
    except:
        pass

    # Check for grounded occurrences
    grounded_components = []
    try:
        all_occurrences = root.allOccurrences
        for occ in all_occurrences:
            if occ.isGrounded:
                grounded_components.append({
                    "name": occ.name,
                    "component": occ.component.name if occ.component else "Unknown",
                    "path": occ.fullPathName if hasattr(occ, 'fullPathName') else occ.name
                })
    except:
        pass

    # Build output data
    data = {
        "joints": joints_data,
        "joint_origins": joint_origins,
        "grounded_components": grounded_components,
        "summary": {
            "joint_count": len(joints_data),
            "joint_origin_count": len(joint_origins),
            "grounded_count": len(grounded_components)
        }
    }

    write_json(os.path.join(session_dir, "joints.json"), data)
    return len(joints_data)
