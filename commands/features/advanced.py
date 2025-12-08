"""
Advanced 3D feature commands: sweep, loft, hole, thread.
"""

import adsk.core
import adsk.fusion

from ...utils import write_result
from ..helpers import get_sketch_by_index, get_operation_type


def loft(command_id, params, ctx):
    """
    Create a loft between two or more profiles to create smooth transitions.

    Params:
        sections: List of section definitions, each with:
            - sketch_index: Index of sketch containing the profile
            - profile_index: Index of profile within sketch (default: 0)
        operation: "new", "join", or "cut" (default: "new")
        is_solid: Whether to create a solid (True) or surface (False). Default: True
        is_closed: Whether the loft is closed (connects last to first). Default: False

    Example:
        {
            "action": "loft",
            "params": {
                "sections": [
                    {"sketch_index": 0, "profile_index": 0},
                    {"sketch_index": 1, "profile_index": 0}
                ],
                "operation": "join"
            }
        }
    """
    sections = params.get("sections", [])
    operation = params.get("operation", "new")
    is_solid = params.get("is_solid", True)
    is_closed = params.get("is_closed", False)

    if len(sections) < 2:
        return write_result(command_id, False, None,
                            "Loft requires at least 2 sections")

    sketches = ctx.sketches
    root = ctx.root
    lofts = root.features.loftFeatures

    # Get operation type
    op, error = get_operation_type(operation)
    if error:
        return write_result(command_id, False, None, error)

    # Create loft input
    loft_input = lofts.createInput(op)
    loft_input.isSolid = is_solid
    loft_input.isClosed = is_closed

    # Add each section (profile)
    for i, section in enumerate(sections):
        sketch_idx = section.get("sketch_index")
        profile_idx = section.get("profile_index", 0)

        if sketch_idx is None:
            return write_result(command_id, False, None,
                                f"Section {i} missing sketch_index")

        sketch, error = get_sketch_by_index(sketches, sketch_idx)
        if error:
            return write_result(command_id, False, None,
                                f"Section {i}: {error}")

        if profile_idx >= sketch.profiles.count:
            return write_result(command_id, False, None,
                                f"Section {i}: Invalid profile_index {profile_idx}. "
                                f"Sketch has {sketch.profiles.count} profiles")

        profile = sketch.profiles.item(profile_idx)
        loft_input.loftSections.add(profile)

    # Create the loft
    try:
        loft_feature = lofts.add(loft_input)
        write_result(command_id, True, {
            "message": f"Created loft with {len(sections)} sections",
            "feature_name": loft_feature.name
        })
    except Exception as e:
        write_result(command_id, False, None, f"Loft failed: {str(e)}")


def loft_rails(command_id, params, ctx):
    """
    Create a loft with guide rails for more controlled transitions.

    Params:
        sections: List of section definitions (same as loft)
        rails: List of rail definitions, each with:
            - sketch_index: Index of sketch containing the rail curve
            - curve_index: Index of curve in sketch (default: 0)
        operation: "new", "join", or "cut" (default: "new")

    Example:
        {
            "action": "loft_rails",
            "params": {
                "sections": [
                    {"sketch_index": 0, "profile_index": 0},
                    {"sketch_index": 1, "profile_index": 0}
                ],
                "rails": [
                    {"sketch_index": 2, "curve_index": 0}
                ],
                "operation": "new"
            }
        }
    """
    sections = params.get("sections", [])
    rails = params.get("rails", [])
    operation = params.get("operation", "new")
    is_solid = params.get("is_solid", True)

    if len(sections) < 2:
        return write_result(command_id, False, None,
                            "Loft requires at least 2 sections")

    sketches = ctx.sketches
    root = ctx.root
    lofts = root.features.loftFeatures

    # Get operation type
    op, error = get_operation_type(operation)
    if error:
        return write_result(command_id, False, None, error)

    # Create loft input
    loft_input = lofts.createInput(op)
    loft_input.isSolid = is_solid

    # Add sections
    for i, section in enumerate(sections):
        sketch_idx = section.get("sketch_index")
        profile_idx = section.get("profile_index", 0)

        if sketch_idx is None:
            return write_result(command_id, False, None,
                                f"Section {i} missing sketch_index")

        sketch, error = get_sketch_by_index(sketches, sketch_idx)
        if error:
            return write_result(command_id, False, None,
                                f"Section {i}: {error}")

        if profile_idx >= sketch.profiles.count:
            return write_result(command_id, False, None,
                                f"Section {i}: Invalid profile_index {profile_idx}")

        profile = sketch.profiles.item(profile_idx)
        loft_input.loftSections.add(profile)

    # Add rails (guide curves)
    for i, rail in enumerate(rails):
        sketch_idx = rail.get("sketch_index")
        curve_idx = rail.get("curve_index", 0)

        if sketch_idx is None:
            return write_result(command_id, False, None,
                                f"Rail {i} missing sketch_index")

        sketch, error = get_sketch_by_index(sketches, sketch_idx)
        if error:
            return write_result(command_id, False, None,
                                f"Rail {i}: {error}")

        # Get the curve from the sketch
        curves = sketch.sketchCurves
        all_curves = []

        # Collect all curves
        for j in range(curves.sketchLines.count):
            line = curves.sketchLines.item(j)
            if not line.isConstruction:
                all_curves.append(line)
        for j in range(curves.sketchArcs.count):
            all_curves.append(curves.sketchArcs.item(j))
        for j in range(curves.sketchCircles.count):
            all_curves.append(curves.sketchCircles.item(j))

        if curve_idx >= len(all_curves):
            return write_result(command_id, False, None,
                                f"Rail {i}: Invalid curve_index {curve_idx}")

        curve = all_curves[curve_idx]
        loft_input.centerLineOrRails.addRail(curve)

    # Create the loft
    try:
        loft_feature = lofts.add(loft_input)
        write_result(command_id, True, {
            "message": f"Created loft with {len(sections)} sections and {len(rails)} rails",
            "feature_name": loft_feature.name
        })
    except Exception as e:
        write_result(command_id, False, None, f"Loft failed: {str(e)}")


COMMANDS = {
    "loft": loft,
    "loft_rails": loft_rails,
}
