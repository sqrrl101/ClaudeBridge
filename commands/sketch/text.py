"""
Sketch text commands: draw_text, emboss_text.

These commands allow adding text to sketches and embossing/debossing text on body faces.
"""

import math

import adsk.core
import adsk.fusion

from ...utils import write_result
from ..helpers import get_sketch_by_index, get_body_by_global_index, get_operation_type


def draw_text(command_id, params, ctx):
    """
    Draw text on a sketch.

    Params:
        sketch_index: Index of sketch (default: last sketch)
        text: The text string to draw (required)
        x: X position of text anchor point (default: 0)
        y: Y position of text anchor point (default: 0)
        height: Text height in cm (default: 1.0)
        angle: Rotation angle in degrees (default: 0)
        font_name: Font name (default: "Arial")

    Returns:
        message: Success message
        text_index: Index of the created text
    """
    sketches = ctx.sketches

    idx = params.get("sketch_index", sketches.count - 1)
    text = params.get("text", "")
    x = params.get("x", 0)
    y = params.get("y", 0)
    height = params.get("height", 1.0)
    angle = params.get("angle", 0)
    font_name = params.get("font_name", "Arial")

    if not text:
        return write_result(command_id, False, None, "Text parameter is required")

    sketch, error = get_sketch_by_index(sketches, idx)
    if error:
        return write_result(command_id, False, None, error)

    try:
        # Create text input
        texts = sketch.sketchTexts
        text_input = texts.createInput2(text, height)

        # Set font if specified
        text_input.fontName = font_name

        # Set position and angle
        anchor_point = adsk.core.Point3D.create(x, y, 0)
        angle_rad = math.radians(angle)

        # Define diagonal point for text bounds
        diagonal_point = adsk.core.Point3D.create(x + height * len(text), y + height * 1.5, 0)

        # Use multiline text with integer alignment values
        # HorizontalAlignments: 0=Left, 1=Center, 2=Right
        # VerticalAlignments: 0=Top, 1=Middle, 2=Bottom
        text_input.setAsMultiLine(
            anchor_point,
            diagonal_point,
            0,  # Left align
            2,  # Bottom align
            0   # Character spacing
        )

        # Add the text
        sketch_text = texts.add(text_input)

        # Apply rotation if specified
        if angle != 0:
            # Get transform for rotation around anchor point
            transform = adsk.core.Matrix3D.create()
            transform.setToRotation(angle_rad, adsk.core.Vector3D.create(0, 0, 1), anchor_point)

            # Move text entities
            entities = adsk.core.ObjectCollection.create()
            for curve in sketch_text.explodedCurves:
                entities.add(curve)
            if entities.count > 0:
                sketch.move(entities, transform)

        write_result(command_id, True, {
            "message": f"Text '{text}' added at ({x},{y}) height={height}cm",
            "text_index": texts.count - 1
        })

    except Exception as e:
        write_result(command_id, False, None, f"Failed to draw text: {str(e)}")


def emboss_text(command_id, params, ctx):
    """
    Emboss or deboss text on a body face.

    This is a convenience command that:
    1. Creates a sketch on the specified face
    2. Adds text to the sketch
    3. Extrudes the text (cut for deboss, join for emboss)

    Params:
        body_index: Index of the body (default: 0)
        face_index: Index of the face on that body (default: 0)
        use_top_face: If true, automatically find the topmost face (default: false)
        text: The text string to emboss (required)
        x: X position relative to face center (default: 0)
        y: Y position relative to face center (default: 0)
        height: Text height in cm (default: 1.0)
        depth: Extrusion depth in cm (default: 0.1)
        emboss: True for raised text (emboss), False for cut text (deboss) (default: False/deboss)
        font_name: Font name (default: "Arial")

    Returns:
        message: Success message
        sketch_index: Index of the created sketch
    """
    root = ctx.root
    sketches = ctx.sketches

    body_index = params.get("body_index", 0)
    face_index = params.get("face_index", 0)
    use_top_face = params.get("use_top_face", False)
    text = params.get("text", "")
    x = params.get("x", 0)
    y = params.get("y", 0)
    height = params.get("height", 1.0)
    depth = params.get("depth", 0.1)
    emboss = params.get("emboss", False)
    font_name = params.get("font_name", "Arial")

    if not text:
        return write_result(command_id, False, None, "Text parameter is required")

    # Get the body using global index (searches all components)
    body, component, error = get_body_by_global_index(root, body_index)
    if error:
        return write_result(command_id, False, None, error)

    # Use the component's sketches collection
    sketches = component.sketches

    try:
        # Find the face
        if use_top_face:
            from ..helpers import find_top_face
            face = find_top_face(body)
            if face is None:
                return write_result(command_id, False, None,
                    f"No planar faces found on body {body_index}")
        else:
            if face_index >= body.faces.count:
                return write_result(command_id, False, None,
                    f"Invalid face_index {face_index}. Body has {body.faces.count} faces.")
            face = body.faces.item(face_index)

        # Create sketch on the face
        sketch = sketches.add(face)
        sketch_index = sketches.count - 1

        # Create text input
        texts = sketch.sketchTexts
        text_input = texts.createInput2(text, height)
        text_input.fontName = font_name

        # Position text - coordinates are relative to sketch origin (face center typically)
        anchor_point = adsk.core.Point3D.create(x, y, 0)
        diagonal_point = adsk.core.Point3D.create(x + height * len(text), y + height * 1.5, 0)

        # Use multiline text with integer alignment values
        # HorizontalAlignments: 0=Left, 1=Center, 2=Right
        # VerticalAlignments: 0=Top, 1=Middle, 2=Bottom
        text_input.setAsMultiLine(
            anchor_point,
            diagonal_point,
            0,  # Left align
            2,  # Bottom align
            0   # Character spacing
        )

        # Add the text to sketch
        sketch_text = texts.add(text_input)

        # The text creates profiles that we can extrude
        # We need to find the profiles created by the text
        if sketch.profiles.count == 0:
            return write_result(command_id, False, None,
                "No profiles created from text. Text may be too small or invalid.")

        # Collect all profiles for extrusion
        profiles = adsk.core.ObjectCollection.create()
        for i in range(sketch.profiles.count):
            profiles.add(sketch.profiles.item(i))

        # Determine operation type
        if emboss:
            operation = adsk.fusion.FeatureOperations.JoinFeatureOperation
            extrude_depth = depth
        else:
            operation = adsk.fusion.FeatureOperations.CutFeatureOperation
            extrude_depth = -depth  # Negative for cutting into the face

        # Create extrusion using the component's features
        extrudes = component.features.extrudeFeatures
        ext_input = extrudes.createInput(profiles, operation)

        # Set distance
        distance = adsk.core.ValueInput.createByReal(extrude_depth)
        ext_input.setDistanceExtent(False, distance)

        extrudes.add(ext_input)

        action = "embossed" if emboss else "debossed"
        write_result(command_id, True, {
            "message": f"Text '{text}' {action} on body {body_index}, depth={depth}cm",
            "sketch_index": sketch_index
        })

    except Exception as e:
        write_result(command_id, False, None, f"Failed to emboss text: {str(e)}")


COMMANDS = {
    "draw_text": draw_text,
    "emboss_text": emboss_text,
}
