from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

from compas_ags.rhino.diagramartist import DiagramArtist


__all__ = ['BaseArtist']


class BaseArtist(DiagramArtist):
    """Artist for base diagram in AGS.

    Parameters
    ----------
    graph: compas_ags.diagrams.FormGraph
        The graph to draw.

    Other Parameters
    ----------------
    See the parent artists for other parameters.

    """

    def __init__(self, form, scale=None, settings=None, **kwargs):
        super(BaseArtist, self).__init__(form, **kwargs)
        self._guid_force = {}
        self.scale = scale
        if settings:
            self.settings.update(settings)

    def draw(self):
        """Draw the base diagram.

        The visible components, display properties and visual style of the base diagram
        drawn by this method can be fully customised using the configuration items
        in the settings dict: ``BaseArtist.settings``.

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
            color.update({vertex: self.settings['color.basediagram'] for vertex in self.diagram.vertices()})
            self.draw_vertices(color=color)
        # edges
        if self.settings['show.edges']:
            color = {}
            color.update({edge: self.settings['color.basediagram'] for edge in self.diagram.edges()})
            self.draw_edges(color=color)
