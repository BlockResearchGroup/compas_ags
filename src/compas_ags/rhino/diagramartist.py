from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

import compas_rhino
from compas_rhino.artists import MeshArtist


__all__ = ['DiagramArtist']


class DiagramArtist(MeshArtist):
    """Base artist for diagrams in AGS.

    Parameters
    ----------
    diagram: :class:`compas_ags.diagrams.Diagram`

    Attributes
    ----------
    guid_vertex : dict
        Map between Rhino object GUIDs and force diagram vertex identifiers.
    guid_edge : dict
        Map between Rhino object GUIDs and force diagram edge identifiers.
    guid_face : dict
        Map between Rhino object GUIDs and force diagram face identifiers.
    guid_vertexlabels : dict
        Map between Rhino object GUIDs and force diagram vertex label identifiers.
    guid_edgelabels : dict
        Map between Rhino object GUIDs and force diagram edge label identifiers.
    guid_facelabels : dict
        Map between Rhino object GUIDs and force diagram face label identifiers.
    """

    def __init__(self, diagram, *args, **kwargs):
        super(DiagramArtist, self).__init__(diagram, *args, **kwargs)
        self._guid_vertex = {}
        self._guid_edge = {}
        self._guid_face = {}
        self._guid_vertexlabel = {}
        self._guid_edgelabel = {}
        self._guid_facelabel = {}

    @property
    def guid_vertex(self):
        """Map between Rhino object GUIDs and force diagram vertex identifiers."""
        return self._guid_vertex

    @guid_vertex.setter
    def guid_vertex(self, values):
        self._guid_vertex = dict(values)

    @property
    def guid_edge(self):
        """Map between Rhino object GUIDs and force diagram edge identifiers."""
        return self._guid_edge

    @guid_edge.setter
    def guid_edge(self, values):
        self._guid_edge = dict(values)

    @property
    def guid_face(self):
        """Map between Rhino object GUIDs and force diagram face identifiers."""
        return self._guid_face

    @guid_face.setter
    def guid_face(self, values):
        self._guid_face = dict(values)

    @property
    def guid_vertexlabel(self):
        """Map between Rhino object GUIDs and force diagram vertex label identifiers."""
        return self._guid_vertexlabel

    @guid_vertexlabel.setter
    def guid_vertexlabel(self, values):
        self._guid_vertexlabel = dict(values)

    @property
    def guid_facelabel(self):
        """Map between Rhino object GUIDs and force diagram face label identifiers."""
        return self._guid_facelabel

    @guid_facelabel.setter
    def guid_facelabel(self, values):
        self._guid_facelabel = dict(values)

    @property
    def guid_edgelabel(self):
        """Map between Rhino object GUIDs and force diagram edge label identifiers."""
        return self._guid_edgelabel

    @guid_edgelabel.setter
    def guid_edgelabel(self, values):
        self._guid_edgelabel = dict(values)

    def clear(self):
        """Clear all objects previously drawn by this artist.

        Parameters
        ----------
        None

        Returns
        -------
        None
        """
        guids = []
        guids_vertices = list(self.guid_vertex.keys())
        guids_edges = list(self.guid_edge.keys())
        guids_faces = list(self.guid_face.keys())
        guids_vertexlabels = list(self.guid_vertexlabel.keys())
        guids_edgelabels = list(self.guid_edgelabel.keys())
        guids_facelabels = list(self.guid_facelabel.keys())
        guids += guids_vertices + guids_edges + guids_faces
        guids += guids_vertexlabels + guids_edgelabels + guids_facelabels
        compas_rhino.delete_objects(guids, purge=True)
        self._guid_vertex = {}
        self._guid_edge = {}
        self._guid_face = {}
        self._guid_vertexlabel = {}
        self._guid_edgelabel = {}
        self._guid_facelabel = {}


# ==============================================================================
# Main
# ==============================================================================

if __name__ == "__main__":
    pass
