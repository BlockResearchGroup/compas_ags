from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

import compas_rhino

from compas_rhino.objects.modifiers import VertexModifier
from compas_ags.rhino.formartist import FormArtist


__all__ = ['FormObject']


class FormObject(object):
    """A form object represents a form diagram in the Rhino model space.

    Parameters
    ----------
    diagram : :class:`compas_ags.diagrams.FormDiagram`
        The form diagram instance.
    settings : dict, optional
        Visualisation settings for the corresponding Rhino object(s).
        Default is ``None``, in which case the default settings of the artist are used.

    Attributes
    ----------
    item : :class:`compas_ags.diagrams.FormDiagram`
        Stores the form diagram instance.
    diagram : :class:`compas_ags.diagrams.FormDiagram`
        Alias for ``item``.
    artist : :class:`compas_ags.rhino.FormArtist`.
        Instance of a form diagram artist.
    """

    def __init__(self, diagram, settings=None, **kwargs):
        self.item = diagram
        self.artist = FormArtist(self.item, settings=settings, **kwargs)

    @property
    def diagram(self):
        """The diagram associated with the object."""
        return self.item

    @diagram.setter
    def diagram(self, diagram):
        self.item = diagram

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
        guids += list(self.artist.guid_force.keys())
        compas_rhino.rs.UnselectObjects(guids)

    def select_vertex(self):
        """Manually select one vertex in the Rhino view.

        Returns
        -------
        int
            The identifier of the selected vertex.
        """
        pointfilter = compas_rhino.rs.filter.point
        guid = compas_rhino.rs.GetObject(message="Select Form Vertex.", preselect=True, select=True, filter=pointfilter)
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
        guids = compas_rhino.rs.GetObjects(message="Select Form Vertices.", preselect=True, select=True, group=False, filter=pointfilter)
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
        guid = compas_rhino.rs.GetObject(message="Select Form Edge.", preselect=True, select=True, filter=curvefilter)
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
        guids = compas_rhino.rs.GetObjects(message="Select Form Edges.", preselect=True, select=True, group=False, filter=curvefilter)
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
            True if the execution was successful.
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
            True if the execution was successful.
            False otherwise.
        """
        return VertexModifier.move_vertices(self.diagram, vertices)

    def modify_vertices(self):
        pass

    def modify_edges(self):
        pass


# ==============================================================================
# Main
# ==============================================================================

if __name__ == '__main__':

    pass
