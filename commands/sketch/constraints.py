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


def add_constraint_coincident(command_id, params, ctx):
    """
    Add a coincident constraint - constrains a point to lie on a curve (line, circle, arc).

    Params:
        sketch_index: Sketch index (default: last sketch)
        point_type: "line_endpoint" or "circle_center" (what provides the point)
        point_source: For line_endpoint: {"line_index": int, "endpoint": "start"|"end"}
                      For circle_center: {"circle_index": int}
        target_type: "circle", "line", or "point"
        target_index: Index of the target curve/point

    Example - constrain line endpoint to circle:
        {"action": "add_constraint_coincident", "params": {
            "point_type": "line_endpoint",
            "point_source": {"line_index": 11, "endpoint": "end"},
            "target_type": "circle",
            "target_index": 1
        }}
    """
    root = ctx.root
    sketch_index = params.get("sketch_index", -1)
    point_type = params.get("point_type", "line_endpoint")
    point_source = params.get("point_source", {})
    target_type = params.get("target_type", "circle")
    target_index = params.get("target_index", 0)

    # Get the sketch
    sketch, comp, error = get_sketch_by_global_index(root, sketch_index)
    if error:
        return write_result(command_id, False, None, error)

    # Get the point to constrain
    point = None
    point_desc = ""

    if point_type == "line_endpoint":
        line_index = point_source.get("line_index", 0)
        endpoint = point_source.get("endpoint", "end")

        lines = sketch.sketchCurves.sketchLines
        if line_index < 0 or line_index >= lines.count:
            return write_result(
                command_id, False, None,
                f"Invalid line index {line_index}. Sketch has {lines.count} lines."
            )

        line = lines.item(line_index)
        if endpoint == "start":
            point = line.startSketchPoint
        else:
            point = line.endSketchPoint
        point_desc = f"line {line_index} {endpoint} point"

    elif point_type == "circle_center":
        circle_index = point_source.get("circle_index", 0)
        circles = sketch.sketchCurves.sketchCircles
        if circle_index < 0 or circle_index >= circles.count:
            return write_result(
                command_id, False, None,
                f"Invalid circle index {circle_index}. Sketch has {circles.count} circles."
            )
        circle = circles.item(circle_index)
        point = circle.centerSketchPoint
        point_desc = f"circle {circle_index} center"

    else:
        return write_result(
            command_id, False, None,
            f"Unsupported point_type: {point_type}. Use 'line_endpoint' or 'circle_center'."
        )

    # Get the target curve
    target = None
    target_desc = ""

    if target_type == "circle":
        circles = sketch.sketchCurves.sketchCircles
        if target_index < 0 or target_index >= circles.count:
            return write_result(
                command_id, False, None,
                f"Invalid circle index {target_index}. Sketch has {circles.count} circles."
            )
        target = circles.item(target_index)
        target_desc = f"circle {target_index}"

    elif target_type == "line":
        lines = sketch.sketchCurves.sketchLines
        if target_index < 0 or target_index >= lines.count:
            return write_result(
                command_id, False, None,
                f"Invalid line index {target_index}. Sketch has {lines.count} lines."
            )
        target = lines.item(target_index)
        target_desc = f"line {target_index}"

    else:
        return write_result(
            command_id, False, None,
            f"Unsupported target_type: {target_type}. Use 'circle' or 'line'."
        )

    # Add the coincident constraint
    try:
        constraints = sketch.geometricConstraints
        constraints.addCoincident(point, target)

        write_result(command_id, True, {
            "message": f"Coincident constraint added: {point_desc} to {target_desc}",
            "sketch_name": sketch.name,
            "component": comp.name
        })
    except Exception as e:
        write_result(command_id, False, None, f"Failed to add coincident constraint: {str(e)}")


def add_constraint_vertical(command_id, params, ctx):
    """
    Add a vertical constraint to a line.

    Params:
        sketch_index: Sketch index (default: last sketch)
        line_index: Index of the line to make vertical

    Example:
        {"action": "add_constraint_vertical", "params": {"line_index": 5}}
    """
    root = ctx.root
    sketch_index = params.get("sketch_index", -1)
    line_index = params.get("line_index", 0)

    sketch, comp, error = get_sketch_by_global_index(root, sketch_index)
    if error:
        return write_result(command_id, False, None, error)

    lines = sketch.sketchCurves.sketchLines
    if line_index < 0 or line_index >= lines.count:
        return write_result(
            command_id, False, None,
            f"Invalid line index {line_index}. Sketch has {lines.count} lines."
        )

    line = lines.item(line_index)

    try:
        constraints = sketch.geometricConstraints
        constraints.addVertical(line)

        write_result(command_id, True, {
            "message": f"Vertical constraint added to line {line_index}",
            "sketch_name": sketch.name,
            "component": comp.name
        })
    except Exception as e:
        write_result(command_id, False, None, f"Failed to add vertical constraint: {str(e)}")


