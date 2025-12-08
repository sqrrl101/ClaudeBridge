"""
Parameter management commands.
"""

import adsk.core

from ..utils import write_result


def set_parameter(command_id, params, ctx):
    """Create or update a user parameter.

    Params:
        name (str): Parameter name
        value (float, optional): Numeric value (use with unit)
        unit (str, optional): Unit for the value (default: "cm")
        expression (str, optional): Formula expression (e.g., "ball_diameter + clearance")

    Use either (value + unit) OR expression, not both.
    Expression allows parameters to auto-calculate from other parameters.
    """
    design = ctx.design

    name = params.get("name")
    value = params.get("value")
    unit = params.get("unit", "cm")
    expression = params.get("expression")

    if not name:
        return write_result(command_id, False, None, "Name required")

    if expression is None and value is None:
        return write_result(command_id, False, None, "Either value or expression required")

    # Determine the expression string to use
    if expression is not None:
        expr_string = expression
    else:
        expr_string = f"{value} {unit}"

    existing = design.userParameters.itemByName(name)
    if existing:
        try:
            existing.expression = expr_string
            # Get the calculated value
            calc_value = existing.value
            calc_unit = existing.unit
            write_result(command_id, True, {
                "message": f"Updated {name} = {expr_string}",
                "expression": expr_string,
                "calculated_value": calc_value,
                "unit": calc_unit
            })
        except Exception as e:
            write_result(command_id, False, None, f"Invalid expression '{expr_string}': {str(e)}")
    else:
        try:
            new_param = design.userParameters.add(
                name,
                adsk.core.ValueInput.createByString(expr_string),
                unit,
                ""
            )
            write_result(command_id, True, {
                "message": f"Created {name} = {expr_string}",
                "expression": expr_string,
                "calculated_value": new_param.value,
                "unit": new_param.unit
            })
        except Exception as e:
            write_result(command_id, False, None, f"Failed to create parameter: {str(e)}")


def rename_parameter(command_id, params, ctx):
    """Rename a user parameter. All references will be updated automatically.

    Params:
        old_name (str): Current name of the parameter
        new_name (str): New name for the parameter
    """
    design = ctx.design

    old_name = params.get("old_name")
    new_name = params.get("new_name")

    if not old_name or not new_name:
        return write_result(command_id, False, None, "old_name and new_name required")

    # Check if old parameter exists
    existing = design.userParameters.itemByName(old_name)
    if not existing:
        return write_result(command_id, False, None, f"Parameter '{old_name}' not found")

    # Check if new name already exists
    if design.userParameters.itemByName(new_name):
        return write_result(command_id, False, None, f"Parameter '{new_name}' already exists")

    # Rename the parameter
    existing.name = new_name
    write_result(command_id, True, {
        "message": f"Renamed '{old_name}' to '{new_name}'",
        "old_name": old_name,
        "new_name": new_name
    })


def delete_parameter(command_id, params, ctx):
    """Delete a user parameter.

    Params:
        name (str): Name of the parameter to delete

    Note: Will fail if the parameter is being used by any feature/sketch.
    """
    design = ctx.design

    name = params.get("name")
    if not name:
        return write_result(command_id, False, None, "name required")

    existing = design.userParameters.itemByName(name)
    if not existing:
        return write_result(command_id, False, None, f"Parameter '{name}' not found")

    try:
        existing.deleteMe()
        write_result(command_id, True, {"message": f"Deleted parameter '{name}'"})
    except Exception as e:
        write_result(command_id, False, None, f"Cannot delete '{name}': {str(e)} (may be in use)")


# Command registry for this module
COMMANDS = {
    "set_parameter": set_parameter,
    "rename_parameter": rename_parameter,
    "delete_parameter": delete_parameter,
}
