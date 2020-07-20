from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

import compas_rhino

from compas.geometry import distance_point_point
from compas.utilities import i_to_rgb
from compas.utilities import color_to_colordict
from compas_rhino.artists import MeshArtist

# from compas_ags.rhino import find_force_ind
# from .diagramhelper import check_edge_pairs

# try:
#     import rhinoscriptsyntax as rs
# except ImportError:
#     compas.raise_if_ironpython()


__all__ = ['ForceArtist']


class ForceArtist(MeshArtist):
    """Inherits the compas :class:`MeshArtist`, provides functionality for visualisation of graphic statics applications.

    Parameters
    ----------
    force: compas_ags.diagrams.ForceDiagram
        The force diagram to draw.
    form: compas_ags.diagrams.FormDiagram, optional, default is None
        The dual graph of the force diagram
    layer: string, optional, default is None
        The name of the layer that will contain the forcediagram.
    scale_diagram: bool, optional (`True`)
        If `True`, scale the diagram to a proper size for visualization

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

    def __init__(self, force, form=None, layer=None, scale_diagram=True):
        super(ForceArtist, self).__init__(force, layer=layer)
        self._scale = 1.0
        self.form = form
        self.settings.update({
            'color.anchor':(255, 0, 0)
        })
        self.update_edge_force()
        self.scale_diagram = scale_diagram
        self.scale = self.calculate_scale()

    @property
    def force(self):
        return self.mesh

    @property
    def scale(self):
        return self._scale

    # @scale.setter
    # def scale(self, scale):
    #     if self.scale_diagram:
    #         self._scale = scale

    def rescale(self):
        # if not self.scale_diagram:
        #     return 1.0
        # if not self.form:
        #     return 1.0
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

    def clear(self):
        """Clear all objects previously drawn by this artist.

        Parameters
        ----------
        None

        Returns
        -------
        None
        """
        for name in list(self.guids.keys()):
            guids = list(self.guids[name].values())
            compas_rhino.delete_objects(guids)
            del self.guids[name]

    def draw(self):
        self.clear()
        self.draw_vertices()
        self.draw_vertexlabels()
        self.draw_edges()
        if self.form is not None:
            self.draw_scale_edgelabels(text=check_edge_pairs(self.form, self.force)[1])
        self.redraw()

    def draw_vertices(self, keys=None, color=None):
        anchor = self.force.anchor()
        dx, dy = self.force.vertex_coordinates(anchor, 'xy')

        keys = keys or list(self.force.vertices())
        colordict = color_to_colordict(color,
                                       keys,
                                       default=self.settings.get('color.vertex'),
                                       colorformat='rgb',
                                       normalize=False)
        points = []
        for key in keys:
            x, y = self.force.vertex_attributes(key, 'xy')
            points.append({
                'pos': [dx + (x - dx) / self.scale, dy + (y - dy) / self.scale, 0],
                'name': "{}.vertex.{}".format(self.force.name, key),
                'color': colordict[key]
            })
        return compas_rhino.draw_points(points, layer=self.layer, clear=False, redraw=False)

    def draw_vertexlabels(self, text=None, color=None):
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
        anchor = self.force.anchor()
        dx, dy = self.force.vertex_coordinates(anchor, 'xy')
        colordict = color_to_colordict(color,
                                       textdict.keys(),
                                       default=self.settings.get('color.vertex'),
                                       colorformat='rgb',
                                       normalize=False)
        labels = []
        for key, text in iter(textdict.items()):
            x, y = self.force.vertex_attributes(key, 'xy')
            labels.append({
                'pos': [dx + (x - dx) / self.scale, dy + (y - dy) / self.scale, 0],
                'name': "{}.vertex.label.{}".format(self.force.name, key),
                'color': colordict[key],
                'text': textdict[key]
            })
        return compas_rhino.draw_labels(labels, layer=self.layer, clear=False, redraw=True)

    def draw_edges(self, keys=None, color=None):
        anchor = self.force.anchor()
        dx, dy = self.force.vertex_coordinates(anchor, 'xy')
        keys = keys or list(self.force.edges())
        colordict = color_to_colordict(color,
                                       keys,
                                       default=self.settings.get('color.edge'),
                                       colorformat='rgb',
                                       normalize=False)
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
        return compas_rhino.draw_lines(lines, layer=self.layer, clear=False, redraw=True)

    def draw_edgelabels(self, text=None, color=None):
        anchor = self.force.anchor()
        dx, dy = self.force.vertex_coordinates(anchor, 'xy')
        if text is None:
            textdict = {(u, v): "{}-{}".format(u, v) for u, v in self.force.edges()}
        elif isinstance(text, dict):
            textdict = text
        else:
            raise NotImplementedError
        colordict = color_to_colordict(color,
                                       textdict.keys(),
                                       default=self.settings.get('color.edge'),
                                       colorformat='rgb',
                                       normalize=False)
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
        return compas_rhino.draw_labels(labels, layer=self.layer, clear=False, redraw=True)

    def draw_faces(self, keys=None, color=None, join_faces=False):
        anchor = self.force.anchor()
        dx, dy = self.force.vertex_coordinates(anchor, 'xy')
        keys = keys or list(self.force.faces())
        colordict = color_to_colordict(color,
                                       keys,
                                       default=self.settings.get('color.face'),
                                       colorformat='rgb',
                                       normalize=False)
        faces = []
        for fkey in keys:
            points = self.force.face_coordinates(fkey)
            scaled_points = [[dx + (pt[0] - dx) / self.scale, dy + (pt[1] - dy) / self.scale, 0] for pt in points]
            faces.append({
                'points': scaled_points,
                'name': "{}.face.{}".format(self.force.name, fkey),
                'color': colordict[fkey],
            })

        guids = compas_rhino.draw_faces(faces, layer=self.layer, clear=False, redraw=True)

        if join_faces:
            guid = rs.JoinMeshes(guids, delete_input=True)
            rs.ObjectLayer(guid, self.layer)
            rs.ObjectName(guid, '{}.mesh'.format(self.force.name))
            if color:
                rs.ObjectColor(guid, color)


    def draw_scale_facelabels(self, text=None, color=None):
        anchor = self.force.anchor()
        dx = self.force.vertex_coordinates(anchor)[0]
        dy = self.force.vertex_coordinates(anchor)[1]

        if text is None:
            textdict = {key: str(key) for key in self.force.faces()}
        elif isinstance(text, dict):
            textdict = text
        else:
            raise NotImplementedError

        colordict = color_to_colordict(color,
                                       textdict.keys(),
                                       default=self.settings.get('color.face'),
                                       colorformat='rgb',
                                       normalize=False)

        labels = []
        for key, text in iter(textdict.items()):
            cen_pt = self.force.face_center(key)
            labels.append({
                'pos': [dx + (cen_pt[0] - dx) / self.scale, dy + (cen_pt[1] - dy) / self.scale, 0],
                'name': "{}.face.label.{}".format(self.force.name, key),
                'color': colordict[key],
                'text': textdict[key],
            })

        return compas_rhino.draw_labels(labels, layer=self.layer, clear=False, redraw=True)


    def scale_diagram(self, scale):
        # TO BE DELETED?
        # be careful to use... this modify the force diagram, instead of just drawing
        x = self.force.vertices_attribute('x')
        y = self.force.vertices_attribute('y')
        anchor = self.force.anchor()
        dx = self.force.vertex_coordinates(anchor)[0]
        dy = self.force.vertex_coordinates(anchor)[1]

        for vkey, attr in self.force.vertices(True):
            attr['x'] = dx + (attr['x'] - dx) / scale
            attr['y'] = dy + (attr['y'] - dy) / scale


    def clear_anchor_vertex(self):
        compas_rhino.delete_objects_by_name(name='{}.anchor_vertex.*'.format(self.force.name))


    def draw_anchor_vertex(self, color=None):
        self.clear_anchor_vertex()
        anchor = self.force.anchor()
        self.clear_vertexlabels(keys=[anchor])
        labels = []
        labels.append({
            'pos'  : self.force.vertex_coordinates(anchor),
            'text' : str(anchor),
            'color': color or self.settings.get('color.anchor'),
            'name' : "{}.anchor_vertex.{}".format(self.force.name, anchor)
        })
        compas_rhino.draw_labels(labels, layer=self.layer, clear=False, redraw=True)


    def update_edge_force(self):
        (u, v) = list(self.force.edges())[0] # get an edge
        # check whether the force diagram is scaled already
        if self.force.edge_attribute((u, v), 'force') is None:
            self.force.update_default_edge_attributes({'force': 0.0})
            for i, ((u, v), attr) in enumerate(self.force.edges(data=True)):
                length = self.force.edge_length(u, v)
                length = round(length, 2)
                attr['force'] = length
        else:  # TO CHECK???!!
            for i, ((u, v), attr) in enumerate(self.force.edges(data=True)):
                length = self.force.edge_length(u, v)
                length = round(length, 2)
                attr['force'] = length

    def draw_edge_force(self, draw=True):
        force_dict = {}
        c_dict  = {}
        max_length = 0

        for i, ((u, v), attr) in enumerate(self.force.edges(data=True)):
            length = attr['force']
            if length > max_length:
                max_length = length
            force_dict[(u, v)] = length

        for i, (u, v) in enumerate(self.force.edges()):
            value = force_dict[(u, v)] / max_length
            c_dict[(u, v)] = i_to_rgb(value)

        if draw is True:
            self.draw_scale_edgelabels(text=dict((v,"%s kN" % k) for v, k in force_dict.items()), color=c_dict)
        return c_dict


    def clear_independent_edge(self):
        compas_rhino.delete_objects_by_name(name='{}.independent_edge.*'.format(self.force.name))


    def draw_independent_edges(self):
        self.clear_independent_edge()
        if self.form is None:
            raise "form diagram doesn't exist"
        else:
            indices = find_force_ind(self.form, self.force)

        anchor = self.force.anchor()
        dx = self.force.vertex_coordinates(anchor)[0]
        dy = self.force.vertex_coordinates(anchor)[1]

        lines = []
        for index, ((u, v), attr) in enumerate(self.force.edges(True)):
            if (u, v) in indices:
                u_x = self.force.vertex_coordinates(u)[0]
                u_y = self.force.vertex_coordinates(u)[1]
                v_x = self.force.vertex_coordinates(v)[0]
                v_y = self.force.vertex_coordinates(v)[1]
                lines.append({
                    'start': [dx + (u_x - dx) / self.scale, dy + (u_y - dy) / self.scale, 0],
                    'end': [dx + (v_x - dx) / self.scale, dy + (v_y - dy) / self.scale, 0],
                    'name': "{}.independent_edge.{}".format(self.force.name, index),
                    'width': 1.0
                })
        return compas_rhino.draw_lines(lines, layer=self.layer, clear=False, redraw=True)


# ==============================================================================
# Main
# ==============================================================================

if __name__ == "__main__":
    pass
