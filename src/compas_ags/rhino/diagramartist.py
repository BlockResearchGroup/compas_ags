from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

import compas_rhino
from compas.geometry import scale_vector
from compas.geometry import add_vectors
from compas.geometry import subtract_vectors
from compas.geometry import centroid_points
from compas.geometry import distance_point_point
from compas.utilities import color_to_colordict as colordict
from compas_rhino.artists import MeshArtist


__all__ = ['DiagramArtist']


def textdict(text, items):
    if text is None:
        item_text = {item: str(item) for item in items}
    elif isinstance(text, dict):
        item_text = text
    elif text == 'key':
        item_text = {item: str(item) for item in items}
    elif text == 'index':
        item_text = {item: str(index) for index, item in enumerate(items)}
    else:
        raise NotImplementedError
    return item_text


class DiagramArtist(MeshArtist):
    """Base artist for diagrams in AGS.

    Parameters
    ----------
    diagram: :class:`compas_ags.diagrams.Diagram`

    Attributes
    ----------
    diagram : :class:`compas_ags.diagrams.Diagram`
        The diagram associated with the artist.
    anchor_point : list
        The location of the point where the diagram should be anchored.
    anchor_vertex : int
        The identifier of the vertex that should be anchored to the anchor point.
    scale : float
        Drawing scale of the diagram.
        The scale is such that the drawing length of an edge of the diagram is ``drawing length = scale * real length``.
    vertex_xyz (read-only) : dict
        Maps the vertices of the diagram to a location in the anchored and scaled drawing.
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
        self.settings.update({
            'show.vertices': True,
            'show.edges': True,
            'show.faces': False,
            'show.vertexlabels': False,
            'show.edgelabels': False,
            'show.facelabels': False,
            'show.forcecolors': True,
            'show.forcelabels': False,
            'color.vertices': (0, 0, 0),
            'color.vertexlabels': (255, 255, 255),
            'color.vertices:is_fixed': (0, 255, 255),
            'color.edges': (0, 0, 0),
            'color.edges:is_ind': (0, 255, 255),
            'color.edges:is_external': (0, 255, 0),
            'color.edges:is_reaction': (0, 255, 0),
            'color.edges:is_load': (0, 255, 0),
            'color.faces': (210, 210, 210),
            'color.compression': (0, 0, 255),
            'color.tension': (255, 0, 0),
            'color.anchor': (255, 0, 0),
            'scale.forces': 0.1,
            'tol.edges': 1e-3,
            'tol.forces': 1e-3,
        })
        self._anchor_point = None
        self._anchor_vertex = None
        self._scale = None
        self._guid_vertex = {}
        self._guid_edge = {}
        self._guid_face = {}
        self._guid_vertexlabel = {}
        self._guid_edgelabel = {}
        self._guid_facelabel = {}

    @property
    def diagram(self):
        """The diagram assigned to the artist."""
        return self.mesh

    @diagram.setter
    def diagram(self, diagram):
        self.mesh = diagram

    @property
    def anchor_point(self):
        """Location of the anchor point for the drawing of the diagram."""
        if not self._anchor_point:
            return self.diagram.vertex_attributes(self.anchor_vertex, 'xyz')
        return self._anchor_point

    @anchor_point.setter
    def anchor_point(self, anchor_point):
        self._anchor_point = anchor_point

    @property
    def anchor_vertex(self):
        """Identifier of the anchored vertex."""
        if self._anchor_vertex is None:
            self._anchor_vertex = next(self.diagram.vertices())
        return self._anchor_vertex

    @anchor_vertex.setter
    def anchor_vertex(self, anchor_vertex):
        if anchor_vertex in self.diagram.vertices():
            self._anchor_vertex = anchor_vertex

    @property
    def scale(self):
        """The drawing scale."""
        if self._scale is None:
            return 1.0
        return self._scale

    @scale.setter
    def scale(self, scale):
        self._scale = scale

    @property
    def vertex_xyz(self):
        """Map between diagram vertices and drawing locations."""
        vertex_xyz = {}
        anchor_xyz = self.diagram.vertex_attributes(self.anchor_vertex, 'xyz')
        origin = self.anchor_point
        for vertex in self.diagram.vertices():
            xyz = self.diagram.vertex_attributes(vertex, 'xyz')
            vertex_xyz[vertex] = add_vectors(
                origin,
                scale_vector(
                    subtract_vectors(xyz, anchor_xyz),
                    self.scale))
        return vertex_xyz

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
        guids += list(self.guid_vertex.keys())
        guids += list(self.guid_edge.keys())
        guids += list(self.guid_face.keys())
        guids += list(self.guid_vertexlabel.keys())
        guids += list(self.guid_edgelabel.keys())
        guids += list(self.guid_facelabel.keys())
        compas_rhino.delete_objects(guids, purge=True)
        self._guid_vertex = {}
        self._guid_edge = {}
        self._guid_face = {}
        self._guid_vertexlabel = {}
        self._guid_edgelabel = {}
        self._guid_facelabel = {}

    def draw(self):
        raise NotImplementedError

    def draw_vertices(self, keys=None, color=None):
        """Draw the vertices of the diagram according to the drawing scale.

        Parameters
        ----------
        keys : list, optional
            The identifiers of the vertices that have to be drawn.
        color : str or tuple or dict, optional
            A color specification.
            The default color is in the settings dict.

        Returns
        -------
        list
            The GUIDs of the created Rhino objects.
        """
        vertices = keys or list(self.diagram.vertices())
        vertex_color = colordict(color, vertices, default=self.settings['color.vertices'], colorformat='rgb', normalize=False)
        vertex_xyz = self.vertex_xyz
        points = []
        for vertex in vertices:
            points.append({'pos': vertex_xyz[vertex],
                           'color': vertex_color[vertex],
                           'name': "{}.vertex.{}".format(self.diagram.name, vertex)})
        guids = compas_rhino.draw_points(points, layer=self.layer, clear=False, redraw=False)
        self.guid_vertex = zip(guids, vertices)
        return guids

    def draw_vertexlabels(self, text=None, color=None):
        """Draw the labels of the vertices of the diagram according to the drawing scale.

        Parameters
        ----------
        text : str or dict, optional
            The label text.
        color : str or tuple or dict, optional
            The colors specification of the labels.
            The default color is in the settings.

        Returns
        -------
        list
            The GUIDs of the created Rhino objects.
        """
        vertex_text = textdict(text, list(self.diagram.vertices()))
        vertex_color = colordict(color, vertex_text.keys(), default=self.settings['color.vertices'], colorformat='rgb', normalize=False)
        vertex_xyz = self.vertex_xyz
        labels = []
        for vertex in vertex_text:
            labels.append({'pos': vertex_xyz[vertex],
                           'color': vertex_color[vertex],
                           'text': vertex_text[vertex],
                           'name': "{}.vertexlabel.{}".format(self.diagram.name, vertex)})
        guids = compas_rhino.draw_labels(labels, layer=self.layer, clear=False, redraw=False)
        self.guid_vertexlabel = zip(guids, vertex_text.keys())
        return guids

    def draw_edges(self, keys=None, color=None):
        """Draw the edges of the force diagram according to the drawing scale.

        Parameters
        ----------
        keys : list, optional
            The identifiers of the edges that have to be drawn.
        color : str or tuple or dict, optional
            A color specification.
            The default color is in the settings dict.

        Returns
        -------
        list
            The GUIDs of the created Rhino objects.
        """
        edges = keys or list(self.diagram.edges())
        edge_color = colordict(color, edges, default=self.settings['color.edges'], colorformat='rgb', normalize=False)
        vertex_xyz = self.vertex_xyz
        lines = []
        for edge in edges:
            start = vertex_xyz[edge[0]]
            end = vertex_xyz[edge[1]]
            if distance_point_point(start, end) < self.settings['tol.edges']:
                continue

            lines.append({'start': start,
                          'end': end,
                          'color': edge_color[edge],
                          'name': "{}.edge.{}-{}".format(self.diagram.name, *edge)})
        guids = compas_rhino.draw_lines(lines, layer=self.layer, clear=False, redraw=False)
        self.guid_edge = zip(guids, edges)
        return guids

    def draw_edgelabels(self, text=None, color=None):
        """Draw the labels of the edges of the force diagram according to the drawing scale.

        Parameters
        ----------
        text : str or dict, optional
            The label text.
        color : str or tuple or dict, optional
            The colors specification of the labels.
            The default color is in the settings.

        Returns
        -------
        list
            The GUIDs of the created Rhino objects.
        """
        if text is None:
            edge_text = {edge: "{}-{}".format(*edge) for edge in self.diagram.edges()}
        elif isinstance(text, dict):
            edge_text = text
        else:
            raise NotImplementedError

        edge_color = colordict(color, edge_text.keys(), default=self.settings['color.edges'], colorformat='rgb', normalize=False)
        vertex_xyz = self.vertex_xyz
        labels = []
        for edge in edge_text:
            start = vertex_xyz[edge[0]]
            end = vertex_xyz[edge[1]]
            if distance_point_point(start, end) < self.settings['tol.edges']:
                continue
            pos = [0.5 * (a + b) for a, b in zip(start, end)]
            labels.append({'pos': pos,
                           'color': edge_color[edge],
                           'text': edge_text[edge],
                           'name': "{}.edgelabel.{}-{}".format(self.diagram.name, *edge)})
        guids = compas_rhino.draw_labels(labels, layer=self.layer, clear=False, redraw=False)
        self.guid_edgelabel = zip(guids, edge_text.keys())
        return guids

    def draw_faces(self, keys=None, color=None):
        """Draw the faces of the force diagram according to the drawing scale.

        Parameters
        ----------
        keys : list, optional
            The identifiers of the faces that have to be drawn.
        color : str or tuple or dict, optional
            A color specification.
            The default color is in the settings dict.
        join_faces : bool, optional
            Join the faces into 1 mesh.
            Note that this mesh can only have one color, but will be flat shaded rather than shiny.

        Returns
        -------
        list
            The GUIDs of the created Rhino objects.
        """
        faces = keys or list(self.diagram.faces())
        face_color = colordict(color, faces, default=self.settings['color.faces'], colorformat='rgb', normalize=False)
        vertex_xyz = self.vertex_xyz
        faces_ = []
        for face in faces:
            points = [vertex_xyz[vertex] for vertex in self.diagram.face_vertices(face)]
            faces_.append({'points': points,
                           'color': face_color[face],
                           'name': "{}.face.{}".format(self.diagram.name, face)})
        guids = compas_rhino.draw_faces(faces_, layer=self.layer, clear=False, redraw=False)
        self.guid_face = zip(guids, faces)
        return guids

    def draw_facelabels(self, text=None, color=None):
        """Draw the labels of the faces of the force diagram according to the drawing scale.

        Parameters
        ----------
        text : str or dict, optional
            The label text.
        color : str or tuple or dict, optional
            The colors specification of the labels.
            The default color is in the settings.

        Returns
        -------
        list
            The GUIDs of the created Rhino objects.
        """
        face_text = textdict(text, list(self.diagram.faces()))
        face_color = colordict(color, face_text.keys(), default=self.settings['color.faces'], colorformat='rgb', normalize=False)
        vertex_xyz = self.vertex_xyz
        labels = []
        for face in face_text:
            pos = centroid_points([vertex_xyz[vertex] for vertex in self.diagram.face_vertices(face)])
            labels.append({'pos': pos,
                           'color': face_color[face],
                           'text': face_text[face],
                           'name': "{}.facelabel.{}".format(self.diagram.name, face)})
        guids = compas_rhino.draw_labels(labels, layer=self.layer, clear=False, redraw=False)
        self.guid_facelabel = zip(guids, face_text.keys())
        return guids


# ==============================================================================
# Main
# ==============================================================================

if __name__ == "__main__":
    pass
