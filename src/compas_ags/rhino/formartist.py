from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

# from math import fabs

import compas_rhino
# from compas.geometry import scale_vector
# from compas.geometry import add_vectors
# from compas.utilities import i_to_green

from compas_rhino.artists import MeshArtist


__all__ = ['FormArtist']


class FormArtist(MeshArtist):
    """Artist for form diagram in AGS.

    Parameters
    ----------
    form : :class:`compas_ags.diagrams.FormDiagram`
        The form diagram to draw.
    layer: string, optional
        The name of the layer that will contain the formdiagram.
        Default is ``None``.

    Attributes
    ----------
    form : :class:`compas_ags.diagrams.FormDiagram`
    settings : dict
        Visualisation settings.
    guids : dict
        GUIDs of Rhino objects created by the artists.

    Notes
    -----
    The artist keeps track of the Rhino objects it creates in ``self.guids``.
    The artist iterates over the edges of the form diagram to collect drawing information.
    The edge generator of the form diagram excludes edges where ``'is_edge' is False``.
    """

    def __init__(self, form, settings=None, **kwargs):
        super(FormArtist, self).__init__(form, **kwargs)
        self.settings.update({
            'show.vertices': True,
            'show.edges': True,
            'show.faces': False,
            'show.vertexlabels': True,
            'show.edgelabels': False,
            'show.facelabels': False,
            'color.vertices': (255, 255, 255),
            'color.vertices:is_fixed': (255, 0, 0),
            'color.edges': (0, 0, 0),
            'color.edges:is_ind': (255, 255, 255),
            'color.edges:is_external': (0, 255, 0),
            'color.faces': (210, 210, 210),
            'color.reactions': (0, 255, 0),
            'color.residuals': (0, 255, 255),
            'color.loads': (0, 255, 0),
            'color.selfweight': (0, 0, 255),
            'color.forces': (0, 0, 255),
            'color.compression': (0, 0, 255),
            'color.tension': (255, 0, 0),
            'scale.reaction': 1.0,
            'scale.residual': 1.0,
            'scale.load': 1.0,
            'scale.force': 1.0,
            'scale.selfweight': 1.0,
            'tol.reaction': 1e-3,
            'tol.residual': 1e-3,
            'tol.load': 1e-3,
            'tol.force': 1e-3,
            'tol.selfweight': 1e-3,
        })
        if settings:
            self.settings.update(settings)
        self.guids = {}

    @property
    def form(self):
        """The form diagram assigned to the artist."""
        return self.mesh

    @form.setter
    def form(self, form):
        self.mesh = form

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
        """Draw the form diagram.

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

        if self.settings['show.vertices']:
            color = {}
            color.update({vertex: self.settings['color.vertices'] for vertex in self.form.vertices()})
            guids = self.draw_vertices(color=color)
            self.guids['vertices'] = dict(zip(self.form.vertices(), guids))

        if self.settings['show.vertexlabels']:
            guids = self.draw_vertexlabels()
            self.guids['vertexlabels'] = dict(zip(self.form.vertices(), guids))

        if self.settings['show.edges']:
            color = {}
            color.update({edge: self.settings['color.edges'] for edge in self.form.edges()})
            color.update({edge: self.settings['color.edges:is_external'] for edge in self.form.external()})
            color.update({edge: self.settings['color.edges:is_ind'] for edge in self.form.edges_where({'is_ind': True})})
            guids = self.draw_edges(color=color)
            self.guids['edges'] = dict(zip(self.form.edges(), guids))

        if self.settings['show.edgelabels']:
            text = {edge: index for index, edge in enumerate(self.form.edges())}
            color.update({edge: self.settings['color.edges'] for edge in self.form.edges()})
            color.update({edge: self.settings['color.edges:is_external'] for edge in self.form.external()})
            color.update({edge: self.settings['color.edges:is_ind'] for edge in self.form.edges_where({'is_ind': True})})
            guids = self.draw_edgelabels(text=text, color=color)
            self.guids['edgelabels'] = dict(zip(self.form.edges(), guids))

    # def draw_external(self, arrow=False, scale=1.0):
    #     """Draw the symbols for the external forces as an overlay of the edges.

    #     An external force has a point of application,
    #     a line of action, direction, and magnitude.

    #     Parameters
    #     ----------
    #     color : rgb color, optional
    #         RGB color specification.
    #         The default value is in ``FormArtist.settings['color.external']``.
    #     arrow : bool, optional
    #         Add an arrow.
    #         Default is ``False``.
    #     scale : float, optional
    #         The length of the line representing the force symbol.
    #         Default is ``1.0``.

    #     Returns
    #     -------
    #     None

    #     Notes
    #     -----
    #     The GUIDs of the Rhino objects created by this method
    #     are stored in ``FormArtist.guids['external']``.
    #     """
    #     compas_rhino.delete_objects(self.guids.setdefault('external'))
    #     leaves = set(self.form.leaves())
    #     lines = []
    #     for u, v in self.form.edges():
    #         if u not in leaves and v not in leaves:
    #             continue
    #         lines.append({
    #             'start': self.form.vertex_coordinates(u),
    #             'end': self.form.vertex_coordinates(v),
    #             'arrow': 'end' if arrow else None,
    #             'color': color or self.settings.get('color.external'),
    #             'name': "{}.external.{}-{}".format(self.form.name, u, v),
    #             'width': 0.5
    #         })
    #     self.guids['external'] = compas_rhino.draw_lines(lines, layer=self.layer, clear=False, redraw=False)

    # def draw_loads(self, scale=None, color=None):
    #     """Draw the symbols for the loads as an overlay of the edges.

    #     A load has a point of application, a line of action, direction, and magnitude.
    #     The magnitude of the symbol is controlled by the scale factor.
    #     The magnitude of the actual load is stored as an editable edge attribute.

    #     Parameters
    #     ----------
    #     color : rgb color, optional
    #         RGB color specification.
    #         The default value is in ``FormArtist.settings['color.external']``.
    #     arrow : bool, optional
    #         Add an arrow.
    #         Default is ``False``.
    #     scale : float, optional
    #         The length of the line representing the force symbol.
    #         Default is ``1.0``.

    #     Returns
    #     -------
    #     None

    #     Notes
    #     -----
    #     The GUIDs of the Rhino objects created by this method
    #     are stored in ``FormArtist.guids['external']``.
    #     """
    #     compas_rhino.delete_objects(self.guids.setdefault('loads'))
    #     lines = []
    #     color = color or self.settings['color.load']
    #     scale = scale or self.settings['scale.load']
    #     tol = self.settings['tol.load']
    #     tol2 = tol ** 2
    #     for key, attr in self.form.vertices_where({'is_anchor': False, 'is_external': False}, True):
    #         px = scale * attr['px']
    #         py = scale * attr['py']
    #         pz = scale * attr['pz']
    #         if px ** 2 + py ** 2 + pz ** 2 < tol2:
    #             continue
    #         sp = self.form.vertex_coordinates(key)
    #         ep = sp[0] + px, sp[1] + py, sp[2] + pz
    #         lines.append({
    #             'start': sp,
    #             'end': ep,
    #             'color': color,
    #             'arrow': 'end',
    #             'name': "{}.load.{}".format(self.form.name, key)
    #         })
    #     self.guids['loads'] = compas_rhino.draw_lines(lines, layer=self.layer, clear=False, redraw=False)

    # # def draw_independent_edges(self):
    # #     compas_rhino.delete_objects(self.guids.setdefault('independent_edges'))
    # #     lines = []
    # #     for index, (u, v) in enumerate(self.form.edges_where({'is_ind': True})):
    # #         lines.append({
    # #             'start': self.form.vertex_coordinates(u),
    # #             'end': self.form.vertex_coordinates(v),
    # #             'name': "{}.independent_edge.{}".format(self.form.name, index),
    # #             'width': 1.0
    # #         })
    # #     self.guids['independent_edges'] = compas_rhino.draw_lines(lines, layer=self.layer, clear=False, redraw=False)

    # # def draw_fixed_vertices(self, color=None):
    # #     compas_rhino.delete_objects(self.guids.setdefault('fixed_vertices'))
    # #     labels = []
    # #     for vkey in self.form.fixed():
    # #         labels.append({
    # #             'pos'  : self.form.vertex_coordinates(vkey),
    # #             'text' : str(vkey),
    # #             'color': color or self.settings.get('color.fix'),
    # #             'name' : "{}.fixed_vertex.{}".format(self.form.name, vkey)
    # #         })
    # #     self.guids['fixed_vertices'] = compas_rhino.draw_labels(labels, layer=self.layer, clear=False, redraw=False)

    # def draw_selfweight(self, scale=None, color=None):
    #     compas_rhino.delete_objects(self.guids.setdefault('selfweight'))
    #     lines = []
    #     color = color or self.settings['color.selfweight']
    #     scale = scale or self.settings['scale.selfweight']
    #     tol = self.settings['tol.selfweight']
    #     tol2 = tol ** 2
    #     for key, attr in self.form.vertices_where({'is_anchor': False, 'is_external': False}, True):
    #         t = attr['t']
    #         a = self.form.vertex_area(key)
    #         sp = self.form.vertex_coordinates(key)
    #         dz = scale * t * a
    #         if dz ** 2 < tol2:
    #             continue
    #         ep = sp[0], sp[1], sp[2] - dz
    #         lines.append({
    #             'start': sp,
    #             'end': ep,
    #             'color': color,
    #             'arrow': 'end',
    #             'name': "{}.selfweight.{}".format(self.form.name, key)
    #         })
    #     self.guids['selfweight'] = compas_rhino.draw_lines(lines, layer=self.layer, clear=False, redraw=False)

    # def draw_reactions(self, scale=None, color=None):
    #     """Draw the resultant of the external forces at an anchored node.

    #     No arrows are added to the lines.
    #     GUIDs of the Rhino objects created by this method are stored in ``FormArtist.guids['reactions']``.

    #     Parameters
    #     ----------
    #     scale : float, optional
    #         The scale factor for the resultant.
    #         Default is in ``FormArtist.settings['scale.reaction']``.
    #     color : rgb color, optional
    #         RGB color specification.
    #         The default value is in ``FormArtist.settings['color.external']``.

    #     Returns
    #     -------
    #     None
    #     """
    #     compas_rhino.delete_objects(self.guids.setdefault('reactions'))
    #     lines = []
    #     color = color or self.settings['color.reaction']
    #     scale = scale or self.settings['scale.reaction']
    #     tol = self.settings['tol.reaction']
    #     tol2 = tol ** 2
    #     for key in self.form.vertices_where({'is_anchor': True}):
    #         rx = 0
    #         ry = 0
    #         for nbr in self.form.vertex_neighbors(key):
    #             if not self.form.edge_attribute((key, nbr), 'is_external'):
    #                 continue
    #             f = self.form.edge_attribute((key, nbr), 'f')
    #             u = self.form.edge_direction(key, nbr)
    #             rx += u[0] * f
    #             ry += u[1] * f
    #         rx = scale * rx
    #         ry = scale * ry
    #         sp = self.form.vertex_coordinates(key)
    #         if rx ** 2 + ry ** 2 > tol2:
    #             ep = sp[0] + rx, sp[1] + ry, sp[2]
    #             lines.append({
    #                 'start': sp,
    #                 'end': ep,
    #                 'color': color,
    #                 'arrow': None,
    #                 'name': "{}.reaction.{}".format(self.form.name, key)
    #             })
    #     self.guids['reactions'] = compas_rhino.draw_lines(lines, layer=self.layer, clear=False, redraw=False)

    # def draw_forces(self, scale=None, color=None):
    #     compas_rhino.delete_objects(self.guids.setdefault('forces'))
    #     lines = []
    #     color_compression = color or self.settings['color.compression']
    #     color_tension = color or self.settings['color.tension']
    #     scale = scale or self.settings['scale.force']
    #     tol = self.settings['tol.force']
    #     leaves = set(self.form.leaves())
    #     for (u, v) in self.form.edges():
    #         if u not in leaves and v not in leaves:
    #             sp, ep = self.form.edge_coordinates(u, v)
    #             f = self.form.edge_attribute((u, v), 'f')
    #             radius = fabs(scale * f)
    #             if radius < tol:
    #                 continue
    #             color = color_compression if f > 0 else color_tension
    #             lines.append({
    #                 'start': sp,
    #                 'end': ep,
    #                 'radius': radius,
    #                 'color': color,
    #                 'name': "{}.force.{}-{}".format(self.form.name, u, v)
    #             })
    #     self.guids['forces'] = compas_rhino.draw_cylinders(lines, layer=self.layer, clear=False, redraw=True)

    # def draw_residuals(self, scale=None, color=None):
    #     compas_rhino.delete_objects(self.guids.setdefault('residuals'))
    #     lines = []
    #     color = color or self.settings['color.residual']
    #     scale = scale or self.settings['scale.residual']
    #     tol = self.settings['tol.residual']
    #     for key in self.form.vertices_where({'is_anchor': False, 'is_external': False}):
    #         r = self.form.vertex_attributes(key, ['_rx', '_ry', '_rz'])
    #         r[:] = scale_vector(r, scale)
    #         if length_vector(r) < tol:
    #             continue
    #         sp = self.form.vertex_coordinates(key)
    #         ep = add_vectors(sp, r)
    #         lines.append({
    #             'start': sp,
    #             'end': ep,
    #             'color': color,
    #             'arrow': 'start',
    #             'name': "{}.residual.{}".format(self.form.name, key)
    #         })
    #     self.guids['residuals'] = compas_rhino.draw_lines(lines, layer=self.layer, clear=False, redraw=False)

    # def draw_angles(self, tol=5.0):
    #     """Draw labels with the angle deviation between corresponding edges of form and force.

    #     The label is drawn at the midpoint of the form diagram edges.
    #     GUIDs of Rhino objects created by this method are stored in ``FormArtist.guids['angles']``.

    #     Parameters
    #     ----------
    #     tol : float, optional
    #         Angles below this value are excluded from the labels.
    #         Default is ``5.0``.

    #     Returns
    #     -------
    #     None
    #     """
    #     compas_rhino.delete_objects(self.guids.setdefault('angles'))
    #     a_max = tol if tol else max(self.form.edges_attribute('a'))
    #     a_min = 0
    #     a_range = a_max - a_min
    #     if a_range:
    #         labels = []
    #         for (u, v) in self.form.edges():
    #             a = self.form.edge_attribute((u, v), 'a')
    #             a_deg = 180 * a / 3.14159
    #             if a_deg > tol:
    #                 labels.append({
    #                     'pos': self.form.edge_midpoint(u, v),
    #                     'text': "{:.0f}".format(a_deg),
    #                     'color': i_to_green((a - a_min) / a_range),
    #                     'name': "{}.angle.{}-{}".format(self.form.name, u, v)
    #                 })
    #         self.guids['angles'] = compas_rhino.draw_labels(labels, layer=self.layer, clear=False, redraw=False)


# ==============================================================================
# Main
# ==============================================================================

if __name__ == "__main__":
    pass
