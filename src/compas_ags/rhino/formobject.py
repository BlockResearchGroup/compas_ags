from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

import compas_rhino
from compas_ags.rhino.diagramobject import DiagramObject
from compas_ags.rhino.forminspector import FormDiagramVertexInspector


__all__ = ['FormObject']


class FormObject(DiagramObject):
    """A form object represents a form diagram in the Rhino model space.
    """

    SETTINGS = {
        'show.vertices': True,
        'show.edges': True,
        'show.vertexlabels': False,
        'show.edgelabels': False,
        'show.forcecolors': True,
        'show.forcelabels': True,
        'show.forcepipes': False,

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

        'scale.forces': None,

        'tol.edges': 1e-3,
        'tol.forces': 1e-3,
    }

    def __init__(self, diagram, *args, **kwargs):
        super(FormObject, self).__init__(diagram, *args, **kwargs)
        self.settings.update(FormObject.SETTINGS)
        settings = kwargs.get('settings') or {}
        if settings:
            self.settings.update(settings)
        self._guid_force = {}
        self._inspector = None

    @property
    def inspector(self):
        """:class:`compas_ags.rhino.FormDiagramInspector`: An inspector conduit."""
        if not self._inspector:
            self._inspector = FormDiagramVertexInspector(self.diagram)
        return self._inspector

    def inspector_on(self, force):
        self.inspector.force_vertex_xyz = force.artist.vertex_xyz
        self.inspector.form_vertex_xyz = self.artist.vertex_xyz
        self.inspector.enable()

    def inspector_off(self):
        self.inspector.disable()

    @property
    def guids(self):
        guids = super(FormObject, self).guids
        guids += list(self.guid_force.keys())
        return guids

    @property
    def guid_force(self):
        """Map between Rhino object GUIDs and form diagram edge force identifiers."""
        return self._guid_force

    @guid_force.setter
    def guid_force(self, values):
        self._guid_force = dict(values)

    def clear(self):
        super(FormObject, self).clear()
        compas_rhino.delete_objects(self.guids, purge=True)
        self._guid_force = {}

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
        if not self.visible:
            return

        self.artist.vertex_xyz = self.vertex_xyz

        # vertices
        if self.settings['show.vertices']:
            vertices = list(self.diagram.vertices())
            color = {}
            color.update({vertex: self.settings['color.vertices'] for vertex in vertices})
            color.update({vertex: self.settings['color.vertices:is_fixed'] for vertex in self.diagram.vertices_where({'is_fixed': True})})
            guids = self.artist.draw_vertices(color=color)
            self.guid_vertex = zip(guids, vertices)

            # vertex labels
            if self.settings['show.vertexlabels']:
                text = {vertex: index for index, vertex in enumerate(vertices)}
                color = {}
                color.update({vertex: self.settings['color.vertexlabels'] for vertex in vertices})
                color.update({vertex: self.settings['color.vertices:is_fixed'] for vertex in self.diagram.vertices_where({'is_fixed': True})})
                guids = self.artist.draw_vertexlabels(text=text, color=color)
                self.guid_vertexlabel = zip(guids, vertices)

        # edges
        if self.settings['show.edges']:
            edges = list(self.diagram.edges())
            color = {}
            color.update({edge: self.settings['color.edges'] for edge in edges})
            color.update({edge: self.settings['color.edges:is_external'] for edge in self.diagram.edges_where({'is_external': True})})
            color.update({edge: self.settings['color.edges:is_load'] for edge in self.diagram.edges_where({'is_load': True})})
            color.update({edge: self.settings['color.edges:is_reaction'] for edge in self.diagram.edges_where({'is_reaction': True})})
            color.update({edge: self.settings['color.edges:is_ind'] for edge in self.diagram.edges_where({'is_ind': True})})

            # force colors
            if self.settings['show.forcecolors']:
                tol = self.settings['tol.forces']
                for edge in self.diagram.edges_where({'is_external': False}):
                    if self.diagram.edge_attribute(edge, 'f') > + tol:
                        color[edge] = self.settings['color.tension']
                    elif self.diagram.edge_attribute(edge, 'f') < - tol:
                        color[edge] = self.settings['color.compression']

            guids = self.artist.draw_edges(color=color)
            self.guid_edge = zip(guids, edges)

            guid_edgelabel = []

            # edge labels
            if self.settings['show.edgelabels']:
                text = {edge: index for index, edge in enumerate(edges)}
                color = {}
                color.update({edge: self.settings['color.edges'] for edge in edges})
                color.update({edge: self.settings['color.edges:is_external'] for edge in self.diagram.edges_where({'is_external': True})})
                color.update({edge: self.settings['color.edges:is_load'] for edge in self.diagram.edges_where({'is_load': True})})
                color.update({edge: self.settings['color.edges:is_reaction'] for edge in self.diagram.edges_where({'is_reaction': True})})
                color.update({edge: self.settings['color.edges:is_ind'] for edge in self.diagram.edges_where({'is_ind': True})})

                # force colors
                if self.settings['show.forcecolors']:
                    tol = self.settings['tol.forces']
                    for edge in self.diagram.edges_where({'is_external': False}):
                        if self.diagram.edge_attribute(edge, 'f') > + tol:
                            color[edge] = self.settings['color.tension']
                        elif self.diagram.edge_attribute(edge, 'f') < - tol:
                            color[edge] = self.settings['color.compression']

                guids = self.artist.draw_edgelabels(text=text, color=color)
                guid_edgelabel += zip(guids, edges)

            # force labels
            if self.settings['show.forcelabels']:
                text = {}
                for index, edge in enumerate(self.diagram.edges_where({'is_external': True})):
                    f = self.diagram.edge_attribute(edge, 'f')
                    if f != 0.0:
                        text[edge] = "{:.4g}kN".format(abs(f))
                color = {}
                # color.update({edge: self.settings['color.edges'] for edge in self.diagram.edges()})
                color.update({edge: self.settings['color.edges:is_external'] for edge in self.diagram.edges_where({'is_external': True})})
                color.update({edge: self.settings['color.edges:is_load'] for edge in self.diagram.edges_where({'is_load': True})})
                color.update({edge: self.settings['color.edges:is_reaction'] for edge in self.diagram.edges_where({'is_reaction': True})})
                color.update({edge: self.settings['color.edges:is_ind'] for edge in self.diagram.edges_where({'is_ind': True})})

                # # force colors
                # if self.settings['show.forcecolors']:
                #     tol = self.settings['tol.forces']
                #     for edge in self.diagram.edges_where({'is_external': False}):
                #         if self.diagram.edge_attribute(edge, 'f') > + tol:
                #             color[edge] = self.settings['color.tension']
                #         elif self.diagram.edge_attribute(edge, 'f') < - tol:
                #             color[edge] = self.settings['color.compression']

                guids = self.artist.draw_edgelabels(text=text, color=color)
                guid_edgelabel += zip(guids, edges)

            self.guid_edgelabel = guid_edgelabel

        # force pipes
        if self.settings['show.forcepipes']:
            guids = self.artist.draw_forcepipes(
                color_compression=self.settings['color.compression'],
                color_tension=self.settings['color.tension'],
                scale=self.settings['scale.forces'],
                tol=self.settings['tol.forces'])

            self.guid_force = zip(guids, edges)

        self.redraw()

    def draw_highlight_edge(self, edge):

        f = self.diagram.edge_attribute(edge, 'f')

        text = {edge: "{:.4g}kN".format(abs(f))}
        color = {}
        color[edge] = self.settings['color.edges']

        if self.diagram.edge_attribute(edge, 'is_external'):
            color[edge] = self.settings['color.edges:is_external']
        if self.diagram.edge_attribute(edge, 'is_load'):
            color[edge] = self.settings['color.edges:is_load']
        if self.diagram.edge_attribute(edge, 'is_reaction'):
            color[edge] = self.settings['color.edges:is_reaction']
        if self.diagram.edge_attribute(edge, 'is_ind'):
            color[edge] = self.settings['color.edges:is_ind']

        tol = self.settings['tol.forces']
        for edge in self.diagram.edges_where({'is_external': False}):
            if f > + tol:
                color[edge] = self.settings['color.tension']
            elif f < - tol:
                color[edge] = self.settings['color.compression']

        guid_edgelabel = self.artist.draw_edgelabels(text=text, color=color)
        self.guid_edgelabel = zip(guid_edgelabel, edge)

        self.redraw()
