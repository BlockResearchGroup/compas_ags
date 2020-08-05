from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

from compas_ags.rhino.diagramartist import DiagramArtist


__all__ = ['ForceArtist']


class ForceArtist(DiagramArtist):
    """Artist for force diagrams in AGS.

    Parameters
    ----------
    force: compas_ags.diagrams.ForceDiagram
        The force diagram to draw.
    scale : float, optional
        The drawing scale.
        Default is ``1.0``.
    settings : dict, optional
        Customisation of the artist settings.

    Other Parameters
    ----------------
    See the parent artists for other parameters.

    """

    def __init__(self, force, scale=None, settings=None, **kwargs):
        super(ForceArtist, self).__init__(force, **kwargs)
        self.scale = scale
        self.settings['show.vertexlabels'] = False  # hide vertices in the ForceDiagram
        if settings:
            self.settings.update(settings)

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
        self.clear_layer()
        # vertices
        if self.settings['show.vertices']:
            color = {}
            color.update({vertex: self.settings['color.vertices'] for vertex in self.diagram.vertices()})
            color.update({vertex: self.settings['color.vertices:is_fixed'] for vertex in self.diagram.vertices_where({'is_fixed': True})})
            # color[self.anchor_vertex] = self.settings['color.anchor']
            self.draw_vertices(color=color)
        # edges
        if self.settings['show.edges']:
            color = {}
            color.update({edge: self.settings['color.edges'] for edge in self.diagram.edges()})
            color.update({edge: self.settings['color.edges:is_external'] for edge in self.diagram.edges() if self.diagram.is_dual_edge_external(edge)})
            color.update({edge: self.settings['color.edges:is_load'] for edge in self.diagram.edges() if self.diagram.is_dual_edge_load(edge)})
            color.update({edge: self.settings['color.edges:is_reaction'] for edge in self.diagram.edges() if self.diagram.is_dual_edge_reaction(edge)})
            color.update({edge: self.settings['color.edges:is_ind'] for edge in self.diagram.edges() if self.diagram.is_dual_edge_ind(edge)})
            # forces of the structure
            if self.settings['show.forces']:
                color.update({edge: self.settings['color.tension'] for edge in self.diagram.edges()
                              if self.diagram.dual_edge_f(edge) > 0 and not self.diagram.is_dual_edge_external(edge)})
                color.update({edge: self.settings['color.compression'] for edge in self.diagram.edges()
                              if self.diagram.dual_edge_f(edge) < 0 and not self.diagram.is_dual_edge_external(edge)})
            self.draw_edges(color=color)
        # vertex labels
        if self.settings['show.vertexlabels']:
            text = {vertex: index for index, vertex in enumerate(self.diagram.vertices())}
            color = {}
            color.update({vertex: self.settings['color.vertexlabels'] for vertex in self.diagram.vertices()})
            color.update({vertex: self.settings['color.vertices:is_fixed'] for vertex in self.diagram.vertices_where({'is_fixed': True})})
            # color[self.anchor_vertex] = self.settings['color.anchor']
            self.draw_vertexlabels(text=text, color=color)
        # edge labels
        if self.settings['show.edgelabels']:
            text = {edge: index for index, edge in enumerate(self.diagram.ordered_edges(self.diagram.dual))}
            color = {}
            color.update({edge: self.settings['color.edges'] for edge in self.diagram.edges()})
            color.update({edge: self.settings['color.edges:is_external'] for edge in self.diagram.edges() if self.diagram.is_dual_edge_external(edge)})
            color.update({edge: self.settings['color.edges:is_load'] for edge in self.diagram.edges() if self.diagram.is_dual_edge_load(edge)})
            color.update({edge: self.settings['color.edges:is_reaction'] for edge in self.diagram.edges() if self.diagram.is_dual_edge_reaction(edge)})
            color.update({edge: self.settings['color.edges:is_ind'] for edge in self.diagram.edges() if self.diagram.is_dual_edge_ind(edge)})
            self.draw_edgelabels(text=text, color=color)
        # force magnitude labels
        if self.settings['show.forcelabels']:
            text = {}
            dual_edges = list(self.diagram.dual.edges())
            for index, edge in enumerate(self.diagram.ordered_edges(self.diagram.dual)):
                f = self.diagram.dual.edge_attribute(dual_edges[index], 'f')
                text[edge] = "%s kN {%s}" % (round(f, 2), index)
            color = {}
            color.update({edge: self.settings['color.edges'] for edge in self.diagram.edges()})
            color.update({edge: self.settings['color.edges:is_external'] for edge in self.diagram.edges() if self.diagram.is_dual_edge_external(edge)})
            color.update({edge: self.settings['color.edges:is_load'] for edge in self.diagram.edges() if self.diagram.is_dual_edge_load(edge)})
            color.update({edge: self.settings['color.edges:is_reaction'] for edge in self.diagram.edges() if self.diagram.is_dual_edge_reaction(edge)})
            color.update({edge: self.settings['color.edges:is_ind'] for edge in self.diagram.edges() if self.diagram.is_dual_edge_ind(edge)})
            self.draw_edgelabels(text=text, color=color)


# ==============================================================================
# Main
# ==============================================================================

if __name__ == "__main__":
    pass
