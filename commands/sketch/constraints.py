"""
Sketch geometric constraint commands.

See: docs/missing-features.md - Sketch Constraints & Dimensions section
"""

from ...utils import write_result
from ..helpers import get_sketch_by_global_index


def add_constraint_midpoint(command_id, params, ctx):
    """
    Add a midpoint constraint - constrains a point to the midpoint of a line.

    This is commonly used to center a line on the origin.

    Params:
        sketch_index: Sketch index (default: last sketch)
        line_index: Index of the line in the sketch (default: 0)
        point: "origin" to use sketch origin, or {"x": num, "y": num} for a specific point
               (default: "origin")

    Example - center a line on origin:
        {"action": "add_constraint_midpoint", "params": {"line_index": 0}}
    """
    root = ctx.root
    sketch_index = params.get("sketch_index", -1)
    line_index = params.get("line_index", 0)
    point_param = params.get("point", "origin")

    # Get the sketch
    sketch, comp, error = get_sketch_by_global_index(root, sketch_index)
    if error:
        return write_result(command_id, False, None, error)

    # Get the line
    lines = sketch.sketchCurves.sketchLines
    if line_index < 0 or line_index >= lines.count:
        return write_result(
            command_id, False, None,
            f"Invalid line index {line_index}. Sketch has {lines.count} lines."
        )

    line = lines.item(line_index)

    # Get the point to constrain
    if point_param == "origin":
        # Use the sketch's origin point
        point = sketch.originPoint
    else:
        # For future: support arbitrary points
        return write_result(
            command_id, False, None,
            "Currently only 'origin' is supported for the point parameter"
        )

    # Add the midpoint constraint
    try:
        constraints = sketch.geometricConstraints
        constraints.addMidPoint(point, line)

        write_result(command_id, True, {
            "message": f"Midpoint constraint added: origin to line {line_index}",
            "sketch_name": sketch.name,
            "component": comp.name
        })
    except Exception as e:
        write_result(command_id, False, None, f"Failed to add midpoint constraint: {str(e)}")


def get_sketch_constraints(command_id, params, ctx):
    """
    Get all geometric constraints in a sketch.

    Params:
        sketch_index: Sketch index (default: last sketch)

    Returns list of constraints with their types and connected entities.
    """
    root = ctx.root
    sketch_index = params.get("sketch_index", -1)

    # Get the sketch
    sketch, comp, error = get_sketch_by_global_index(root, sketch_index)
    if error:
        return write_result(command_id, False, None, error)

    constraints = sketch.geometricConstraints
    constraint_list = []

    # Constraint type mapping
    constraint_types = {
        0: "Coincident",
        1: "Collinear",
        2: "Concentric",
        3: "Equal",
        4: "Fix",
        5: "Horizontal",
        6: "HorizontalPoints",
        7: "MidPoint",
        8: "Parallel",
        9: "Perpendicular",
        10: "Smooth",
        11: "Symmetry",
        12: "Tangent",
        13: "Vertical",
        14: "VerticalPoints",
        15: "CircularPattern",
        16: "RectangularPattern",
        17: "Offset",
        18: "Mirror"
    }

    for i in range(constraints.count):
        constraint = constraints.item(i)
        c_type = constraint_types.get(constraint.objectType, str(constraint.objectType))

        # Try to get more details about what the constraint connects
        constraint_info = {
            "index": i,
            "type": c_type,
            "is_deletable": constraint.isDeletable if hasattr(constraint, 'isDeletable') else None,
        }

        # Try to identify connected entities based on constraint type
        try:
            # Different constraints have different properties
            if hasattr(constraint, 'point'):
                pt = constraint.point
                constraint_info["point"] = [round(pt.geometry.x, 4), round(pt.geometry.y, 4)]
            if hasattr(constraint, 'line'):
                line = constraint.line
                constraint_info["line_start"] = [round(line.startSketchPoint.geometry.x, 4),
                                                  round(line.startSketchPoint.geometry.y, 4)]
                constraint_info["line_end"] = [round(line.endSketchPoint.geometry.x, 4),
                                                round(line.endSketchPoint.geometry.y, 4)]
            if hasattr(constraint, 'entityOne'):
                constraint_info["entity_one"] = str(constraint.entityOne.objectType)
            if hasattr(constraint, 'entityTwo'):
                constraint_info["entity_two"] = str(constraint.entityTwo.objectType)
        except:
            pass

        constraint_list.append(constraint_info)

    write_result(command_id, True, {
        "sketch_name": sketch.name,
        "component": comp.name,
        "constraint_count": len(constraint_list),
        "constraints": constraint_list
    })


# Future commands:
# - add_constraint_horizontal: Horizontal constraint
# - add_constraint_vertical: Vertical constraint
# - add_constraint_coincident: Connect points
# - add_constraint_tangent: Tangent curves
# - add_constraint_perpendicular: Perpendicular
# - add_constraint_parallel: Parallel lines
# - add_constraint_equal: Equal lengths
# - add_constraint_concentric: Concentric circles

COMMANDS = {
    "add_constraint_midpoint": add_constraint_midpoint,
    "get_sketch_constraints": get_sketch_constraints,
}
