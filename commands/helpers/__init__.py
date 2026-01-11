"""
Shared helper utilities for command handlers.

Packages:
- geometry/: Geometry helpers (components, sketches, bodies, edges, faces, planes)

Modules:
- sketch_curves: Sketch curve access (lines, circles, arcs, etc.)
- command_utils: Decorators for reducing boilerplate
- validation: Parameter validation
"""

# Geometry helpers (from geometry/ package)
from .geometry import (
    collect_all_components,
    get_all_sketches,
    get_sketch_by_global_index,
    get_body_by_index,
    get_body_by_global_index,
    get_all_bodies,
    get_sketch_by_index,
    collect_edges,
    find_top_face,
    get_construction_axis,
    get_construction_plane,
    # Occurrence/joint helpers
    get_occurrence_by_index,
    get_occurrence_by_name,
    get_joint_direction,
    get_key_point_type,
    get_joint_type_setter,
    create_transform_matrix,
    get_face_from_occurrence,
    get_edge_from_occurrence,
    create_joint_geometry_from_spec,
)

# Sketch curve accessors
from .sketch_curves import (
    get_line,
    get_circle,
    get_arc,
    get_ellipse,
    get_line_endpoint,
    get_circle_center,
    get_arc_center,
    get_arc_endpoint,
    get_constraint,
    get_sketch_point,
)

# Command decorators
from .command_utils import with_sketch, with_error_handling

# Validation helpers
from .validation import require_param, get_operation_type
