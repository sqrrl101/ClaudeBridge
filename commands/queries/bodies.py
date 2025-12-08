"""
Body-related query commands.
"""

from ...utils import write_result


def _collect_all_components(root):
    """Recursively collect all components in the design hierarchy."""
    components = [root]

    def traverse_occurrences(occurrences):
        for i in range(occurrences.count):
            occ = occurrences.item(i)
            comp = occ.component
            components.append(comp)
            # Recursively traverse nested occurrences
            if comp.occurrences.count > 0:
                traverse_occurrences(comp.occurrences)

    traverse_occurrences(root.occurrences)
    return components


def _get_body_info(body, index, component_name=None):
    """Extract detailed information from a body."""
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

    info = {
        "name": body.name,
        "index": index,
        "is_solid": body.isSolid,
        "volume_cm3": round(body.volume, 4) if body.volume else None,
        "area_cm2": round(body.area, 4) if body.area else None,
        "face_count": body.faces.count,
        "edge_count": body.edges.count,
        "vertex_count": body.vertices.count,
        "face_types": face_types,
        "bounding_box": {
            "min": [round(bbox.minPoint.x, 4), round(bbox.minPoint.y, 4), round(bbox.minPoint.z, 4)],
            "max": [round(bbox.maxPoint.x, 4), round(bbox.maxPoint.y, 4), round(bbox.maxPoint.z, 4)],
            "size": [
                round(bbox.maxPoint.x - bbox.minPoint.x, 4),
                round(bbox.maxPoint.y - bbox.minPoint.y, 4),
                round(bbox.maxPoint.z - bbox.minPoint.z, 4)
            ]
        }
    }
    if component_name:
        info["component"] = component_name
    return info


def get_bodies_detailed(command_id, params, ctx):
    """Get comprehensive body information including geometry details.

    Traverses all components in the design hierarchy to find all bodies.
    """
    root = ctx.root

    # Collect all components recursively
    all_components = _collect_all_components(root)

    bodies = []
    global_index = 0

    for comp in all_components:
        for i in range(comp.bRepBodies.count):
            body = comp.bRepBodies.item(i)
            body_info = _get_body_info(body, global_index, comp.name)
            bodies.append(body_info)
            global_index += 1

    write_result(command_id, True, {"bodies": bodies, "count": len(bodies)})


def get_circular_edges(command_id, params, ctx):
    """Get all circular edges with their diameters.

    Useful for measuring openings, holes, and cylindrical features.

    Params:
        body_index (int, optional): Specific body to query (default: all bodies)
    """
    import math

    root = ctx.root
    body_index = params.get("body_index")

    # Collect all components recursively
    all_components = _collect_all_components(root)

    # Gather all bodies
    all_bodies = []
    for comp in all_components:
        for i in range(comp.bRepBodies.count):
            all_bodies.append((comp.bRepBodies.item(i), comp.name))

    if body_index is not None:
        if body_index >= len(all_bodies):
            write_result(command_id, False, None, f"Body index {body_index} out of range (max {len(all_bodies)-1})")
            return
        all_bodies = [all_bodies[body_index]]

    results = []

    for body, comp_name in all_bodies:
        body_edges = []
        for i, edge in enumerate(body.edges):
            geom = edge.geometry
            curve_type = geom.curveType

            # curveType 2 = Circle3D
            if curve_type == 2:  # Circle
                try:
                    center = geom.center
                    radius_cm = geom.radius
                    diameter_mm = radius_cm * 2 * 10  # Convert to mm

                    body_edges.append({
                        "edge_index": i,
                        "type": "circle",
                        "center": [round(center.x, 4), round(center.y, 4), round(center.z, 4)],
                        "radius_cm": round(radius_cm, 4),
                        "diameter_mm": round(diameter_mm, 2),
                        "circumference_mm": round(2 * math.pi * radius_cm * 10, 2)
                    })
                except:
                    pass
            # curveType 5 = Ellipse3D
            elif curve_type == 5:  # Ellipse
                try:
                    center = geom.center
                    major = geom.majorRadius
                    minor = geom.minorRadius
                    body_edges.append({
                        "edge_index": i,
                        "type": "ellipse",
                        "center": [round(center.x, 4), round(center.y, 4), round(center.z, 4)],
                        "major_radius_cm": round(major, 4),
                        "minor_radius_cm": round(minor, 4),
                        "major_diameter_mm": round(major * 2 * 10, 2),
                        "minor_diameter_mm": round(minor * 2 * 10, 2)
                    })
                except:
                    pass

        if body_edges:
            results.append({
                "body": body.name,
                "component": comp_name,
                "circular_edges": body_edges
            })

    write_result(command_id, True, {
        "bodies": results,
        "total_circular_edges": sum(len(b["circular_edges"]) for b in results)
    })


COMMANDS = {
    "get_bodies_detailed": get_bodies_detailed,
    "get_circular_edges": get_circular_edges,
}
