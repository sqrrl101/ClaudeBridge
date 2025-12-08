"""
Sketch-related query commands.
"""

import math

from ...utils import write_result
from ..helpers import get_all_sketches, get_sketch_by_global_index


def get_sketches_detailed(command_id, params, ctx):
    """Get detailed sketch information including curve counts.

    Returns all sketches across all components with global indexing.
    """
    root = ctx.root
    all_sketches = get_all_sketches(root)

    sketch_list = []
    for sketch, global_index, comp in all_sketches:
        curves = sketch.sketchCurves
        sketch_list.append({
            "name": sketch.name,
            "index": global_index,
            "component": comp.name,
            "profile_count": sketch.profiles.count,
            "is_visible": sketch.isVisible,
            "curves": {
                "lines": curves.sketchLines.count,
                "circles": curves.sketchCircles.count,
                "arcs": curves.sketchArcs.count,
                "ellipses": curves.sketchEllipses.count,
                "splines": curves.sketchFittedSplines.count,
                "total": curves.count
            }
        })

    write_result(command_id, True, {"sketches": sketch_list, "count": len(sketch_list)})


def get_sketch_geometry(command_id, params, ctx):
    """Get detailed geometry coordinates for all curves in a sketch.

    Supports global indexing across all components.
    """
    root = ctx.root
    sketch_index = params.get("sketch_index", 0)

    sketch, comp, error = get_sketch_by_global_index(root, sketch_index)
    if error:
        return write_result(command_id, False, None, error)

    curves = sketch.sketchCurves

    # Helper to round coordinates
    def pt(point):
        return [round(point.x, 4), round(point.y, 4), round(point.z, 4)]

    # Extract circles
    circles = []
    for i in range(curves.sketchCircles.count):
        circle = curves.sketchCircles.item(i)
        circles.append({
            "index": i,
            "center": pt(circle.centerSketchPoint.geometry),
            "radius": round(circle.radius, 4),
            "diameter": round(circle.radius * 2, 4),
            "is_construction": circle.isConstruction
        })

    # Extract lines
    lines = []
    for i in range(curves.sketchLines.count):
        line = curves.sketchLines.item(i)
        lines.append({
            "index": i,
            "start": pt(line.startSketchPoint.geometry),
            "end": pt(line.endSketchPoint.geometry),
            "length": round(line.length, 4),
            "is_construction": line.isConstruction
        })

    # Extract arcs
    arcs = []
    for i in range(curves.sketchArcs.count):
        arc = curves.sketchArcs.item(i)
        arcs.append({
            "index": i,
            "center": pt(arc.centerSketchPoint.geometry),
            "radius": round(arc.radius, 4),
            "start_point": pt(arc.startSketchPoint.geometry),
            "end_point": pt(arc.endSketchPoint.geometry),
            "start_angle_deg": round(math.degrees(arc.startAngle), 2),
            "end_angle_deg": round(math.degrees(arc.endAngle), 2),
            "is_construction": arc.isConstruction
        })

    # Extract ellipses
    ellipses = []
    for i in range(curves.sketchEllipses.count):
        ellipse = curves.sketchEllipses.item(i)
        ellipses.append({
            "index": i,
            "center": pt(ellipse.centerSketchPoint.geometry),
            "major_radius": round(ellipse.majorRadius, 4),
            "minor_radius": round(ellipse.minorRadius, 4),
            "is_construction": ellipse.isConstruction
        })

    # Get sketch plane info
    plane_info = {}
    try:
        plane = sketch.referencePlane
        if plane:
            plane_info = {
                "name": plane.name if hasattr(plane, 'name') else "Custom",
            }
    except:
        plane_info = {"name": "Unknown"}

    write_result(command_id, True, {
        "sketch_name": sketch.name,
        "sketch_index": sketch_index,
        "component": comp.name,
        "plane": plane_info,
        "circles": circles,
        "lines": lines,
        "arcs": arcs,
        "ellipses": ellipses,
        "counts": {
            "circles": len(circles),
            "lines": len(lines),
            "arcs": len(arcs),
            "ellipses": len(ellipses),
            "total": len(circles) + len(lines) + len(arcs) + len(ellipses)
        }
    })


COMMANDS = {
    "get_sketches_detailed": get_sketches_detailed,
    "get_sketch_geometry": get_sketch_geometry,
}
