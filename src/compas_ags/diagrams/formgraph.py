from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

from compas.datastructures import Network
# from compas.datastructures import network_is_xy

__all__ = ['FormGraph']


class FormGraph(Network):

    def __init__(self):
        super(FormGraph, self).__init__()

    def is_2d(self):
        return True # network_is_xy(self)


# ==============================================================================
# Main
# ==============================================================================

if __name__ == '__main__':
    pass
