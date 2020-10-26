from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

from compas_ags.rhino.diagramobject import DiagramObject
from compas_ags.rhino.forceinspector import ForceDiagramVertexInspector


__all__ = ['ForceObject']


class ForceObject(DiagramObject):
    """A force object represents a force diagram in the Rhino view.
    """

    SETTINGS = {
        'show.vertices': True,
        'show.edges': True,
        'show.vertexlabels': False,
        'show.edgelabels': False,
        'show.forcelabels': False,
        'show.forcecolors': True,

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

        'tol.forces': 1e-3,
    }

    def __init__(self, diagram, *args, **kwargs):
        super(ForceObject, self).__init__(diagram, *args, **kwargs)
        self.settings.update(ForceObject.SETTINGS)
        settings = kwargs.get('settings') or {}
        if settings:
            self.settings.update(settings)
        self._inspector = None

    @property
    def inspector(self):
        """:class:`compas_ags.rhino.ForceDiagramInspector`: An inspector conduit."""
        if not self._inspector:
            self._inspector = ForceDiagramVertexInspector(self.diagram)
        return self._inspector

    def inspector_on(self, form):
        self.inspector.form_vertex_xyz = form.artist.vertex_xyz
        self.inspector.force_vertex_xyz = self.artist.vertex_xyz
        self.inspector.enable()

    def inspector_off(self):
        self.inspector.disable()

    def draw(self):
        """Draw the diagram.

        The visible components, display properties and visual style of the diagram
        can be fully customised using the configuration items in the settings dict.

        The method will clear the drawing layer and any objects it has drawn in a previous call,
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
            tol = self.settings['tol.forces']
            edges = [edge for edge in self.diagram.edges() if self.diagram.edge_length(*edge) > tol]
            color = {}
            color.update({edge: self.settings['color.edges'] for edge in edges})
            color.update({edge: self.settings['color.edges:is_external'] for edge in self.diagram.edges_where_dual({'is_external': True})})
            color.update({edge: self.settings['color.edges:is_load'] for edge in self.diagram.edges_where_dual({'is_load': True})})
            color.update({edge: self.settings['color.edges:is_reaction'] for edge in self.diagram.edges_where_dual({'is_reaction': True})})
            color.update({edge: self.settings['color.edges:is_ind'] for edge in self.diagram.edges_where_dual({'is_ind': True})})

            # force colors
            if self.settings['show.forcecolors']:
                tol = self.settings['tol.forces']
                for edge in self.diagram.edges_where_dual({'is_external': False}):
                    if self.diagram.dual_edge_force(edge) > + tol:
                        color[edge] = self.settings['color.tension']
                    elif self.diagram.dual_edge_force(edge) < - tol:
                        color[edge] = self.settings['color.compression']

            guids = self.artist.draw_edges(edges=edges, color=color)
            self.guid_edge = zip(guids, edges)

            guid_edgelabel = []

            # edge labels
            if self.settings['show.edgelabels']:
                edge_index = self.diagram.edge_index(self.diagram.dual)
                edge_index.update({(v, u): index for (u, v), index in edge_index.items()})
                text = {edge: edge_index[edge] for edge in edges}
                color = {}
                color.update({edge: self.settings['color.edges'] for edge in edges})
                color.update({edge: self.settings['color.edges:is_external'] for edge in self.diagram.edges_where_dual({'is_external': True})})
                color.update({edge: self.settings['color.edges:is_load'] for edge in self.diagram.edges_where_dual({'is_load': True})})
                color.update({edge: self.settings['color.edges:is_reaction'] for edge in self.diagram.edges_where_dual({'is_reaction': True})})
                color.update({edge: self.settings['color.edges:is_ind'] for edge in self.diagram.edges_where_dual({'is_ind': True})})

                # force colors
                if self.settings['show.forcecolors']:
                    tol = self.settings['tol.forces']
                    for edge in self.diagram.edges_where_dual({'is_external': False}):
                        if self.diagram.dual_edge_force(edge) > + tol:
                            color[edge] = self.settings['color.tension']
                        elif self.diagram.dual_edge_force(edge) < - tol:
                            color[edge] = self.settings['color.compression']

                guids = self.artist.draw_edgelabels(text=text, color=color)
                guid_edgelabel += zip(guids, edges)

            # force labels
            if self.settings['show.forcelabels']:
                text = {}
                for edge in edges:
                    f = self.diagram.dual_edge_force(edge)
                    text[edge] = "{:.4g}kN".format(abs(f))

                color = {}
                color.update({edge: self.settings['color.edges'] for edge in edges})
                color.update({edge: self.settings['color.edges:is_external'] for edge in self.diagram.edges_where_dual({'is_external': True})})
                color.update({edge: self.settings['color.edges:is_load'] for edge in self.diagram.edges_where_dual({'is_load': True})})
                color.update({edge: self.settings['color.edges:is_reaction'] for edge in self.diagram.edges_where_dual({'is_reaction': True})})
                color.update({edge: self.settings['color.edges:is_ind'] for edge in self.diagram.edges_where_dual({'is_ind': True})})

                # force colors
                if self.settings['show.forcecolors']:
                    tol = self.settings['tol.forces']
                    for edge in self.diagram.edges_where_dual({'is_external': False}):
                        if self.diagram.dual_edge_force(edge) > + tol:
                            color[edge] = self.settings['color.tension']
                        elif self.diagram.dual_edge_force(edge) < - tol:
                            color[edge] = self.settings['color.compression']

                guids = self.artist.draw_edgelabels(text=text, color=color)

                guid_edgelabel += zip(guids, edges)

            self.guid_edgelabel = guid_edgelabel

        self.redraw()

    def draw_highlight_edge(self, edge):

        if not self.diagram.has_edge(edge):
            edge = edge[1], edge[0]

        f = self.diagram.dual_edge_force(edge)

        text = {edge: "{:.4g}kN".format(abs(f))}
        color = {}
        color[edge] = self.settings['color.edges']

        if edge in self.diagram.edges_where_dual({'is_external': True}):
            color[edge] = self.settings['color.edges:is_external']
        if edge in self.diagram.edges_where_dual({'is_load': True}):
            color[edge] = self.settings['color.edges:is_load']
        if edge in self.diagram.edges_where_dual({'is_reaction': True}):
            color[edge] = self.settings['color.edges:is_reaction']
        if edge in self.diagram.edges_where_dual({'is_ind': True}):
            color[edge] = self.settings['color.edges:is_ind']

        tol = self.settings['tol.forces']
        if edge in self.diagram.edges_where_dual({'is_external': False}):
            if f > + tol:
                color[edge] = self.settings['color.tension']
            elif f < - tol:
                color[edge] = self.settings['color.compression']

        guid_edgelabel = self.artist.draw_edgelabels(text=text, color=color)
        self.guid_edgelabel = zip(guid_edgelabel, edge)

        self.redraw()
