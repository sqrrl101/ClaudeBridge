"""
Parameter information collector for session export.
"""

import os
from ..utils import write_json


def export_parameters(design, session_dir):
    """
    Export all parameters (user and model).

    Collects both user-defined parameters and model-generated parameters
    including their expressions, values, units, and metadata.

    Args:
        design: Fusion 360 Design object
        session_dir: Directory to write output files

    Returns:
        int: Total number of parameters exported
    """
    user_params = []
    for i in range(design.userParameters.count):
        param = design.userParameters.item(i)
        try:
            value = round(param.value, 6)
        except:
            # Non-numeric parameter (text, boolean, etc.)
            value = None
        user_params.append({
            "name": param.name,
            "expression": param.expression,
            "value": value,
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

        try:
            value = round(param.value, 6)
        except:
            # Non-numeric parameter (text, boolean, etc.)
            value = None
        model_params.append({
            "name": param.name,
            "expression": param.expression,
            "value": value,
            "unit": param.unit,
            "role": role,
            "created_by": created_by
        })

    write_json(os.path.join(session_dir, "parameters.json"), {
        "user_parameters": user_params,
        "model_parameters": model_params,
        "counts": {
            "user": len(user_params),
            "model": len(model_params),
            "total": len(user_params) + len(model_params)
        }
    })
    return len(user_params) + len(model_params)
