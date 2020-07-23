from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

import compas_rhino

from compas_rhino.objects.modifiers import VertexModifier
from compas_rhino.objects.modifiers import EdgeModifier

from compas_rhino.objects import MeshObject


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

    def select_vertex(self):
        """Manually select one vertex in the Rhino view.

        Returns
        -------
        int
            The identifier of the selected vertex.
        """
        pointfilter = compas_rhino.rs.filter.point
        guid = compas_rhino.rs.GetObject(message="Select Vertex.", preselect=True, select=True, filter=pointfilter)
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

    def move_vertex(self, vertex):
        """Move one selected vertex.

        Parameters
        ----------
        vertex : int
            The identifier of the vertex.

        Returns
        -------
        bool
            True if the operation was successful.
            False otherwise.
        """
        return VertexModifier.move_vertex(self.diagram, vertex)

    def move_vertices(self, vertices):
        """Move selected vertices.

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
        return VertexModifier.move_vertices(self.diagram, vertices)

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
