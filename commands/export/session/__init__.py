"""
Session export command - exports complete design data to a timestamped folder.

This consolidates all query functionality into a single export that creates
JSON files for each data type, enabling AI to read files directly without
multiple round-trip commands.
"""

import os
from datetime import datetime

from ....config import BASE_DIR
from ....utils import write_result
from ...helpers import collect_all_components
from .utils import write_json
from .collectors import (
    export_design_info,
    export_bodies,
    export_sketches,
    export_features,
    export_parameters,
    export_construction_planes,
    export_joints,
)


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
        all_components = collect_all_components(root)

        # Export all data
        design_summary = export_design_info(design, root, all_components, session_dir)
        body_count = export_bodies(root, all_components, session_dir)
        sketch_count = export_sketches(root, all_components, session_dir)
        feature_count = export_features(root, all_components, session_dir)
        param_count = export_parameters(design, session_dir)
        plane_count = export_construction_planes(root, session_dir)
        joint_count = export_joints(root, session_dir)

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
                "construction_planes.json",
                "joints.json"
            ],
            "summary": {
                "components": design_summary["component_count"],
                "bodies": body_count,
                "sketches": sketch_count,
                "features": feature_count,
                "parameters": param_count,
                "construction_planes": plane_count,
                "joints": joint_count
            }
        }
        write_json(os.path.join(session_dir, "manifest.json"), manifest)

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
