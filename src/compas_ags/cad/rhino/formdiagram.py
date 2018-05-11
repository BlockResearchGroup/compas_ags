from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

import compas_rhino

from compas_ags.diagrams import FormDiagram


__author__    = ['Tom Van Mele', ]
__copyright__ = 'Copyright 2016 - Block Research Group, ETH Zurich'
__license__   = 'MIT License'
__email__     = 'vanmelet@ethz.ch'


__all__ = [
    'FormDiagram',
]


class FormDiagram(FormDiagram):
    """"""

    def __init__(self):
        super(FormDiagram, self).__init__()
        self.attributes['layer'] = 'AGS::FormDiagram'

    def draw(self):
        vertexcolor = dict(
            (key, self.attributes['color.vertex:is_fixed'] if attr['is_fixed'] else self.attributes['color.vertex'])
            for key, attr in self.vertices_iter(True)
        )
        edgecolor = dict()
        compas_rhino.draw_network(
            self,
            layer=self.attributes['layer'],
            vertexcolor=vertexcolor,
            edgecolor=edgecolor
        )


# ==============================================================================
# Debugging
# ==============================================================================

if __name__ == "__main__":
    pass
