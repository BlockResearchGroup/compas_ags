from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

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

    """

    def __init__(self, form, scale=None, settings=None, **kwargs):
        super(FormArtist, self).__init__(form, **kwargs)
        self.scale = scale
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

    @property
    def form(self):
        """The form diagram assigned to the artist."""
        return self.mesh

    @form.setter
    def form(self, form):
        self.mesh = form

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
        # vertices
        if self.settings['show.vertices']:
            color = {}
            color.update({vertex: self.settings['color.vertices'] for vertex in self.form.vertices()})
            self.draw_vertices(color=color)
        # edges
        if self.settings['show.edges']:
            color = {}
            color.update({edge: self.settings['color.edges'] for edge in self.form.edges()})
            color.update({edge: self.settings['color.edges:is_external'] for edge in self.form.edges_where({'is_external': True})})
            color.update({edge: self.settings['color.edges:is_ind'] for edge in self.form.edges_where({'is_ind': True})})
            self.draw_edges(color=color)
        # vertex labels
        if self.settings['show.vertexlabels']:
            text = {vertex: index for index, vertex in enumerate(self.form.vertices())}
            color = {}
            color.update({vertex: self.settings['color.vertices'] for vertex in self.form.vertices()})
            self.draw_vertexlabels(text=text, color=color)
        # edge labels
        if self.settings['show.edgelabels']:
            text = {edge: index for index, edge in enumerate(self.form.edges())}
            color = {}
            color.update({edge: self.settings['color.edges'] for edge in self.form.edges()})
            color.update({edge: self.settings['color.edges:is_external'] for edge in self.form.edges_where({'is_external': True})})
            color.update({edge: self.settings['color.edges:is_ind'] for edge in self.form.edges_where({'is_ind': True})})
            self.draw_edgelabels(text=text, color=color)


# ==============================================================================
# Main
# ==============================================================================

if __name__ == "__main__":
    pass
