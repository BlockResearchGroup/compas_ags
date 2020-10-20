from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

from compas_ags.rhino.diagramartist import DiagramArtist


__all__ = ['ForceArtist']


class ForceArtist(DiagramArtist):
    """Artist for force diagrams in AGS.

    Parameters
    ----------
    form: compas_ags.diagrams.FormDiagram
        The form diagram to draw.

    """

    def __init__(self, force, layer=None):
        super(ForceArtist, self).__init__(force, layer=layer)
