"""
Session export command - exports complete design data to a timestamped folder.

This consolidates all query functionality into a single export that creates
JSON files for each data type, enabling AI to read files directly without
multiple round-trip commands.
"""

import os
import json
import math
from datetime import datetime

from ...config import BASE_DIR
from ...utils import write_result


def _collect_all_components(root):
    """Recursively collect all components in the design hierarchy."""
    components = [root]

    def traverse_occurrences(occurrences):
        for i in range(occurrences.count):
            occ = occurrences.item(i)
            comp = occ.component
            components.append(comp)
            if comp.occurrences.count > 0:
                traverse_occurrences(comp.occurrences)

    traverse_occurrences(root.occurrences)
    return components


def _write_json(filepath, data):
    """Write JSON to file with pretty formatting."""
    with open(filepath, 'w') as f:
        json.dump(data, f, indent=2)


def _pt(point):
    """Round point coordinates."""
    return [round(point.x, 4), round(point.y, 4), round(point.z, 4)]


def _export_design_info(design, root, all_components, session_dir):
    """Export design overview information."""
    # Bodies summary
    bodies = []
    global_body_index = 0
    for comp in all_components:
        for i in range(comp.bRepBodies.count):
            body = comp.bRepBodies.item(i)
            bbox = body.boundingBox
            bodies.append({
                "name": body.name,
                "index": global_body_index,
                "component": comp.name,
                "volume_cm3": round(body.volume, 4) if body.volume else None,
                "face_count": body.faces.count,
                "size": [
                    round(bbox.maxPoint.x - bbox.minPoint.x, 4),
                    round(bbox.maxPoint.y - bbox.minPoint.y, 4),
                    round(bbox.maxPoint.z - bbox.minPoint.z, 4)
                ]
            })
            global_body_index += 1

    # Sketches summary
    sketch_list = []
    global_sketch_index = 0
    for comp in all_components:
        for i in range(comp.sketches.count):
            sketch = comp.sketches.item(i)
            sketch_list.append({
                "name": sketch.name,
                "index": global_sketch_index,
                "component": comp.name,
                "profiles": sketch.profiles.count,
                "curves": sketch.sketchCurves.count
            })
            global_sketch_index += 1

    # Features summary
    features = []
    global_feature_index = 0
    for comp in all_components:
        for i in range(comp.features.count):
            feat = comp.features.item(i)
            features.append({
                "name": feat.name,
                "index": global_feature_index,
                "component": comp.name,
                "type": feat.objectType.split("::")[-1].replace("Feature", "")
            })
            global_feature_index += 1

    # Components summary
    components = []
    for comp in all_components:
        components.append({
            "name": comp.name,
            "bodies": comp.bRepBodies.count,
            "sketches": comp.sketches.count,
            "features": comp.features.count
        })

    # Parameters summary
    params_list = []
    for i in range(design.userParameters.count):
        param = design.userParameters.item(i)
        params_list.append({
            "name": param.name,
            "value": f"{param.expression} ({param.value} {param.unit})"
        })

    data = {
        "name": design.rootComponent.name,
        "components": components,
        "bodies": bodies,
        "sketches": sketch_list,
        "features": features,
        "parameters": params_list,
        "summary": {
            "component_count": len(all_components),
            "body_count": len(bodies),
            "sketch_count": len(sketch_list),
            "feature_count": len(features),
            "parameter_count": len(params_list)
        }
    }

    _write_json(os.path.join(session_dir, "design_info.json"), data)
    return data["summary"]


