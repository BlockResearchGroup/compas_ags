from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

from compas_ags.rhino.diagramobject import DiagramObject
from compas_ags.rhino.forceinspector import ForceDiagramVertexInspector
from compas_ags.utilities import calculate_drawingscale


__all__ = ['ForceObject']


class ForceObject(DiagramObject):
    """A force object represents a force diagram in the Rhino view.
    """

    SETTINGS = {
        'show.vertices': True,
        'show.edges': True,
        'show.faces': False,
        'show.vertexlabels': False,
        'show.edgelabels': False,
        'show.facelabels': False,
        'show.forcecolors': True,
        'show.forcelabels': True,

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
            color = {}
            color.update({vertex: self.settings['color.vertices'] for vertex in self.diagram.vertices()})
            color.update({vertex: self.settings['color.vertices:is_fixed'] for vertex in self.diagram.vertices_where({'is_fixed': True})})

            self.artist.draw_vertices(color=color)

        # edges
        if self.settings['show.edges']:
            color = {}
            color.update({edge: self.settings['color.edges'] for edge in self.diagram.edges()})
            color.update({edge: self.settings['color.edges:is_external'] for edge in self.diagram.edges_where_dual({'is_external': True})})
            color.update({edge: self.settings['color.edges:is_load'] for edge in self.diagram.edges_where_dual({'is_load': True})})
            color.update({edge: self.settings['color.edges:is_reaction'] for edge in self.diagram.edges_where_dual({'is_reaction': True})})
            color.update({edge: self.settings['color.edges:is_ind'] for edge in self.diagram.edges_where_dual({'is_ind': True})})

            # force colors
            if self.settings['show.forcecolors']:
                tol = self.settings['tol.forces']
                for edge in self.diagram.edges_where_dual({'is_external': False}):
                    if self.diagram.dual_edge_f(edge) > + tol:
                        color[edge] = self.settings['color.tension']
                    elif self.diagram.dual_edge_f(edge) < - tol:
                        color[edge] = self.settings['color.compression']

            self.artist.draw_edges(color=color)

        # vertex labels
        if self.settings['show.vertexlabels']:
            text = {vertex: index for index, vertex in enumerate(self.diagram.vertices())}
            color = {}
            color.update({vertex: self.settings['color.vertexlabels'] for vertex in self.diagram.vertices()})
            color.update({vertex: self.settings['color.vertices:is_fixed'] for vertex in self.diagram.vertices_where({'is_fixed': True})})

            self.artist.draw_vertexlabels(text=text, color=color)

        # edge labels
        if self.settings['show.edgelabels']:
            edge_index = self.diagram.edge_index(self.diagram.dual)
            edge_index.update({(v, u): index for (u, v), index in edge_index.items()})
            text = {edge: edge_index[edge] for edge in self.diagram.edges()}
            color = {}
            color.update({edge: self.settings['color.edges'] for edge in self.diagram.edges()})
            color.update({edge: self.settings['color.edges:is_external'] for edge in self.diagram.edges_where_dual({'is_external': True})})
            color.update({edge: self.settings['color.edges:is_load'] for edge in self.diagram.edges_where_dual({'is_load': True})})
            color.update({edge: self.settings['color.edges:is_reaction'] for edge in self.diagram.edges_where_dual({'is_reaction': True})})
            color.update({edge: self.settings['color.edges:is_ind'] for edge in self.diagram.edges_where_dual({'is_ind': True})})

            # force colors
            if self.settings['show.forcecolors']:
                tol = self.settings['tol.forces']
                for edge in self.diagram.edges_where_dual({'is_external': False}):
                    if self.diagram.dual_edge_f(edge) > + tol:
                        color[edge] = self.settings['color.tension']
                    elif self.diagram.dual_edge_f(edge) < - tol:
                        color[edge] = self.settings['color.compression']

            self.artist.draw_edgelabels(text=text, color=color)

        # force labels
        if self.settings['show.forcelabels']:
            text = {}
            dual_edges = list(self.diagram.dual.edges())
            for index, (u, v) in enumerate(self.diagram.ordered_edges(self.diagram.dual)):
                f = self.diagram.dual.edge_attribute(dual_edges[index], 'f')
                if (u, v) in self.diagram.edges():
                    text[(u, v)] = "%s kN" % (round(abs(f), 1))
                else:
                    text[(v, u)] = "%s kN" % (round(abs(f), 1))

            color = {}
            color.update({edge: self.settings['color.edges'] for edge in self.diagram.edges()})
            color.update({edge: self.settings['color.edges:is_external'] for edge in self.diagram.edges_where_dual({'is_external': True})})
            color.update({edge: self.settings['color.edges:is_load'] for edge in self.diagram.edges_where_dual({'is_load': True})})
            color.update({edge: self.settings['color.edges:is_reaction'] for edge in self.diagram.edges_where_dual({'is_reaction': True})})
            color.update({edge: self.settings['color.edges:is_ind'] for edge in self.diagram.edges_where_dual({'is_ind': True})})

            # force colors
            if self.settings['show.forcecolors']:
                tol = self.settings['tol.forces']
                for edge in self.diagram.edges_where_dual({'is_external': False}):
                    if self.diagram.dual_edge_f(edge) > + tol:
                        color[edge] = self.settings['color.tension']
                    elif self.diagram.dual_edge_f(edge) < - tol:
                        color[edge] = self.settings['color.compression']

            self.artist.draw_edgelabels(text=text, color=color)

        self.redraw()


# ==============================================================================
# Main
# ==============================================================================

if __name__ == '__main__':

    pass
