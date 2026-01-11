"""
Feature information collector for session export.
"""

import os
import adsk.fusion
from ..utils import write_json


def _get_hole_type_name(hole_type):
    """Convert HoleTypes enum to readable string."""
    type_map = {
        adsk.fusion.HoleTypes.SimpleHoleType: "simple",
        adsk.fusion.HoleTypes.CounterboreHoleType: "counterbore",
        adsk.fusion.HoleTypes.CountersinkHoleType: "countersink",
    }
    return type_map.get(hole_type, "unknown")


def _get_hole_tap_type_name(tap_type):
    """Convert HoleTapTypes enum to readable string."""
    # Try to get name from enum value
    try:
        # HoleTapTypes enum values: SimpleTapType=0, TappedTapType=1, ClearanceTapType=2
        type_map = {
            0: "simple",
            1: "tapped",
            2: "clearance",
        }
        return type_map.get(int(tap_type), f"unknown_{tap_type}")
    except:
        return "unknown"


def _get_param_value(param):
    """Safely get a parameter value in cm."""
    if param is None:
        return None
    try:
        return round(param.value, 6)
    except:
        return None


def _extract_hole_details(feat):
    """
    Extract detailed information from a HoleFeature.

    Args:
        feat: A HoleFeature object

    Returns:
        dict: Detailed hole information
    """
    details = {
        "hole_type": _get_hole_type_name(feat.holeType),
        "diameter_cm": _get_param_value(feat.holeDiameter),
        "tip_angle_deg": _get_param_value(feat.tipAngle),
        "tap_type": _get_hole_tap_type_name(feat.holeTapType),
    }

    # For tapped holes, holeDiameter returns minor diameter, so also get nominal size
    try:
        tap_type = int(feat.holeTapType)
        if tap_type == 1:  # Tapped
            tapped_info = feat.tappedHoleInfo
            if tapped_info and hasattr(tapped_info, 'holeDiameter'):
                # Get the nominal thread diameter
                details["thread_nominal_diameter_cm"] = round(tapped_info.holeDiameter.value, 6)
                details["thread_minor_diameter_cm"] = details["diameter_cm"]
                details["diameter_cm"] = details["thread_nominal_diameter_cm"]
        elif tap_type == 2:  # Clearance
            clearance_info = feat.clearanceHoleInfo
            if clearance_info and hasattr(clearance_info, 'holeDiameter'):
                details["fastener_diameter_cm"] = round(clearance_info.fastenerDiameter, 6) if hasattr(clearance_info, 'fastenerDiameter') else None
    except:
        pass

    # Add counterbore details if applicable
    if feat.holeType == adsk.fusion.HoleTypes.CounterboreHoleType:
        details["counterbore"] = {
            "depth_cm": _get_param_value(feat.counterboreDepth),
            "diameter_cm": _get_param_value(feat.counterboreDiameter),
        }

    # Add countersink details if applicable
    if feat.holeType == adsk.fusion.HoleTypes.CountersinkHoleType:
        details["countersink"] = {
            "angle_deg": _get_param_value(feat.countersinkAngle),
            "diameter_cm": _get_param_value(feat.countersinkDiameter),
        }

    # Get position if available
    try:
        pos = feat.position
        if pos:
            details["position"] = {
                "x": round(pos.x, 6),
                "y": round(pos.y, 6),
                "z": round(pos.z, 6),
            }
    except:
        pass

    # Get direction if available
    try:
        dir_vec = feat.direction
        if dir_vec:
            details["direction"] = {
                "x": round(dir_vec.x, 6),
                "y": round(dir_vec.y, 6),
                "z": round(dir_vec.z, 6),
            }
    except:
        pass

    # Get thread info if tapped (tap_type == 1)
    try:
        if int(feat.holeTapType) == 1:  # TappedTapType
            thread_info = feat.tappedHoleInfo
            if thread_info:
                details["thread"] = {
                    "designation": thread_info.threadDesignation if hasattr(thread_info, 'threadDesignation') else None,
                    "class": thread_info.threadClass if hasattr(thread_info, 'threadClass') else None,
                    "is_modeled": thread_info.isModeled if hasattr(thread_info, 'isModeled') else None,
                }
    except:
        pass

    # Get face counts
    try:
        details["side_face_count"] = feat.sideFaces.count if feat.sideFaces else 0
        details["end_face_count"] = feat.endFaces.count if feat.endFaces else 0
    except:
        pass

    return details


def export_features(root, all_components, session_dir):
    """
    Export feature timeline information.

    Collects information about all features in the design including
    their type, suppression status, and validity. For hole features,
    extracts detailed hole parameters (diameter, depth, type, etc.).

    Args:
        root: Root component
        all_components: List of all components in the design
        session_dir: Directory to write output files

    Returns:
        int: Number of features exported
    """
    features = []
    global_index = 0

    for comp in all_components:
        for i in range(comp.features.count):
            feat = comp.features.item(i)
            feature_type = feat.objectType.split("::")[-1].replace("Feature", "")

            feature_data = {
                "name": feat.name,
                "index": global_index,
                "component": comp.name,
                "type": feature_type,
                "is_suppressed": feat.isSuppressed,
                "is_valid": feat.isValid
            }

            # Extract detailed hole information
            if feature_type == "Hole":
                try:
                    hole_feat = adsk.fusion.HoleFeature.cast(feat)
                    if hole_feat:
                        feature_data["hole_details"] = _extract_hole_details(hole_feat)
                except Exception as e:
                    feature_data["hole_details_error"] = str(e)

            features.append(feature_data)
            global_index += 1

    write_json(os.path.join(session_dir, "features.json"), {
        "features": features,
        "count": len(features)
    })
    return len(features)
