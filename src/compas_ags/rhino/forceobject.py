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

    def scale_from_3_points(self):
        """Scale the ForceDiagram from 3 points
        """
        color = Rhino.ApplicationSettings.AppearanceSettings.FeedbackColor

        vertex_xyz = self.artist.vertex_xyz
        edges = list(self.diagram.edges())
        anchor_xyz = self.diagram.vertex_attributes(self.artist.anchor_vertex, 'xyz')
        origin = self.artist.anchor_point

        # select the base point as the anchor point
        gp = Rhino.Input.Custom.GetPoint()
        gp.SetCommandPrompt('Select the base point.')
        gp.Get()
        if gp.CommandResult() != Rhino.Commands.Result.Success:
            return False
        base = gp.Point()

        # get the first reference point
        gp = Rhino.Input.Custom.GetPoint()
        gp.SetCommandPrompt('Select the first reference point.')
        gp.DrawLineFromPoint(base, True)
        gp.Get()
        if gp.CommandResult() != Rhino.Commands.Result.Success:
            return False
        ref1 = gp.Point()

        # get the second reference point
        gp.SetCommandPrompt('Select the second reference point.')

        def OnDynamicDraw(sender, e):
            base_ref1 = base.DistanceTo(ref1)
            base_ref2 = base.DistanceTo(e.CurrentPoint)
            ratio = base_ref2 / base_ref1
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

        base_ref1 = base.DistanceTo(ref1)
        base_ref2 = base.DistanceTo(ref2)
        ratio = base_ref2 / base_ref1
        scale_factor = self.artist.scale * ratio
        self.artist.scale = scale_factor

    def scale_from_4_points(self):
        """Scale the ForceDiagram from 4 points
        """
        color = Rhino.ApplicationSettings.AppearanceSettings.FeedbackColor

        vertex_xyz = self.artist.vertex_xyz
        edges = list(self.diagram.edges())
        anchor_xyz = self.diagram.vertex_attributes(self.artist.anchor_vertex, 'xyz')
        origin = self.artist.anchor_point

        # select the start point of reference line
        gp = Rhino.Input.Custom.GetPoint()
        gp.SetCommandPrompt('Select the start point of reference line.')
        gp.Get()
        if gp.CommandResult() != Rhino.Commands.Result.Success:
            return False
        ref1_sp = gp.Point()

        # get the end point of reference line
        gp = Rhino.Input.Custom.GetPoint()
        gp.SetCommandPrompt('Select the end point of reference line.')
        gp.DrawLineFromPoint(ref1_sp, True)
        gp.Get()
        if gp.CommandResult() != Rhino.Commands.Result.Success:
            return False
        ref1_ep = gp.Point()
        gp.EnableDrawLineFromPoint(False)

        # select the start point of target line
        gp.SetCommandPrompt('Select the start point of the target line.')
        gp.Get()
        if gp.CommandResult() != Rhino.Commands.Result.Success:
            return False
        ref2_sp = gp.Point()

        # select the end point of target line
        gp.SetCommandPrompt('Select the end point of the target line.')
        gp.EnableDrawLineFromPoint(True)

        def OnDynamicDraw(sender, e):
            line1 = ref1_sp.DistanceTo(ref1_ep)
            line2 = ref2_sp.DistanceTo(e.CurrentPoint)
            ratio = line2 / line1
            for vertex in self.diagram.vertices():
                xyz = self.diagram.vertex_attributes(vertex, 'xyz')
                vector = subtract_vectors(xyz, anchor_xyz)
                vertex_xyz[vertex] = add_vectors(origin, scale_vector(vector, self.artist.scale * ratio))
            for u, v in iter(edges):
                e.Display.DrawDottedLine(Point3d(* vertex_xyz[u]), Point3d(* vertex_xyz[v]), color)

        gp.DynamicDraw += OnDynamicDraw
        gp.DrawLineFromPoint(ref2_sp, True)
        gp.Get()
        if gp.CommandResult() != Rhino.Commands.Result.Success:
            return False
        ref2_ep = gp.Point()

        line1 = ref1_sp.DistanceTo(ref1_ep)
        line2 = ref2_sp.DistanceTo(ref2_ep)
        ratio = line2 / line1
        scale_factor = self.artist.scale * ratio
        self.artist.scale = scale_factor


# ==============================================================================
# Main
# ==============================================================================

if __name__ == '__main__':

    pass
