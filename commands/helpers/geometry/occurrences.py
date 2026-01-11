"""
Occurrence and joint geometry helpers for assembly operations.
"""

import adsk.core
import adsk.fusion


def get_occurrence_by_index(root, index):
    """
    Get an occurrence by its index in allOccurrences.

    Args:
        root: Root component
        index: Index of occurrence (0-based)

    Returns:
        tuple: (occurrence, error_message)
    """
    if root is None:
        return None, "No root component"

    all_occs = root.allOccurrences
    if all_occs is None or all_occs.count == 0:
        return None, "No occurrences in design"

    if index < 0 or index >= all_occs.count:
        return None, f"Invalid occurrence index {index}. Has {all_occs.count} occurrences (0-{all_occs.count - 1})"

    return all_occs.item(index), None


def get_occurrence_by_name(root, name):
    """
    Get an occurrence by its name.

    Args:
        root: Root component
        name: Name of occurrence to find

    Returns:
        tuple: (occurrence, error_message)
    """
    if root is None:
        return None, "No root component"

    all_occs = root.allOccurrences
    if all_occs is None or all_occs.count == 0:
        return None, "No occurrences in design"

    for occ in all_occs:
        if occ.name == name or occ.component.name == name:
            return occ, None

    return None, f"No occurrence found with name '{name}'"


def get_joint_direction(direction_str):
    """
    Convert direction string to JointDirections enum.

    Args:
        direction_str: "x", "y", or "z" (case insensitive)

    Returns:
        tuple: (JointDirections enum value, error_message)
    """
    if direction_str is None:
        direction_str = "z"

    directions = {
        "x": adsk.fusion.JointDirections.XAxisJointDirection,
        "y": adsk.fusion.JointDirections.YAxisJointDirection,
        "z": adsk.fusion.JointDirections.ZAxisJointDirection,
    }

    key = direction_str.lower()
    if key not in directions:
        return None, f"Invalid joint direction '{direction_str}'. Use 'x', 'y', or 'z'"

    return directions[key], None


def get_key_point_type(key_point_str):
    """
    Convert key point string to JointKeyPointTypes enum.

    Args:
        key_point_str: "center", "start", "end", or "middle" (case insensitive)

    Returns:
        tuple: (JointKeyPointTypes enum value, error_message)
    """
    if key_point_str is None:
        key_point_str = "center"

    key_points = {
        "center": adsk.fusion.JointKeyPointTypes.CenterKeyPoint,
        "start": adsk.fusion.JointKeyPointTypes.StartKeyPoint,
        "end": adsk.fusion.JointKeyPointTypes.EndKeyPoint,
        "middle": adsk.fusion.JointKeyPointTypes.MiddleKeyPoint,
    }

    key = key_point_str.lower()
    if key not in key_points:
        return None, f"Invalid key point '{key_point_str}'. Use 'center', 'start', 'end', or 'middle'"

    return key_points[key], None


def get_joint_type_setter(joint_type_str):
    """
    Get the method name for setting joint motion type.

    Args:
        joint_type_str: "revolute", "slider", "rigid", "ball", "cylindrical", "planar", "pin_slot"

    Returns:
        tuple: (method_name, error_message)
    """
    if joint_type_str is None:
        joint_type_str = "rigid"

    joint_types = {
        "revolute": "setAsRevoluteJointMotion",
        "slider": "setAsSliderJointMotion",
        "rigid": "setAsRigidJointMotion",
        "ball": "setAsBallJointMotion",
        "cylindrical": "setAsCylindricalJointMotion",
        "planar": "setAsPlanarJointMotion",
        "pin_slot": "setAsPinSlotJointMotion",
    }

    key = joint_type_str.lower().replace("-", "_").replace(" ", "_")
    if key not in joint_types:
        valid = ", ".join(joint_types.keys())
        return None, f"Invalid joint type '{joint_type_str}'. Use one of: {valid}"

    return joint_types[key], None


def create_transform_matrix(x=0, y=0, z=0, rx=0, ry=0, rz=0):
    """
    Create a Matrix3D transform with translation and rotation.

    Args:
        x, y, z: Translation in cm
        rx, ry, rz: Rotation angles in degrees (applied in order: X, Y, Z)

    Returns:
        Matrix3D transform
    """
    import math

    transform = adsk.core.Matrix3D.create()

    # Apply translation
    if x != 0 or y != 0 or z != 0:
        transform.translation = adsk.core.Vector3D.create(x, y, z)

    # Apply rotations (convert degrees to radians)
    if rx != 0:
        rotation = adsk.core.Matrix3D.create()
        rotation.setToRotation(math.radians(rx),
                               adsk.core.Vector3D.create(1, 0, 0),
                               adsk.core.Point3D.create(0, 0, 0))
        transform.transformBy(rotation)

    if ry != 0:
        rotation = adsk.core.Matrix3D.create()
        rotation.setToRotation(math.radians(ry),
                               adsk.core.Vector3D.create(0, 1, 0),
                               adsk.core.Point3D.create(0, 0, 0))
        transform.transformBy(rotation)

    if rz != 0:
        rotation = adsk.core.Matrix3D.create()
        rotation.setToRotation(math.radians(rz),
                               adsk.core.Vector3D.create(0, 0, 1),
                               adsk.core.Point3D.create(0, 0, 0))
        transform.transformBy(rotation)

    return transform


