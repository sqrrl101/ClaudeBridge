"""
Body information collector for session export.
"""

import os
import math
from ..utils import write_json, pt


def export_bodies(root, all_components, session_dir):
    """
    Export detailed body information including circular edges.

    Collects comprehensive information about all bodies in the design,
    including geometry, bounding boxes, face types, and circular/elliptical edges.

    Args:
        root: Root component
        all_components: List of all components in the design
        session_dir: Directory to write output files

    Returns:
        int: Number of bodies exported
    """
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
                if geom is None:
                    continue
                curve_type = geom.curveType

                if curve_type == 2:  # Circle
                    try:
                        center = geom.center
                        radius_cm = geom.radius
                        diameter_mm = radius_cm * 2 * 10
                        circular_edges.append({
                            "edge_index": edge_idx,
                            "type": "circle",
                            "center": pt(center),
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
                            "center": pt(center),
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
                    "min": pt(bbox.minPoint),
                    "max": pt(bbox.maxPoint),
                    "size": [
                        round(bbox.maxPoint.x - bbox.minPoint.x, 4),
                        round(bbox.maxPoint.y - bbox.minPoint.y, 4),
                        round(bbox.maxPoint.z - bbox.minPoint.z, 4)
                    ]
                },
                "circular_edges": circular_edges
            })
            global_index += 1

    write_json(os.path.join(session_dir, "bodies.json"), {
        "bodies": bodies,
        "count": len(bodies)
    })
    return len(bodies)
