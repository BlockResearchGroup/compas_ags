from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

from compas.datastructures import Network


__all__ = ['FormGraph']


class FormGraph(Network):

    def __init__(self):
        super(FormGraph, self).__init__()
        self.is_2d()

    def is_2d(self):
        for key in self.nodes():
            if self.node_attribute(key, 'z') != 0.0 :
                print('Node %s not in xy plane. It will be projected to xy plane' % key)
                self.node_attribute(key, 'z', 0.0)
        return True


# ==============================================================================
# Main
# ==============================================================================

if __name__ == '__main__':
    pass
