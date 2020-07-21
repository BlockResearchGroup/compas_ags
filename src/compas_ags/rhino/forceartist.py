from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

import compas_rhino

from compas.geometry import distance_point_point
from compas.utilities import i_to_rgb
from compas.utilities import color_to_colordict

from compas_ags.rhino.diagramartist import DiagramArtist


__all__ = ['ForceArtist']


class ForceArtist(DiagramArtist):
    """Artist for force diagrams in AGS.

    Parameters
    ----------
    force: compas_ags.diagrams.ForceDiagram
        The force diagram to draw.
    form: compas_ags.diagrams.FormDiagram, optional, default is None
        The dual graph of the force diagram
    layer: string, optional, default is None
        The name of the layer that will contain the forcediagram.

    Attributes
    ----------
    force (read-only): :class:`compas_ags.diagrams.ForceDiagram`
    form : :class:`compas_ags.diagrams.FormDiagram`
    settings : dict
        Visualisation settings.
    guids : dict
        GUIDs of Rhino objects created by the artists.
    scale : float
        The scale of the diagram.
        The magnitude of force represented by an edge is ``length * scale``.

    """

    def __init__(self, force, form=None, scale=None, layer=None):
        super(ForceArtist, self).__init__(force, layer=layer)
        self._scale = None
        self._form = None
        self.scale = scale
        self.form = form
        self.settings.update({
            'show.vertices': True,
            'show.vertices:is_anchor': True,
            'show.edges': True,
            'show.faces': False,
            'show.vertexlabels': True,
            'show.edgelabels': False,
            'show.facelabels': False,
            'color.vertices': (255, 255, 255),
            'color.vertices:is_anchor':(255, 0, 0),
            'color.vertices:is_fixed': (255, 0, 0),
            'color.edges': (0, 0, 0),
            'color.edges:is_ind': (255, 255, 255),
            'color.edges:is_external': (0, 255, 0),
            'color.faces': (210, 210, 210),
            'color.compression': (0, 0, 255),
            'color.tension': (255, 0, 0)
        })

    @property
    def force(self):
        return self.mesh

    @property
    def scale(self):
        if self._scale is None:
            self._scale = 1.0
        return self._scale

    @scale.setter
    def scale(self, scale):
        self._scale = scale

    # def update_edge_force(self):
    #     (u, v) = list(self.force.edges())[0] # get an edge
    #     # check whether the force diagram is scaled already
    #     if self.force.edge_attribute((u, v), 'force') is None:
    #         self.force.update_default_edge_attributes({'force': 0.0})
    #         for i, ((u, v), attr) in enumerate(self.force.edges(data=True)):
    #             length = self.force.edge_length(u, v)
    #             length = round(length, 2)
    #             attr['force'] = length
    #     else:  # TO CHECK???!!
    #         for i, ((u, v), attr) in enumerate(self.force.edges(data=True)):
    #             length = self.force.edge_length(u, v)
    #             length = round(length, 2)
    #             attr['force'] = length

    def rescale(self):
        form_x = self.form.vertices_attribute('x')
        form_y = self.form.vertices_attribute('y')
        form_xdim = max(form_x) - min(form_x)
        form_ydim = max(form_y) - min(form_y)
        force_x = self.force.vertices_attribute('x')
        force_y = self.force.vertices_attribute('y')
        force_xdim = max(force_x) - min(force_x)
        force_ydim = max(force_y) - min(force_y)
        scale = max([force_xdim / form_xdim, force_ydim / form_ydim])
        self._scale = scale
        return scale

    def draw(self):
        """Draw the force diagram.

        The visible components, display properties and visual style of the form diagram
        drawn by this method can be fully customised using the configuration items
        in the settings dict: ``FormArtist.settings``.

        The method will clear the scene of any objects it has previously drawn
        and keep track of any newly created objects using their GUID.

        Parameters
        ----------
        None

        Returns
        -------
        None
        """
        self.clear()
        self.clear_layer()
        # vertices
        if self.settings['show.vertices']:
            color = {}
            color.update({vertex: self.settings['color.vertices'] for vertex in self.force.vertices()})
            self.draw_vertices(color=color)
        # vertexlabels
        if self.settings['show.vertexlabels']:
            self.draw_vertexlabels()
        # edges
        if self.settings['show.edges']:
            color = {}
            color.update({edge: self.settings['color.edges'] for edge in self.force.edges()})
            self.draw_edges(color=color)
        # edgelabels
        if self.settings['show.edgelabels']:
            text = {edge: index for index, edge in enumerate(self.force.edges())}
            color.update({edge: self.settings['color.edges'] for edge in self.force.edges()})
            self.draw_edgelabels(text=text, color=color)

    def draw_vertices(self, keys=None, color=None):
        """Draw the vertices of the force diagram according to the drawing scale.

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
        keys = keys or list(self.force.vertices())
        colordict = color_to_colordict(color,
                                       keys,
                                       default=self.settings['color.vertices'],
                                       colorformat='rgb',
                                       normalize=False)
        anchor = self.force.anchor()
        dx, dy = self.force.vertex_coordinates(anchor, 'xy')
        points = []
        for key in keys:
            x, y = self.force.vertex_attributes(key, 'xy')
            points.append({
                'pos': [dx + (x - dx) / self.scale, dy + (y - dy) / self.scale, 0],
                'name': "{}.vertex.{}".format(self.force.name, key),
                'color': colordict[key]
            })
        guids = compas_rhino.draw_points(points, layer=self.layer, clear=False, redraw=False)
        self.guid_vertex = zip(guids, keys)
        return guids

    def draw_vertexlabels(self, text=None, color=None):
        """Draw the labels of the vertices of the force diagram according to the drawing scale.

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
            textdict = {key: str(key) for key in self.force.vertices()}
        elif isinstance(text, dict):
            textdict = text
        elif text == 'key':
            textdict = {key: str(key) for key in self.force.vertices()}
        elif text == 'index':
            textdict = {key: str(index) for index, key in enumerate(self.force.vertices())}
        else:
            raise NotImplementedError
        colordict = color_to_colordict(color,
                                       textdict.keys(),
                                       default=self.settings.get('color.vertices'),
                                       colorformat='rgb',
                                       normalize=False)
        anchor = self.force.anchor()
        dx, dy = self.force.vertex_coordinates(anchor, 'xy')
        labels = []
        for key, text in iter(textdict.items()):
            x, y = self.force.vertex_attributes(key, 'xy')
            labels.append({
                'pos': [dx + (x - dx) / self.scale, dy + (y - dy) / self.scale, 0],
                'name': "{}.vertex.label.{}".format(self.force.name, key),
                'color': colordict[key],
                'text': textdict[key]
            })
        guids = compas_rhino.draw_labels(labels, layer=self.layer, clear=False, redraw=False)
        self.guid_vertexlabel = zip(guids, textdict.keys())
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
        keys = keys or list(self.force.edges())
        colordict = color_to_colordict(color,
                                       keys,
                                       default=self.settings.get('color.edges'),
                                       colorformat='rgb',
                                       normalize=False)
        anchor = self.force.anchor()
        dx, dy = self.force.vertex_coordinates(anchor, 'xy')
        lines = []
        for u, v in keys:
            u_x, u_y = self.force.vertex_attributes(u, 'xy')
            v_x, v_y = self.force.vertex_attributes(v, 'xy')
            lines.append({
                'start': [dx + (u_x - dx) / self.scale, dy + (u_y - dy) / self.scale, 0],
                'end': [dx + (v_x - dx) / self.scale, dy + (v_y - dy) / self.scale, 0],
                'color': colordict[(u, v)],
                'name': "{}.edge.{}-{}".format(self.force.name, u, v)
            })
        guids = compas_rhino.draw_lines(lines, layer=self.layer, clear=False, redraw=False)
        self.guid_edge = zip(guids, keys)
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
            textdict = {(u, v): "{}-{}".format(u, v) for u, v in self.force.edges()}
        elif isinstance(text, dict):
            textdict = text
        else:
            raise NotImplementedError
        colordict = color_to_colordict(color,
                                       textdict.keys(),
                                       default=self.settings.get('color.edges'),
                                       colorformat='rgb',
                                       normalize=False)
        anchor = self.force.anchor()
        dx, dy = self.force.vertex_coordinates(anchor, 'xy')
        labels = []
        for (u, v), text in iter(textdict.items()):
            u_x, u_y = self.force.vertex_attributes(u, 'xy')
            v_x, v_y = self.force.vertex_attributes(v, 'xy')
            s = [dx + (u_x - dx) / self.scale, dy + (u_y - dy) / self.scale, 0]
            e = [dx + (v_x - dx) / self.scale, dy + (v_y - dy) / self.scale, 0]
            labels.append({
                'pos': [(a + b) / 2 for a, b in zip(s, e)],
                'name': "{}.edge.label.{}-{}".format(self.force.name, u, v),
                'color': colordict[(u, v)],
                'text': textdict[(u, v)]
            })
        guids = compas_rhino.draw_labels(labels, layer=self.layer, clear=False, redraw=False)
        self.guid_edgelabel = zip(guids, textdict.keys())
        return guids

    def draw_faces(self, keys=None, color=None, join_faces=False):
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
        keys = keys or list(self.force.faces())
        colordict = color_to_colordict(color,
                                       keys,
                                       default=self.settings.get('color.faces'),
                                       colorformat='rgb',
                                       normalize=False)
        anchor = self.force.anchor()
        dx, dy = self.force.vertex_coordinates(anchor, 'xy')
        faces = []
        for fkey in keys:
            points = self.force.face_coordinates(fkey)
            scaled_points = [[dx + (pt[0] - dx) / self.scale, dy + (pt[1] - dy) / self.scale, 0] for pt in points]
            faces.append({
                'points': scaled_points,
                'name': "{}.face.{}".format(self.force.name, fkey),
                'color': colordict[fkey],
            })
        guids = compas_rhino.draw_faces(faces, layer=self.layer, clear=False, redraw=False)
        if join_faces:
            guid = rs.JoinMeshes(guids, delete_input=True)
            rs.ObjectLayer(guid, self.layer)
            rs.ObjectName(guid, '{}.mesh'.format(self.force.name))
            if color:
                rs.ObjectColor(guid, color)
            guids = [guid]
        self.guid_face = zip(guids, keys)
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
        if text is None:
            textdict = {key: str(key) for key in self.force.faces()}
        elif isinstance(text, dict):
            textdict = text
        else:
            raise NotImplementedError
        colordict = color_to_colordict(color,
                                       textdict.keys(),
                                       default=self.settings.get('color.faces'),
                                       colorformat='rgb',
                                       normalize=False)
        anchor = self.force.anchor()
        dx = self.force.vertex_coordinates(anchor)[0]
        dy = self.force.vertex_coordinates(anchor)[1]
        labels = []
        for key, text in iter(textdict.items()):
            cx, cy, _ = self.force.face_centroid(key)
            labels.append({
                'pos': [dx + (cx - dx) / self.scale, dy + (cy - dy) / self.scale, 0],
                'name': "{}.face.label.{}".format(self.force.name, key),
                'color': colordict[key],
                'text': textdict[key],
            })
        guids = compas_rhino.draw_labels(labels, layer=self.layer, clear=False, redraw=False)
        self.guid_facelabel = zip(guids, textdict.keys())
        return guids

    # def scale_diagram(self, scale):
    #     # TO BE DELETED?
    #     # be careful to use... this modify the force diagram, instead of just drawing
    #     x = self.force.vertices_attribute('x')
    #     y = self.force.vertices_attribute('y')
    #     anchor = self.force.anchor()
    #     dx = self.force.vertex_coordinates(anchor)[0]
    #     dy = self.force.vertex_coordinates(anchor)[1]
    #     for vkey, attr in self.force.vertices(True):
    #         attr['x'] = dx + (attr['x'] - dx) / scale
    #         attr['y'] = dy + (attr['y'] - dy) / scale

    # def draw_anchor_vertex(self, color=None):
    #     self.clear_anchor_vertex()
    #     anchor = self.force.anchor()
    #     self.clear_vertexlabels(keys=[anchor])
    #     labels = []
    #     labels.append({
    #         'pos'  : self.force.vertex_coordinates(anchor),
    #         'text' : str(anchor),
    #         'color': color or self.settings.get('color.anchor'),
    #         'name' : "{}.anchor_vertex.{}".format(self.force.name, anchor)
    #     })
    #     compas_rhino.draw_labels(labels, layer=self.layer, clear=False, redraw=True)

    # def draw_edge_force(self, draw=True):
    #     force_dict = {}
    #     c_dict  = {}
    #     max_length = 0

    #     for i, ((u, v), attr) in enumerate(self.force.edges(data=True)):
    #         length = attr['force']
    #         if length > max_length:
    #             max_length = length
    #         force_dict[(u, v)] = length

    #     for i, (u, v) in enumerate(self.force.edges()):
    #         value = force_dict[(u, v)] / max_length
    #         c_dict[(u, v)] = i_to_rgb(value)

    #     if draw is True:
    #         self.draw_scale_edgelabels(text=dict((v,"%s kN" % k) for v, k in force_dict.items()), color=c_dict)
    #     return c_dict

    # def draw_independent_edges(self):
    #     self.clear_independent_edge()
    #     if self.form is None:
    #         raise "form diagram doesn't exist"
    #     else:
    #         indices = find_force_ind(self.form, self.force)

    #     anchor = self.force.anchor()
    #     dx = self.force.vertex_coordinates(anchor)[0]
    #     dy = self.force.vertex_coordinates(anchor)[1]

    #     lines = []
    #     for index, ((u, v), attr) in enumerate(self.force.edges(True)):
    #         if (u, v) in indices:
    #             u_x = self.force.vertex_coordinates(u)[0]
    #             u_y = self.force.vertex_coordinates(u)[1]
    #             v_x = self.force.vertex_coordinates(v)[0]
    #             v_y = self.force.vertex_coordinates(v)[1]
    #             lines.append({
    #                 'start': [dx + (u_x - dx) / self.scale, dy + (u_y - dy) / self.scale, 0],
    #                 'end': [dx + (v_x - dx) / self.scale, dy + (v_y - dy) / self.scale, 0],
    #                 'name': "{}.independent_edge.{}".format(self.force.name, index),
    #                 'width': 1.0
    #             })
    #     return compas_rhino.draw_lines(lines, layer=self.layer, clear=False, redraw=True)


# ==============================================================================
# Main
# ==============================================================================

if __name__ == "__main__":
    pass
