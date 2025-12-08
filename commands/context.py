"""
Context object that provides access to Fusion 360 application objects.
"""

import adsk.core
import adsk.fusion


class CommandContext:
    """
    Provides access to common Fusion 360 objects for command handlers.

    Attributes:
        app: The Fusion 360 Application object
        ui: The UserInterface object
        design: The active Design (may be None)
        root: The root component (if design exists)
        active_component: The currently active component (if design exists)
        sketches: The sketches collection (from active component)
        extrudes: The extrude features collection (from active component)
    """

    def __init__(self, app, ui):
        self.app = app
        self.ui = ui
        self._design = None
        self._root = None

    @property
    def design(self):
        """Get the active design, refreshed each access."""
        return adsk.fusion.Design.cast(self.app.activeProduct)

    @property
    def root(self):
        """Get the root component of the active design."""
        design = self.design
        return design.rootComponent if design else None

    @property
    def active_component(self):
        """Get the currently active component (the one being edited)."""
        design = self.design
        if not design:
            return None
        # activeEditObject returns the component currently being edited
        # This respects which component the user has activated in the browser
        active = design.activeEditObject
        if hasattr(active, 'sketches'):
            # It's a component
            return active
        # Fall back to root if activeEditObject is not a component
        return design.rootComponent

    @property
    def sketches(self):
        """Get the sketches collection from active component."""
        comp = self.active_component
        return comp.sketches if comp else None

    @property
    def extrudes(self):
        """Get the extrude features collection from active component."""
        comp = self.active_component
        return comp.features.extrudeFeatures if comp else None

    def require_design(self):
        """
        Check if a design is active.

        Returns:
            tuple: (success: bool, error_message: str or None)
        """
        if not self.design:
            return False, "No active design"
        return True, None
