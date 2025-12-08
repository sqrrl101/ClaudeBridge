"""
Query commands for retrieving design information.

DEPRECATED: Individual query commands have been replaced by export_session
which exports all design data to a timestamped folder in one operation.

Use: {"action": "export_session", "params": {}}

The exported session folder contains:
- design_info.json (replaces get_info, get_full_design)
- bodies.json (replaces get_bodies_detailed, get_circular_edges)
- sketches/overview.json (replaces get_sketches_detailed)
- sketches/sketch_N.json (replaces get_sketch_geometry)
- features.json (replaces get_features)
- parameters.json (replaces get_parameters, get_all_parameters)
- construction_planes.json (replaces get_construction_planes)
"""

# All query commands removed - use export_session instead
COMMANDS = {}
