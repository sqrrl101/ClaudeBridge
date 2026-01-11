"""
Body selection and retrieval helpers for Fusion 360.
"""

from .components import collect_all_components


def get_all_bodies(root):
    """
    Get all bodies across all components with global indexing.

    Args:
        root: Root component

    Returns:
        List of tuples: (body, global_index, component)
    """
    all_components = collect_all_components(root)
    bodies = []
    global_index = 0

    for comp in all_components:
        for i in range(comp.bRepBodies.count):
            body = comp.bRepBodies.item(i)
            bodies.append((body, global_index, comp))
            global_index += 1

    return bodies


def get_body_by_global_index(root, index):
    """
    Get a body by global index across all components.

    Args:
        root: Root component
        index: Global body index

    Returns:
        tuple: (body, component, error_message)
    """
    all_bodies = get_all_bodies(root)

    if not all_bodies:
        return None, None, "No bodies in design"

    if index < 0 or index >= len(all_bodies):
        return None, None, f"Invalid body index {index}. Design has {len(all_bodies)} bodies."

    body, _, comp = all_bodies[index]
    return body, comp, None


def get_body_by_index(root, index):
    """
    Get a body from the root component by index.

    Args:
        root: Root component
        index: Body index

    Returns:
        tuple: (body, error_message) - body is None if error
    """
    if index >= root.bRepBodies.count:
        return None, f"Invalid body index {index}. Design has {root.bRepBodies.count} bodies."
    return root.bRepBodies.item(index), None
