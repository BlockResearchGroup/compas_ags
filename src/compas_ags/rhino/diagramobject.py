from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

import compas
import compas_rhino

from compas.geometry import scale_vector
from compas.geometry import add_vectors
from compas.geometry import subtract_vectors
from compas_rhino.objects.modifiers import VertexModifier
from compas_rhino.objects.modifiers import EdgeModifier

from compas_rhino.objects import MeshObject

if compas.IPY:
    if compas.RHINO:
        import Rhino
        from Rhino.Geometry import Point3d


__all__ = ['DiagramObject']


class DiagramObject(MeshObject):
    """A diagram object represents a form or force diagram in the Rhino view.

    Parameters
    ----------
    diagram : :class:`compas_ags.diagrams.FormDiagram`
        The form diagram instance.
    settings : dict, optional
        Visualisation settings for the corresponding Rhino object(s).
        Default is ``None``, in which case the default settings of the artist are used.

    Attributes
    ----------
    diagram : :class:`compas_ags.diagrams.Diagram`
        Stores the diagram instance.
    artist : :class:`compas_ags.rhino.DiagramArtist`.
        Instance of a diagram artist.
    """

    def __init__(self, diagram, scene=None, name=None, layer=None, visible=True, settings=None):
        super(DiagramObject, self).__init__(diagram, scene, name, layer, visible, settings)

    @property
    def diagram(self):
        """The diagram associated with the object."""
        return self._item

    @diagram.setter
    def diagram(self, diagram):
        self._item = diagram

    def draw(self):
        """Draw the diagram using the artist."""
        self.artist.draw()

    def clear(self):
        """Clear the diagram object and all related Rhino objects from the scene."""
        self.artist.clear()
        self.artist.clear_layer()

    def unselect(self):
        """Unselect all Rhino objects associated with this diagram object."""
        guids = []
        guids += list(self.artist.guid_vertex.keys())
        guids += list(self.artist.guid_vertexlabel.keys())
        guids += list(self.artist.guid_edge.keys())
        guids += list(self.artist.guid_edgelabel.keys())
        guids += list(self.artist.guid_face.keys())
        guids += list(self.artist.guid_facelabel.keys())
        compas_rhino.rs.UnselectObjects(guids)

    def select_vertex(self, message="Select Vertex."):
        """Manually select one vertex in the Rhino view.

        Returns
        -------
        int
            The identifier of the selected vertex.
        """
        pointfilter = compas_rhino.rs.filter.point
        guid = compas_rhino.rs.GetObject(message=message, preselect=True, select=True, filter=pointfilter)
        if guid and guid in self.artist.guid_vertex:
            return self.artist.guid_vertex[guid]

    def select_vertices(self):
        """Manually select vertices in the Rhino view.

        Returns
        -------
        list
            The identifiers of the selected vertices.
        """
        pointfilter = compas_rhino.rs.filter.point
        guids = compas_rhino.rs.GetObjects(message="Select Vertices.", preselect=True, select=True, group=False, filter=pointfilter)
        if not guids:
            return []
        return [self.artist.guid_vertex[guid] for guid in guids if guid in self.artist.guid_vertex]

    def select_edge(self):
        """Manually select one edge in the Rhino view.

        Returns
        -------
        tuple of int
            The identifier of the selected edge.
        """
        curvefilter = compas_rhino.rs.filter.curve
        guid = compas_rhino.rs.GetObject(message="Select Edge.", preselect=True, select=True, filter=curvefilter)
        if guid and guid in self.artist.guid_edge:
            return self.artist.guid_edge[guid]

    def select_edges(self):
        """Manually select edges in the Rhino view.

        Returns
        -------
        list
            The identifiers of the selected edges.
        """
        curvefilter = compas_rhino.rs.filter.curve
        guids = compas_rhino.rs.GetObjects(message="Select Edges.", preselect=True, select=True, group=False, filter=curvefilter)
        if not guids:
            return []
        return [self.artist.guid_edge[guid] for guid in guids if guid in self.artist.guid_edge]

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

        diagram = self.diagram
        vertex_xyz = self.artist.vertex_xyz
        scale = 1 / self.artist.scale
        color = Rhino.ApplicationSettings.AppearanceSettings.FeedbackColor
        if '_is_edge' in diagram.default_edge_attributes:
            nbrs = [vertex_xyz[nbr] for nbr in diagram.vertex_neighbors(vertex) if diagram.edge_attribute((vertex, nbr), '_is_edge')]
        else:
            nbrs = [vertex_xyz[nbr] for nbr in diagram.vertex_neighbors(vertex)]
        nbrs = [Point3d(*xyz) for xyz in nbrs]
        gp = Rhino.Input.Custom.GetPoint()
        gp.SetCommandPrompt('Point to move to?')
        gp.DynamicDraw += OnDynamicDraw
        if constraint:
            gp.Constrain(constraint, allow_off)
        gp.Get()
        if gp.CommandResult() != Rhino.Commands.Result.Success:
            return False
        pos1 = vertex_xyz[vertex]
        pos2 = list(gp.Point())
        vector = scale_vector(subtract_vectors(pos2, pos1), scale)
        xyz = diagram.vertex_attributes(vertex, 'xyz')
        diagram.vertex_attributes(vertex, 'xyz', add_vectors(xyz, vector))
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
                a = a + vector
                b = b + vector
                e.Display.DrawDottedLine(a, b, color)
            for a, b in connectors:
                a = a + vector
                e.Display.DrawDottedLine(a, b, color)

        diagram = self.diagram
        vertex_xyz = self.artist.vertex_xyz
        scale = 1 / self.artist.scale
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
        vector = scale_vector(list(end - start), scale)
        for vertex in vertices:
            xyz = diagram.vertex_attributes(vertex, 'xyz')
            diagram.vertex_attributes(vertex, 'xyz', add_vectors(xyz, vector))
        return True

    def modify_vertices(self, vertices=None, names=None):
        """Modify the attributes of a selection of diagram vertices.

        Parameters
        ----------
        vertices : list, optional
            The identifiers of selected vertices.
            Default is ``None``.
        names : list, optional
            The names of the attributes that should be modified.

        Returns
        -------
        bool
            True if the operation was successful.
            False otherwise.
        """
        vertices = vertices or list(self.diagram.vertices())
        names = [name for name in sorted(self.diagram.default_vertex_attributes.keys()) if not name.startswith('_')]
        return VertexModifier.update_vertex_attributes(self.diagram, vertices, names)

    def modify_edges(self, edges=None, names=None):
        """Modify the attributes of a selection of diagram edges.

        Parameters
        ----------
        edges : list, optional
            The identifiers of selected edges.
            Default is ``None``.
        names : list, optional
            The names of the attributes that should be modified.

        Returns
        -------
        bool
            True if the operation was successful.
            False otherwise.
        """
        edges = edges or list(self.diagram.edges())
        names = [name for name in sorted(self.diagram.default_edge_attributes.keys()) if not name.startswith('_')]
        return EdgeModifier.update_edge_attributes(self.diagram, edges, names)


# ==============================================================================
# Main
# ==============================================================================

if __name__ == '__main__':

    pass