def _export_bodies(root, all_components, session_dir):
    """Export detailed body information including circular edges."""
    bodies = []
    global_index = 0

    for comp in all_components:
        for i in range(comp.bRepBodies.count):
            body = comp.bRepBodies.item(i)
            bbox = body.boundingBox

            # Count face types
            face_types = {}
            for face in body.faces:
                ft = face.geometry.surfaceType
                type_names = {
                    0: "Plane", 1: "Cylinder", 2: "Cone", 3: "Sphere",
                    4: "Torus", 5: "EllipticalCylinder", 6: "EllipticalCone", 7: "NURBS"
                }
                type_name = type_names.get(ft, "Other")
                face_types[type_name] = face_types.get(type_name, 0) + 1

            # Collect circular edges
            circular_edges = []
            for edge_idx, edge in enumerate(body.edges):
                geom = edge.geometry
                curve_type = geom.curveType

                if curve_type == 2:  # Circle
                    try:
                        center = geom.center
                        radius_cm = geom.radius
                        diameter_mm = radius_cm * 2 * 10
                        circular_edges.append({
                            "edge_index": edge_idx,
                            "type": "circle",
                            "center": _pt(center),
                            "radius_cm": round(radius_cm, 4),
                            "diameter_mm": round(diameter_mm, 2),
                            "circumference_mm": round(2 * math.pi * radius_cm * 10, 2)
                        })
                    except:
                        pass
                elif curve_type == 5:  # Ellipse
                    try:
                        center = geom.center
                        major = geom.majorRadius
                        minor = geom.minorRadius
                        circular_edges.append({
                            "edge_index": edge_idx,
                            "type": "ellipse",
                            "center": _pt(center),
                            "major_radius_cm": round(major, 4),
                            "minor_radius_cm": round(minor, 4),
                            "major_diameter_mm": round(major * 2 * 10, 2),
                            "minor_diameter_mm": round(minor * 2 * 10, 2)
                        })
                    except:
                        pass

            bodies.append({
                "name": body.name,
                "index": global_index,
                "component": comp.name,
                "is_solid": body.isSolid,
                "volume_cm3": round(body.volume, 4) if body.volume else None,
                "area_cm2": round(body.area, 4) if body.area else None,
                "face_count": body.faces.count,
                "edge_count": body.edges.count,
                "vertex_count": body.vertices.count,
                "face_types": face_types,
                "bounding_box": {
                    "min": _pt(bbox.minPoint),
                    "max": _pt(bbox.maxPoint),
                    "size": [
                        round(bbox.maxPoint.x - bbox.minPoint.x, 4),
                        round(bbox.maxPoint.y - bbox.minPoint.y, 4),
                        round(bbox.maxPoint.z - bbox.minPoint.z, 4)
                    ]
                },
                "circular_edges": circular_edges
            })
            global_index += 1

    _write_json(os.path.join(session_dir, "bodies.json"), {
        "bodies": bodies,
        "count": len(bodies)
    })
    return len(bodies)