def get_face_from_occurrence(occurrence, body_index=0, face_index=0):
    """
    Get a face from an occurrence's body.

    Args:
        occurrence: The occurrence to get face from
        body_index: Index of body in occurrence's component
        face_index: Index of face on the body

    Returns:
        tuple: (face_proxy, error_message)
    """
    comp = occurrence.component
    if comp is None:
        return None, "Occurrence has no component"

    bodies = comp.bRepBodies
    if bodies is None or bodies.count == 0:
        return None, f"Component '{comp.name}' has no bodies"

    if body_index < 0 or body_index >= bodies.count:
        return None, f"Invalid body index {body_index}. Component has {bodies.count} bodies"

    body = bodies.item(body_index)
    faces = body.faces

    if faces is None or faces.count == 0:
        return None, f"Body has no faces"

    if face_index < 0 or face_index >= faces.count:
        return None, f"Invalid face index {face_index}. Body has {faces.count} faces"

    face = faces.item(face_index)

    # Create proxy for assembly context
    face_proxy = face.createForAssemblyContext(occurrence)
    return face_proxy, None


def get_edge_from_occurrence(occurrence, body_index=0, edge_index=0):
    """
    Get an edge from an occurrence's body.

    Args:
        occurrence: The occurrence to get edge from
        body_index: Index of body in occurrence's component
        edge_index: Index of edge on the body

    Returns:
        tuple: (edge_proxy, error_message)
    """
    comp = occurrence.component
    if comp is None:
        return None, "Occurrence has no component"

    bodies = comp.bRepBodies
    if bodies is None or bodies.count == 0:
        return None, f"Component '{comp.name}' has no bodies"

    if body_index < 0 or body_index >= bodies.count:
        return None, f"Invalid body index {body_index}. Component has {bodies.count} bodies"

    body = bodies.item(body_index)
    edges = body.edges

    if edges is None or edges.count == 0:
        return None, f"Body has no edges"

    if edge_index < 0 or edge_index >= edges.count:
        return None, f"Invalid edge index {edge_index}. Body has {edges.count} edges"

    edge = edges.item(edge_index)

    # Create proxy for assembly context
    edge_proxy = edge.createForAssemblyContext(occurrence)
    return edge_proxy, None


def create_joint_geometry_from_spec(occurrence, spec):
    """
    Create JointGeometry from a specification dictionary.

    Args:
        occurrence: The occurrence containing the geometry
        spec: Dictionary with geometry specification:
            - type: "face", "edge", or "point"
            - body_index: Index of body (default 0)
            - face_index: Index of face (for type="face")
            - edge_index: Index of edge (for type="edge")
            - key_point: "center", "start", "end", "middle" (optional)

    Returns:
        tuple: (JointGeometry, error_message)
    """
    if spec is None:
        return None, "No geometry specification provided"

    geo_type = spec.get("type", "face").lower()
    body_index = spec.get("body_index", 0)
    key_point_str = spec.get("key_point", "center")

    key_point_type, error = get_key_point_type(key_point_str)
    if error:
        return None, error

    if geo_type == "face":
        face_index = spec.get("face_index", 0)
        face, error = get_face_from_occurrence(occurrence, body_index, face_index)
        if error:
            return None, error

        # Determine face type and create appropriate geometry
        try:
            geometry = face.geometry
            if hasattr(geometry, 'surfaceType'):
                surface_type = geometry.surfaceType
                if surface_type == adsk.core.SurfaceTypes.PlaneSurfaceType:
                    return adsk.fusion.JointGeometry.createByPlanarFace(face, None, key_point_type), None
                elif surface_type == adsk.core.SurfaceTypes.CylinderSurfaceType:
                    return adsk.fusion.JointGeometry.createByCylindricalFace(face, key_point_type), None
                elif surface_type == adsk.core.SurfaceTypes.SphereSurfaceType:
                    return adsk.fusion.JointGeometry.createBySphereFace(face), None
                elif surface_type == adsk.core.SurfaceTypes.ConeSurfaceType:
                    return adsk.fusion.JointGeometry.createByCylindricalFace(face, key_point_type), None
            # Default to planar
            return adsk.fusion.JointGeometry.createByPlanarFace(face, None, key_point_type), None
        except:
            # Fallback to non-planar face method
            return adsk.fusion.JointGeometry.createByNonPlanarFace(face, key_point_type), None

    elif geo_type == "edge":
        edge_index = spec.get("edge_index", 0)
        edge, error = get_edge_from_occurrence(occurrence, body_index, edge_index)
        if error:
            return None, error

        return adsk.fusion.JointGeometry.createByCurve(edge, key_point_type), None

    elif geo_type == "point":
        # For point type, use a vertex or construction point
        return None, "Point geometry type not yet implemented. Use 'face' or 'edge'"

    else:
        return None, f"Invalid geometry type '{geo_type}'. Use 'face', 'edge', or 'point'"
