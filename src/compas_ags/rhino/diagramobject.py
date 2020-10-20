from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

import Rhino
from Rhino.Geometry import Point3d

import compas_rhino

from compas.geometry import scale_vector
from compas.geometry import add_vectors
from compas.geometry import subtract_vectors

from compas_rhino.objects import MeshObject


__all__ = ['DiagramObject']


class DiagramObject(MeshObject):
    """A diagram object represents a form or force diagram in the Rhino view.
    """

    @property
    def diagram(self):
        """The diagram associated with the object."""
        return self.mesh

    @diagram.setter
    def diagram(self, diagram):
        self.mesh = diagram

    def unselect(self):
        """Unselect all Rhino objects associated with this diagram object."""
        compas_rhino.rs.UnselectObjects(self.artist.guids)

    def select_vertex(self, message="Select Vertex."):
        """Manually select one vertex in the Rhino view.

        Returns
        -------
        int
            The identifier of the selected vertex.
        """
        pointfilter = compas_rhino.rs.filter.point
        guid = compas_rhino.rs.GetObject(message=message, preselect=True, select=True, filter=pointfilter)
        if guid and guid in self.guid_vertex:
            return self.guid_vertex[guid]

    def select_edge(self, message="Select Edge."):
        """Manually select one edge in the Rhino view.

        Returns
        -------
        tuple of int
            The identifier of the selected edge.
        """
        curvefilter = compas_rhino.rs.filter.curve
        guid = compas_rhino.rs.GetObject(message=message, preselect=True, select=True, filter=curvefilter)
        if guid and guid in self.guid_edge:
            return self.guid_edge[guid]

    def move(self):
        """Move the entire diagram.

        Returns
        -------
        bool
            True if the operation is successful.
            False otherwise.
        """
        def OnDynamicDraw(sender, e):
            translation = subtract_vectors(list(e.CurrentPoint), start)
            for vertex in vertex_xyz:
                vertex_xyz[vertex] = add_vectors(vertex_xyz0[vertex], translation)
            for u, v in iter(edges):
                e.Display.DrawDottedLine(Point3d(* vertex_xyz[u]), Point3d(* vertex_xyz[v]), color)

        color = Rhino.ApplicationSettings.AppearanceSettings.FeedbackColor
        vertex_xyz = self.artist.vertex_xyz
        vertex_xyz0 = {vertex: xyz[:] for vertex, xyz in vertex_xyz.items()}
        edges = list(self.diagram.edges())
        start = compas_rhino.pick_point('Point to move from?')
        if not start:
            return False
        start = list(start)

        gp = Rhino.Input.Custom.GetPoint()
        gp.SetCommandPrompt('Point to move to?')
        gp.DynamicDraw += OnDynamicDraw
        gp.Get()
        if gp.CommandResult() != Rhino.Commands.Result.Success:
            return False

        end = list(gp.Point())
        translation = subtract_vectors(end, start)
        self.location = add_vectors(self.location, translation)
        return True

    def move_vertex(self, vertex, constraint=None, allow_off=None):
        """Move one vertex of the diagram and update the data structure to the new geometry.

        Parameters
        ----------
        vertex : int
            The identifier of the vertex.

        Other Parameters
        ----------------
        constraint : :class:`Rhino.Geometry.GeometryBase`, optional
        allow_off : bool, optional

        Returns
        -------
        bool
            True if the operation was successful.
            False otherwise.
        """
        def OnDynamicDraw(sender, e):
            sp = e.CurrentPoint
            for ep in nbrs:
                e.Display.DrawDottedLine(sp, ep, color)

        color = Rhino.ApplicationSettings.AppearanceSettings.FeedbackColor
        diagram = self.diagram
        vertex_xyz = self.artist.vertex_xyz

        if '_is_edge' in diagram.default_edge_attributes:
            nbrs = [Point3d(* vertex_xyz[nbr]) for nbr in diagram.vertex_neighbors(vertex) if diagram.edge_attribute((vertex, nbr), '_is_edge')]
        else:
            nbrs = [Point3d(* vertex_xyz[nbr]) for nbr in diagram.vertex_neighbors(vertex)]

        gp = Rhino.Input.Custom.GetPoint()
        gp.SetCommandPrompt('Point to move to?')
        if constraint:
            gp.Constrain(constraint, allow_off)
        gp.DynamicDraw += OnDynamicDraw
        gp.Get()
        if gp.CommandResult() != Rhino.Commands.Result.Success:
            return False

        point = list(gp.Point())
        xyz0 = vertex_xyz[vertex]
        dxyz0 = subtract_vectors(point, xyz0)
        dxyz = scale_vector(dxyz0, 1 / self.scale)
        xyz = diagram.vertex_attributes(vertex, 'xyz')
        xyz[:] = add_vectors(xyz, dxyz)
        diagram.vertex_attributes(vertex, 'xyz', xyz)
        return True

    def move_vertices(self, vertices):
        """Move a selection of vertices of the diagram and update the data structure to the new geometry.

        Parameters
        ----------
        vertices : list
            The identifiers of the vertices.

        Returns
        -------
        bool
            True if the operation was successful.
            False otherwise.
        """
        def OnDynamicDraw(sender, e):
            end = e.CurrentPoint
            vector = end - start
            for a, b in lines:
                e.Display.DrawDottedLine(a + vector, b + vector, color)
            for a, b in connectors:
                e.Display.DrawDottedLine(a + vector, b, color)

        diagram = self.diagram
        vertex_xyz = self.artist.vertex_xyz

        color = Rhino.ApplicationSettings.AppearanceSettings.FeedbackColor
        lines = []
        connectors = []
        for vertex in vertices:
            a = vertex_xyz[vertex]
            nbrs = diagram.vertex_neighbors(vertex)
            for nbr in nbrs:
                if '_is_edge' in diagram.default_edge_attributes and not diagram.edge_attribute((vertex, nbr), '_is_edge'):
                    continue
                b = vertex_xyz[nbr]
                line = [Point3d(* a), Point3d(* b)]
                if nbr in vertices:
                    lines.append(line)
                else:
                    connectors.append(line)

        gp = Rhino.Input.Custom.GetPoint()

        gp.SetCommandPrompt('Point to move from?')
        gp.Get()
        if gp.CommandResult() != Rhino.Commands.Result.Success:
            return False
        start = gp.Point()

        gp.SetCommandPrompt('Point to move to?')
        gp.SetBasePoint(start, False)
        gp.DrawLineFromPoint(start, True)
        gp.DynamicDraw += OnDynamicDraw
        gp.Get()
        if gp.CommandResult() != Rhino.Commands.Result.Success:
            return False
        end = gp.Point()

        dxyz0 = list(end - start)
        dxyz = scale_vector(dxyz0, 1 / self.scale)
        for vertex in vertices:
            xyz = diagram.vertex_attributes(vertex, 'xyz')
            xyz[:] = add_vectors(xyz, dxyz)
            diagram.vertex_attributes(vertex, 'xyz', xyz)
        return True


# ==============================================================================
# Main
# ==============================================================================

if __name__ == '__main__':

    pass