def add_constraint_horizontal(command_id, params, ctx):
    """
    Add a horizontal constraint to a line.

    Params:
        sketch_index: Sketch index (default: last sketch)
        line_index: Index of the line to make horizontal

    Example:
        {"action": "add_constraint_horizontal", "params": {"line_index": 5}}
    """
    root = ctx.root
    sketch_index = params.get("sketch_index", -1)
    line_index = params.get("line_index", 0)

    sketch, comp, error = get_sketch_by_global_index(root, sketch_index)
    if error:
        return write_result(command_id, False, None, error)

    lines = sketch.sketchCurves.sketchLines
    if line_index < 0 or line_index >= lines.count:
        return write_result(
            command_id, False, None,
            f"Invalid line index {line_index}. Sketch has {lines.count} lines."
        )

    line = lines.item(line_index)

    try:
        constraints = sketch.geometricConstraints
        constraints.addHorizontal(line)

        write_result(command_id, True, {
            "message": f"Horizontal constraint added to line {line_index}",
            "sketch_name": sketch.name,
            "component": comp.name
        })
    except Exception as e:
        write_result(command_id, False, None, f"Failed to add horizontal constraint: {str(e)}")


def add_constraint_coincident_points(command_id, params, ctx):
    """
    Add a coincident constraint between two line endpoints (point-to-point).

    Params:
        sketch_index: Sketch index (default: last sketch)
        line1_index: Index of the first line
        line1_endpoint: "start" or "end" for the first line
        line2_index: Index of the second line
        line2_endpoint: "start" or "end" for the second line

    Example - connect line 10's end to line 11's start:
        {"action": "add_constraint_coincident_points", "params": {
            "line1_index": 10, "line1_endpoint": "end",
            "line2_index": 11, "line2_endpoint": "start"
        }}
    """
    root = ctx.root
    sketch_index = params.get("sketch_index", -1)
    line1_index = params.get("line1_index", 0)
    line1_endpoint = params.get("line1_endpoint", "end")
    line2_index = params.get("line2_index", 1)
    line2_endpoint = params.get("line2_endpoint", "start")

    sketch, comp, error = get_sketch_by_global_index(root, sketch_index)
    if error:
        return write_result(command_id, False, None, error)

    lines = sketch.sketchCurves.sketchLines

    # Get first line and point
    if line1_index < 0 or line1_index >= lines.count:
        return write_result(
            command_id, False, None,
            f"Invalid line1_index {line1_index}. Sketch has {lines.count} lines."
        )
    line1 = lines.item(line1_index)
    point1 = line1.startSketchPoint if line1_endpoint == "start" else line1.endSketchPoint

    # Get second line and point
    if line2_index < 0 or line2_index >= lines.count:
        return write_result(
            command_id, False, None,
            f"Invalid line2_index {line2_index}. Sketch has {lines.count} lines."
        )
    line2 = lines.item(line2_index)
    point2 = line2.startSketchPoint if line2_endpoint == "start" else line2.endSketchPoint

    # Add the coincident constraint between the two points
    try:
        constraints = sketch.geometricConstraints
        constraints.addCoincident(point1, point2)

        write_result(command_id, True, {
            "message": f"Coincident constraint added: line {line1_index} {line1_endpoint} to line {line2_index} {line2_endpoint}",
            "sketch_name": sketch.name,
            "component": comp.name
        })
    except Exception as e:
        write_result(command_id, False, None, f"Failed to add coincident constraint: {str(e)}")


def delete_constraint(command_id, params, ctx):
    """
    Delete a geometric constraint by index.

    Params:
        sketch_index: Sketch index (default: last sketch)
        constraint_index: Index of the constraint to delete

    Example:
        {"action": "delete_constraint", "params": {"constraint_index": 14}}
    """
    root = ctx.root
    sketch_index = params.get("sketch_index", -1)
    constraint_index = params.get("constraint_index", 0)

    sketch, comp, error = get_sketch_by_global_index(root, sketch_index)
    if error:
        return write_result(command_id, False, None, error)

    constraints = sketch.geometricConstraints

    if constraint_index < 0 or constraint_index >= constraints.count:
        return write_result(
            command_id, False, None,
            f"Invalid constraint index {constraint_index}. Sketch has {constraints.count} constraints."
        )

    constraint = constraints.item(constraint_index)

    if not constraint.isDeletable:
        return write_result(
            command_id, False, None,
            f"Constraint {constraint_index} is not deletable."
        )

    try:
        constraint.deleteMe()

        write_result(command_id, True, {
            "message": f"Constraint {constraint_index} deleted",
            "sketch_name": sketch.name,
            "component": comp.name
        })
    except Exception as e:
        write_result(command_id, False, None, f"Failed to delete constraint: {str(e)}")


# Future commands:
# - add_constraint_tangent: Tangent curves
# - add_constraint_perpendicular: Perpendicular
# - add_constraint_parallel: Parallel lines
# - add_constraint_equal: Equal lengths
# - add_constraint_concentric: Concentric circles

COMMANDS = {
    "add_constraint_midpoint": add_constraint_midpoint,
    "add_constraint_coincident": add_constraint_coincident,
    "add_constraint_coincident_points": add_constraint_coincident_points,
    "add_constraint_vertical": add_constraint_vertical,
    "add_constraint_horizontal": add_constraint_horizontal,
    "delete_constraint": delete_constraint,
    "get_sketch_constraints": get_sketch_constraints,
}
