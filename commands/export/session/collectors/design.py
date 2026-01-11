"""
Design information collector for session export.
"""

import os
from ..utils import write_json


def export_design_info(design, root, all_components, session_dir):
    """
    Export design overview information.

    Collects summary information about bodies, sketches, features, components,
    and parameters in the design.

    Args:
        design: Fusion 360 Design object
        root: Root component
        all_components: List of all components in the design
        session_dir: Directory to write output files

    Returns:
        dict: Summary counts of exported entities
    """
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
        try:
            value_str = f"{param.expression} ({param.value} {param.unit})"
        except:
            # Non-numeric parameter (text, boolean, etc.)
            value_str = param.expression
        params_list.append({
            "name": param.name,
            "value": value_str
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

    write_json(os.path.join(session_dir, "design_info.json"), data)
    return data["summary"]
