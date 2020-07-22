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
    anchor_point : list
    anchor_vertex : int
    scale : float
        The scale of the diagram.
        The magnitude of force represented by an edge is ``length * scale``.

    """

    def __init__(self, force, form=None, scale=None, layer=None):
        super(ForceArtist, self).__init__(force, layer=layer)
        self._anchor_point = None
        self._anchor_vertex = None
        self._scale = None
        self._form = None
        self.scale = scale
        self.form = form
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
            'color.compression': (0, 0, 255),
            'color.tension': (255, 0, 0)
        })

    @property
    def force(self):
        return self.mesh

    @force.setter
    def force(self, force):
        self.mesh = force

    @property
    def form(self):
        return self._form

    @form.setter
    def form(self, form):
        self._form = form

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

    # def rescale(self):
    #     form_x = self.form.vertices_attribute('x')
    #     form_y = self.form.vertices_attribute('y')
    #     form_xdim = max(form_x) - min(form_x)
    #     form_ydim = max(form_y) - min(form_y)
    #     force_x = self.force.vertices_attribute('x')
    #     force_y = self.force.vertices_attribute('y')
    #     force_xdim = max(force_x) - min(force_x)
    #     force_ydim = max(force_y) - min(force_y)
    #     scale = max([force_xdim / form_xdim, force_ydim / form_ydim])
    #     self._scale = scale
    #     return scale

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
            color.update({vertex: self.settings['color.vertices'] for vertex in self.force.vertices()})
            self.draw_vertices(color=color)
        # edges
        if self.settings['show.edges']:
            color = {}
            color.update({edge: self.settings['color.edges'] for edge in self.force.edges()})
            color.update({edge: self.settings['color.edges:is_external'] for edge in self.force.edges_where({'is_external': True})})
            color.update({edge: self.settings['color.edges:is_ind'] for edge in self.force.edges_where({'is_ind': True})})
            self.draw_edges(color=color)
        # vertex labels
        if self.settings['show.vertexlabels']:
            text = {vertex: index for index, vertex in enumerate(self.force.vertices())}
            color = {}
            color.update({vertex: self.settings['color.vertices'] for vertex in self.force.vertices()})
            self.draw_vertexlabels(text=text, color=color)
        # edge labels
        if self.settings['show.edgelabels']:
            text = {edge: index for index, edge in enumerate(self.force.edges())}
            color = {}
            color.update({edge: self.settings['color.edges'] for edge in self.force.edges()})
            color.update({edge: self.settings['color.edges:is_external'] for edge in self.force.edges_where({'is_external': True})})
            color.update({edge: self.settings['color.edges:is_ind'] for edge in self.force.edges_where({'is_ind': True})})
            self.draw_edgelabels(text=text, color=color)


# ==============================================================================
# Main
# ==============================================================================

if __name__ == "__main__":
    pass
