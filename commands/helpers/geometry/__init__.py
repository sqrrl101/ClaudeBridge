"""
Geometry helpers package for Fusion 360.

This package provides utilities for working with Fusion 360 geometry:
- components: Component hierarchy traversal
- sketches: Sketch selection and retrieval
- bodies: Body selection
- edges: Edge collection
- faces: Face selection and analysis
- planes: Construction planes and axes
- occurrences: Occurrence and joint geometry helpers
"""

from .components import collect_all_components
from .sketches import get_all_sketches, get_sketch_by_global_index, get_sketch_by_index
from .bodies import get_body_by_index, get_body_by_global_index, get_all_bodies
from .edges import collect_edges
from .faces import find_top_face
from .planes import get_construction_axis, get_construction_plane
from .occurrences import (
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

__all__ = [
    'collect_all_components',
    'get_all_sketches',
    'get_sketch_by_global_index',
    'get_sketch_by_index',
    'get_body_by_index',
    'get_body_by_global_index',
    'get_all_bodies',
    'collect_edges',
    'find_top_face',
    'get_construction_axis',
    'get_construction_plane',
    # Occurrence/joint helpers
    'get_occurrence_by_index',
    'get_occurrence_by_name',
    'get_joint_direction',
    'get_key_point_type',
    'get_joint_type_setter',
    'create_transform_matrix',
    'get_face_from_occurrence',
    'get_edge_from_occurrence',
    'create_joint_geometry_from_spec',
]
