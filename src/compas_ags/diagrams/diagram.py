from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

from compas.datastructures import Mesh


__all__ = ["Diagram"]


class Diagram(Mesh):
    """Basic mesh-based data structure for diagrams in AGS.

    Attributes
    ----------
    dual : :class:`compas_ags.diagrams.Diagram`
        The dual diagram of this diagram.

    """

    def __init__(self):
        super(Diagram, self).__init__()
        self._dual = None

    @property
    def dual(self):
        """The dual of this diagram."""
        return self._dual

    @dual.setter
    def dual(self, dual):
        self._dual = dual

    def vertex_index(self):
        return {vertex: index for index, vertex in enumerate(self.vertices())}

    def index_vertex(self):
        return {index: vertex for index, vertex in enumerate(self.vertices())}

    def edge_index(self):
        return {edge: index for index, edge in enumerate(self.edges())}

    def index_edge(self):
        return {index: edge for index, edge in enumerate(self.edges())}


# ==============================================================================
# Main
# ==============================================================================

if __name__ == "__main__":
    pass
