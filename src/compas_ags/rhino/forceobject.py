from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

import Rhino
from Rhino.Geometry import Point3d

from compas.geometry import subtract_vectors
from compas.geometry import add_vectors
from compas.geometry import scale_vector

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

    def scale_from_2_points(self):
        """Scale the ForceDiagram from 2 reference points
        """
        color = Rhino.ApplicationSettings.AppearanceSettings.FeedbackColor

        vertex_xyz = self.artist.vertex_xyz
        edges = list(self.diagram.edges())
        anchor_xyz = self.diagram.vertex_attributes(self.artist.anchor_vertex, 'xyz')
        origin = self.artist.anchor_point
        origin_pt = Point3d(* origin)

        # get the first reference point
        gp = Rhino.Input.Custom.GetPoint()
        gp.SetCommandPrompt('Select the 1st reference point.')
        gp.Get()
        if gp.CommandResult() != Rhino.Commands.Result.Success:
            return False
        ref1 = gp.Point()

        # get the second reference point
        gp.SetCommandPrompt('Select the 2nd reference point.')

        def OnDynamicDraw(sender, e):
            d1 = origin_pt.DistanceTo(ref1)
            d2 = origin_pt.DistanceTo(e.CurrentPoint)
            ratio = d2 / d1
            for vertex in self.diagram.vertices():
                xyz = self.diagram.vertex_attributes(vertex, 'xyz')
                vector = subtract_vectors(xyz, anchor_xyz)
                vertex_xyz[vertex] = add_vectors(origin, scale_vector(vector, self.artist.scale * ratio))
            for u, v in iter(edges):
                e.Display.DrawDottedLine(Point3d(* vertex_xyz[u]), Point3d(* vertex_xyz[v]), color)

        gp.DynamicDraw += OnDynamicDraw
        gp.Get()
        if gp.CommandResult() != Rhino.Commands.Result.Success:
            return False
        ref2 = gp.Point()

        d1 = origin_pt.DistanceTo(ref1)
        d2 = origin_pt.DistanceTo(ref2)
        ratio = d2 / d1
        scale_factor = self.artist.scale * ratio
        self.artist.scale = scale_factor


# ==============================================================================
# Main
# ==============================================================================

if __name__ == '__main__':

    pass
