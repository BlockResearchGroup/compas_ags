import compas_rhino as rhino

from compas_ags.ags.diagrams import ForceDiagram


__author__    = ['Tom Van Mele', ]
__copyright__ = 'Copyright 2016 - Block Research Group, ETH Zurich'
__license__   = 'MIT License'
__email__     = 'vanmelet@ethz.ch'


class ForceDiagram(ForceDiagram):
    """"""

    def __init__(self):
        super(ForceDiagram, self).__init__()
        self.attributes['layer'] = 'AGS::ForceDiagram'

    def draw(self):
        vertexcolor = dict(
            (key, self.attributes['color.vertex'])
            for key, attr in self.vertices_iter(True)
        )
        edgecolor = dict()
        rhino.draw_network(
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
