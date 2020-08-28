from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

from compas_ags.rhino.diagramobject import DiagramObject
from compas_ags.rhino.forceinspector import ForceDiagramInspector


__all__ = ['ForceObject']


class ForceObject(DiagramObject):
    """A force object represents a force diagram in the Rhino view.
    """

    def __init__(self, diagram, scene=None, name=None, layer=None, visible=True, settings=None):
        super(ForceObject, self).__init__(diagram, scene, name, layer, visible, settings)
        self._inspector = None

    @property
    def inspector(self):
        """:class:`compas_ags.rhino.ForceDiagramInspector`: An inspector conduit."""
        if not self._inspector:
            self._inspector = ForceDiagramInspector(self.diagram)
        return self._inspector

    def inspector_on(self, form):
        self.inspector.form_vertex_xyz = form.artist.vertex_xyz
        self.inspector.force_vertex_xyz = self.artist.vertex_xyz
        self.inspector.enable()

    def inspector_off(self):
        self.inspector.disable()


# ==============================================================================
# Main
# ==============================================================================

if __name__ == '__main__':

    pass
