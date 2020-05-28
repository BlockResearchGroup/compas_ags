from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

from compas_rhino.artists import MeshArtist


__all__ = ['ForceArtist']


class ForceArtist(MeshArtist):
    """Inherits the compas :class:`MeshArtist`, provides functionality for visualisation of 3D graphic statics applications.
    
    Parameters
    ----------
    form: compas_ags.forcediagram.ForceDiagram
        The force diagram to draw.
    layer: string, optional
        The name of the layer that will contain the forcediagram.
    """
    
    __module__ = 'compas_tna.rhino'

    @property
    def force(self):
        return self.datastructure

    def __init__(self, force, layer=None):
        super(ForceArtist, self).__init__(force, layer=layer)
    
    def draw_edge_force(self):
        pass
# ==============================================================================
# Main
# ==============================================================================

if __name__ == "__main__":
    pass
