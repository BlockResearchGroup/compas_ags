from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

from compas_ags.rhino.diagramartist import DiagramArtist


__all__ = ['GraphArtist']


class GraphArtist(DiagramArtist):
    """Artist for input graph in AGS.

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

    def __init__(self, form, scale=None, settings=None, **kwargs):
        super(GraphArtist, self).__init__(form, **kwargs)
        self._guid_force = {}
        self.scale = scale
        if settings:
            self.settings.update(settings)

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
            color.update({vertex: self.settings['color.basegraph'] for vertex in self.diagram.vertices()})
            self.draw_vertices(color=color)
        # edges
        if self.settings['show.edges']:
            color = {}
            color.update({edge: self.settings['color.basegraph'] for edge in self.diagram.edges()})
            self.draw_edges(color=color)