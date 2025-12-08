"""
Sketch creation commands.
"""

from ...utils import write_result
from ..helpers import get_construction_plane, get_body_by_index


def create_sketch(command_id, params, ctx):
    """
    Create a new sketch on a construction plane or offset plane.

    Params:
        plane: Base plane ("xy", "xz", "yz") - used if plane_index not provided
        plane_index: Index of a construction plane (from create_offset_plane)

    Returns:
        sketch_name: Name of created sketch
        sketch_index: Index of created sketch
    """
    root = ctx.root
    sketches = ctx.sketches

    plane_index = params.get("plane_index", None)
    plane_name = params.get("plane", "xy")

    try:
        if plane_index is not None:
            # Use a construction plane by index (e.g., from create_offset_plane)
            planes = root.constructionPlanes
            if plane_index >= planes.count:
                return write_result(command_id, False, None,
                    f"Invalid plane_index {plane_index}. Design has {planes.count} construction planes.")
            plane = planes.item(plane_index)
        else:
            # Use a base construction plane (xy, xz, yz)
            plane, error = get_construction_plane(root, plane_name)
            if error:
                return write_result(command_id, False, None, error)

        sketch = sketches.add(plane)
        write_result(command_id, True, {
            "sketch_name": sketch.name,
            "sketch_index": sketches.count - 1
        })

    except Exception as e:
        write_result(command_id, False, None, f"Failed to create sketch: {str(e)}")


def create_sketch_on_face(command_id, params, ctx):
    """
    Create a new sketch on an existing body face.

    Params:
        body_index: Index of the body (default 0)
        face_index: Index of the face on that body (default 0)
        use_top_face: If true, automatically find the topmost face (ignores face_index)

    Returns:
        sketch_name: Name of created sketch
        sketch_index: Index of created sketch
        face_info: Information about the face used
    """
    root = ctx.root
    sketches = ctx.sketches

    body_index = params.get("body_index", 0)
    face_index = params.get("face_index", 0)
    use_top_face = params.get("use_top_face", False)

    # Get the body
    body, error = get_body_by_index(root, body_index)
    if error:
        return write_result(command_id, False, None, error)

    try:
        if use_top_face:
            # Find the topmost planar face
            from ..helpers import find_top_face
            face = find_top_face(body)
            if face is None:
                return write_result(command_id, False, None,
                    f"No planar faces found on body {body_index}")
        else:
            # Get face by index
            if face_index >= body.faces.count:
                return write_result(command_id, False, None,
                    f"Invalid face_index {face_index}. Body has {body.faces.count} faces.")
            face = body.faces.item(face_index)

        # Create sketch on the face
        sketch = sketches.add(face)

        # Get face info for response
        bbox = face.boundingBox
        face_info = {
            "face_index": face_index if not use_top_face else "top",
            "center_z": (bbox.minPoint.z + bbox.maxPoint.z) / 2
        }

        write_result(command_id, True, {
            "sketch_name": sketch.name,
            "sketch_index": sketches.count - 1,
            "body_index": body_index,
            "face_info": face_info
        })

    except Exception as e:
        write_result(command_id, False, None, f"Failed to create sketch on face: {str(e)}")


COMMANDS = {
    "create_sketch": create_sketch,
    "create_sketch_on_face": create_sketch_on_face,
}
