from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

from itertools import islice
from compas.datastructures import network_find_cycles
from compas_ags.diagrams import Diagram


__all__ = ['BaseDiagram']


class BaseDiagram(Diagram):
    """Mesh-based data structure for input graph in AGS.
    """

    def __init__(self):
        super(BaseDiagram, self).__init__()
        self._graph = None
        self.attributes.update({
            'name': 'BaseDiagram',
        })
        self.update_default_vertex_attributes({
            'is_fixed': False,
            'cx': 0.0,
            'cy': 0.0,
        })
        self.update_default_edge_attributes({
            '_is_edge': True,
            'is_external': False,
        })

    @property
    def graph(self):
        return self._graph

    @graph.setter
    def graph(self, graph):
        self._graph = graph

    @classmethod
    def from_graph(cls, graph):
        """Construct a base diagram from a form graph.

        This constructor converts the form graph into a mesh by finding the cycles of its planar embedding.
        Note that tt doesn't check if the graph actually is a planar embedding.
        The outside face of the mesh is automatically split into smaller faces at the leaves.

        Parameters
        ----------
        graph : :class:`compas_ags.diagrams.FormGraph`

        Returns
        -------
        :class:`compas_ags.diagrams.BaseDiagram`
        """

        node_index = graph.node_index()
        cycles = network_find_cycles(graph, breakpoints=graph.leaves())
        points = graph.nodes_attributes('xyz')
        cycles[:] = [[node_index[node] for node in cycle] for cycle in cycles]
        basediagram = cls.from_vertices_and_faces(points, cycles)
        basediagram.edges_attribute('_is_edge', False, keys=list(basediagram.edges_on_boundary()))
        basediagram.edges_attribute('is_external', True, keys=basediagram.leaf_edges())
        basediagram.graph = graph
        return basediagram

    # --------------------------------------------------------------------------
    # vertices
    # --------------------------------------------------------------------------

    def leaves(self):
        """Identify the leaves of the base diagram.

        Returns
        -------
        list
            The identifiers of vertices with only one connected edge.
        """
        keys = []
        for key in self.vertices():
            edges = 0
            nbrs = self.vertex_neighbors(key)
            for nbr in nbrs:
                if self.edge_attribute((key, nbr), '_is_edge'):
                    edges += 1
            if edges == 1:
                keys.append(key)
        return keys

    # --------------------------------------------------------------------------
    # edges
    # --------------------------------------------------------------------------

    def edges(self, data=False):
        """Edge iterator automatically discarding mesh edges that are not relevant in AGS.

        Parameters
        ----------
        data : bool, optional
            If `True`, yield the data attributes of the edges together with their identifiers.

        Yields
        ------
        tuple
            If `data` is `False`, the tuple of vertices identifying the edge.
            Otherwise, a tuple with the pair of vertices and an attribute dict.
        """
        seen = set()
        for u in self.halfedge:
            for v in self.halfedge[u]:
                if (u, v) in seen or (v, u) in seen:
                    continue
                seen.add((u, v))
                seen.add((v, u))
                if not self.edge_attribute((u, v), '_is_edge'):
                    continue
                if not data:
                    yield u, v
                else:
                    yield (u, v), self.edge_attributes((u, v))

    def leaf_edges(self):
        """Identify the edges connecting leaf vertices to the diagram.

        Returns
        -------
        list
            The identifiers of the edges.
        """
        edges = []
        leaves = set(self.leaves())
        for u, v in self.edges():
            if u in leaves or v in leaves:
                edges.append((u, v))
        return edges


# ==============================================================================
# Main
# ==============================================================================

if __name__ == '__main__':
    pass
