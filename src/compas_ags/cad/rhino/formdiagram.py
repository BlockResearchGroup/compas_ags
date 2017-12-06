import compas_rhino as rhino

from compas_ags.ags.diagrams import FormDiagram


__author__    = ['Tom Van Mele', ]
__copyright__ = 'Copyright 2016 - Block Research Group, ETH Zurich'
__license__   = 'MIT License'
__email__     = 'vanmelet@ethz.ch'


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
