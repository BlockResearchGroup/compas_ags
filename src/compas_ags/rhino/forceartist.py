from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

from compas_rhino.artists import MeshArtist


__all__ = ['ForceArtist']


class ForceArtist(MeshArtist):

    __module__ = 'compas_tna.rhino'

    @property
    def force(self):
        return self.datastructure


# ==============================================================================
# Main
# ==============================================================================

if __name__ == "__main__":
    pass
