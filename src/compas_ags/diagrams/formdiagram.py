from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

from itertools import islice
from compas.utilities import geometric_key_xy
from compas.datastructures import network_find_cycles
from compas_ags.diagrams import Diagram


__all__ = ['FormDiagram']


class FormDiagram(Diagram):
    """Mesh-based data structure for form diagrams in AGS."""

    def __init__(self):
        super(FormDiagram, self).__init__()
        self.attributes.update({
            'name': 'FormDiagram',
            'color.vertex': (255, 255, 255),
            'color.edge': (0, 0, 0),
            'color.face': (0, 255, 255),
            'color.vertex:is_fixed': (255, 0, 0),
        })
        self.update_default_vertex_attributes({
            'is_fixed': False,
            'cx': 0.0,
            'cy': 0.0,
        })
        self.update_default_edge_attributes({
            'q': 1.0,
            'f': 0.0,
            'l': 0.0,
            'is_ind': False,
            'is_element': False,
            'is_reaction': False,
            'is_load': False,
            'is_edge': True,
        })

    @classmethod
    def from_graph(cls, graph):
        """Construct a form diagram from a form graph.

        Parameters
        ----------
        graph : :class:`compas_ags.diagrams.FormGraph`

        Returns
        -------
        :class:`compas_ags.diagrams.FormDiagram`
        """
        points = graph.to_points()
        cycles = network_find_cycles(graph, breakpoints=graph.leaves())
        form = cls.from_vertices_and_faces(points, cycles)
        form.edges_attribute('is_edge', False, keys=list(form.edges_on_boundary()))
        return form

    # --------------------------------------------------------------------------
    # Topology
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
                if not self.edge_attribute((u, v), 'is_edge'):
                    continue
                if not data:
                    yield u, v
                else:
                    yield (u, v), self.edge_attributes((u, v))

    def leaves(self):
        """Identify the leaves of the form diagram.

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
                if self.edge_attribute((key, nbr), 'is_edge'):
                    edges += 1
            if edges == 1:
                keys.append(key)
        return keys

    def face_adjacency_edge(self, f1, f2):
        edges = list(self.edges())
        for u, v in self.face_halfedges(f1):
            if self.halfedge[v][u] == f2:
                if (u, v) in edges:
                    return u, v
                return v, u

    def uv_index(self):
        return {key: index for index, key in enumerate(self.edges())}

    def index_uv(self):
        return {index: key for index, key in enumerate(self.edges())}

    # def external(self):
    #     external = []
    #     leaves = set(self.leaves())
    #     for u, v in self.edges():
    #         if u in leaves or v in leaves:
    #             external.append((u, v))
    #     return external

    # --------------------------------------------------------------------------
    # Convenience functions for retrieving the attributes of the formdiagram.
    # --------------------------------------------------------------------------

    def q(self):
        return self.edges_attribute('q')

    def xy(self):
        return self.vertices_attributes('xy')

    def fixed(self):
        return list(self.vertices_where({'is_fixed': True}))

    def constrained(self):
        return [key for key, attr in self.vertices(True) if attr['cx'] or attr['cy']]

    def constraints(self):
        cx = self.vertices_attribute('cx')
        cy = self.vertices_attribute('cy')
        return cx, cy

    def ind(self):
        return list(self.edges_where({'is_ind': True}))

    # --------------------------------------------------------------------------
    # Set stuff
    # --------------------------------------------------------------------------

    def set_fixed(self, keys):
        self.vertices_attribute('is_fixed', True, keys=keys)

    def edge_forcedensity(self, edge, q=None):
        """Get or set the forcedensity in an edge.

        Parameters
        ----------
        edge : int or tuple
            The identifier of the edge.
            This can be the index in the edge list or a tuple of vertices.
        q : float, optional
            If no new value is given, the current forcedensity value will be returned.
            Otherwise the stored value is updated with the provided one.

        Returns
        -------
        float or None
            The current forcedensity in the edge if no new value is given.
            Otherwise, nothing.
        """
        if type(edge) is int:
            edge = next(islice(self.edges(), edge, None))
        if q is None:
            return self.edge_attribute(edge, 'q')
        self.edge_attribute(edge, 'q', q)

    def edge_force(self, edge, force=None):
        """Get or set the force in an edge.

        Parameters
        ----------
        edge : int or tuple
            The identifier of the edge.
            This can be the index in the edge list or a tuple of vertices.
        force : float, optional
            If no value is given, the current force value will be returned.
            Otherwise the stored value is updated.

        Returns
        -------
        float or None
            The current force in the edge if no new value is given.
            Otherwise, nothing.
        """
        if type(edge) is int:
            edge = next(islice(self.edges(), edge, None))
        length = self.edge_length(*edge)
        q = self.edge_attribute(edge, 'q')
        if force is None:
            return q * length
        self.edge_attribute(edge, 'is_ind', True)
        self.edge_attribute(edge, 'q', force / length)

    # --------------------------------------------------------------------------
    # Identify features of the formdiagram based on geometrical inputs.
    # --------------------------------------------------------------------------

    def identify_fixed(self, points=None, fix_degree=1):
        for key, attr in self.vertices(True):
            attr['is_fixed'] = self.vertex_degree(key) <= fix_degree
        if points:
            xy_key = {}
            for key in self.vertices():
                gkey = geometric_key_xy(self.vertex_attributes(key, 'xy'))
                xy_key[gkey] = key
            for xy in points:
                gkey = geometric_key_xy(xy)
                if gkey in xy_key:
                    key = xy_key[gkey]
                    self.vertex[key]['is_fixed'] = True

    def identify_constraints(self, points=None):
        if points:
            xy_key = {}
            for key in self.vertices():
                gkey = geometric_key_xy(self.vertex_attributes(key, 'xy'))
                xy_key[gkey] = key
            for xy in points:
                gkey = geometric_key_xy(xy)
                if gkey in xy_key:
                    key = xy_key[gkey]
                    self.vertex[key]['cx'] = 1.0
                    self.vertex[key]['cy'] = 1.0


# ==============================================================================
# Main
# ==============================================================================

if __name__ == '__main__':
    pass