def _export_sketches(root, all_components, session_dir):
    """Export sketch overview and individual sketch geometry files."""
    sketches_dir = os.path.join(session_dir, "sketches")
    os.makedirs(sketches_dir, exist_ok=True)

    # Collect all sketches with global indexing
    all_sketches = []
    global_index = 0
    for comp in all_components:
        for i in range(comp.sketches.count):
            sketch = comp.sketches.item(i)
            all_sketches.append((sketch, global_index, comp))
            global_index += 1

    # Export overview
    overview = []
    for sketch, idx, comp in all_sketches:
        curves = sketch.sketchCurves
        overview.append({
            "name": sketch.name,
            "index": idx,
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

    _write_json(os.path.join(sketches_dir, "overview.json"), {
        "sketches": overview,
        "count": len(overview)
    })

    # Export individual sketch geometry
    for sketch, idx, comp in all_sketches:
        curves = sketch.sketchCurves

        # Extract circles
        circles = []
        for i in range(curves.sketchCircles.count):
            circle = curves.sketchCircles.item(i)
            circles.append({
                "index": i,
                "center": _pt(circle.centerSketchPoint.geometry),
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
                "start": _pt(line.startSketchPoint.geometry),
                "end": _pt(line.endSketchPoint.geometry),
                "length": round(line.length, 4),
                "is_construction": line.isConstruction
            })

        # Extract arcs
        arcs = []
        for i in range(curves.sketchArcs.count):
            arc = curves.sketchArcs.item(i)
            arc_data = {
                "index": i,
                "center": _pt(arc.centerSketchPoint.geometry),
                "radius": round(arc.radius, 4),
                "start_point": _pt(arc.startSketchPoint.geometry),
                "end_point": _pt(arc.endSketchPoint.geometry),
                "is_construction": arc.isConstruction
            }
            # Try to get angles from geometry object
            try:
                geom = arc.geometry
                arc_data["start_angle_deg"] = round(math.degrees(geom.startAngle), 2)
                arc_data["end_angle_deg"] = round(math.degrees(geom.endAngle), 2)
            except:
                pass
            arcs.append(arc_data)

        # Extract ellipses
        ellipses = []
        for i in range(curves.sketchEllipses.count):
            ellipse = curves.sketchEllipses.item(i)
            ellipses.append({
                "index": i,
                "center": _pt(ellipse.centerSketchPoint.geometry),
                "major_radius": round(ellipse.majorRadius, 4),
                "minor_radius": round(ellipse.minorRadius, 4),
                "is_construction": ellipse.isConstruction
            })

        # Get sketch plane info
        plane_info = {}
        try:
            plane = sketch.referencePlane
            if plane:
                plane_info = {"name": plane.name if hasattr(plane, 'name') else "Custom"}
        except:
            plane_info = {"name": "Unknown"}

        sketch_data = {
            "sketch_name": sketch.name,
            "sketch_index": idx,
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
        }

        _write_json(os.path.join(sketches_dir, f"sketch_{idx}.json"), sketch_data)

    return len(all_sketches)


def _export_features(root, all_components, session_dir):
    """Export feature timeline information."""
    features = []
    global_index = 0

    for comp in all_components:
        for i in range(comp.features.count):
            feat = comp.features.item(i)
            features.append({
                "name": feat.name,
                "index": global_index,
                "component": comp.name,
                "type": feat.objectType.split("::")[-1].replace("Feature", ""),
                "is_suppressed": feat.isSuppressed,
                "is_valid": feat.isValid
            })
            global_index += 1

    _write_json(os.path.join(session_dir, "features.json"), {
        "features": features,
        "count": len(features)
    })
    return len(features)


def _export_parameters(design, session_dir):
    """Export all parameters (user and model)."""
    user_params = []
    for i in range(design.userParameters.count):
        param = design.userParameters.item(i)
        user_params.append({
            "name": param.name,
            "expression": param.expression,
            "value": round(param.value, 6),
            "unit": param.unit,
            "comment": param.comment
        })

    model_params = []
    for i in range(design.allParameters.count):
        param = design.allParameters.item(i)
        if param.objectType == "adsk::fusion::UserParameter":
            continue

        role = ""
        try:
            if hasattr(param, 'role'):
                role = param.role
        except:
            pass

        created_by = ""
        try:
            if hasattr(param, 'createdBy') and param.createdBy:
                created_by = param.createdBy.name
        except:
            pass

        model_params.append({
            "name": param.name,
            "expression": param.expression,
            "value": round(param.value, 6),
            "unit": param.unit,
            "role": role,
            "created_by": created_by
        })

    _write_json(os.path.join(session_dir, "parameters.json"), {
        "user_parameters": user_params,
        "model_parameters": model_params,
        "counts": {
            "user": len(user_params),
            "model": len(model_params),
            "total": len(user_params) + len(model_params)
        }
    })
    return len(user_params) + len(model_params)


def _export_construction_planes(root, session_dir):
    """Export construction plane information."""
    planes = root.constructionPlanes
    plane_list = []

    for i in range(planes.count):
        plane = planes.item(i)
        plane_list.append({
            "index": i,
            "name": plane.name,
            "is_visible": plane.isVisible
        })

    _write_json(os.path.join(session_dir, "construction_planes.json"), {
        "planes": plane_list,
        "count": planes.count
    })
    return planes.count


def export_session(command_id, params, ctx):
    """
    Export complete design data to a timestamped session folder.

    Creates a folder with all design information as separate JSON files,
    enabling AI to read files directly without multiple commands.

    Params:
        name (str, optional): Custom session name (default: timestamp)

    Returns:
        session_path: Path to the created session folder
        files: List of exported files
        summary: Counts of exported entities
    """
    root = ctx.root
    design = ctx.design

    # Create session folder
    sessions_dir = os.path.join(BASE_DIR, "sessions")
    os.makedirs(sessions_dir, exist_ok=True)

    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    custom_name = params.get("name", "")
    if custom_name:
        folder_name = f"{timestamp}_{custom_name}"
    else:
        folder_name = timestamp

    session_dir = os.path.join(sessions_dir, folder_name)
    os.makedirs(session_dir, exist_ok=True)

    try:
        # Collect all components
        all_components = _collect_all_components(root)

        # Export all data
        design_summary = _export_design_info(design, root, all_components, session_dir)
        body_count = _export_bodies(root, all_components, session_dir)
        sketch_count = _export_sketches(root, all_components, session_dir)
        feature_count = _export_features(root, all_components, session_dir)
        param_count = _export_parameters(design, session_dir)
        plane_count = _export_construction_planes(root, session_dir)

        # Create manifest
        manifest = {
            "session_name": folder_name,
            "design_name": design.rootComponent.name,
            "exported_at": datetime.now().isoformat(),
            "files": [
                "design_info.json",
                "bodies.json",
                "sketches/overview.json",
                *[f"sketches/sketch_{i}.json" for i in range(sketch_count)],
                "features.json",
                "parameters.json",
                "construction_planes.json"
            ],
            "summary": {
                "components": design_summary["component_count"],
                "bodies": body_count,
                "sketches": sketch_count,
                "features": feature_count,
                "parameters": param_count,
                "construction_planes": plane_count
            }
        }
        _write_json(os.path.join(session_dir, "manifest.json"), manifest)

        write_result(command_id, True, {
            "session_path": session_dir,
            "session_name": folder_name,
            "files": manifest["files"],
            "summary": manifest["summary"]
        })

    except Exception as e:
        write_result(command_id, False, None, f"Failed to export session: {str(e)}")


COMMANDS = {
    "export_session": export_session,
}
