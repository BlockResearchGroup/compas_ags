from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

from itertools import islice
from compas_ags.diagrams import Diagram
from compas.datastructures import network_find_cycles
from compas.geometry import Line


__all__ = ["FormDiagram"]


class FormDiagram(Diagram):
    """Mesh-based data structure for form diagrams in AGS."""

    def __init__(self):
        super(FormDiagram, self).__init__()
        self._graph = None
        self.attributes.update(
            {
                "name": "Form",
            }
        )
        self.update_default_vertex_attributes(
            {
                "is_fixed": False,
                "line_constraint": None,
                "cx": 0.0,
                "cy": 0.0,
            }
        )
        self.update_default_edge_attributes(
            {
                "_is_edge": True,
                "a": 0.0,
                "q": 1.0,
                "f": 0.0,
                "l": 0.0,
                "is_ind": False,
                "is_external": False,
                "is_reaction": False,
                "is_load": False,
                "target_vector": None,
                "target_force": None,
            }
        )

    @property
    def graph(self):
        return self._graph

    @graph.setter
    def graph(self, graph):
        self._graph = graph

    @classmethod
    def from_graph(cls, graph):
        """Construct a form diagram from a form graph.

        This constructor converts the form graph into a mesh by finding the cycles of its planar embedding.
        Note that tt doesn't check if the graph actually is a planar embedding.
        The outside face of the mesh is automatically split into smaller faces at the leaves.

        Parameters
        ----------
        graph : :class:`compas_ags.diagrams.FormGraph`

        Returns
        -------
        :class:`compas_ags.diagrams.FormDiagram`
        """
        for node in list(graph.nodes()):
            if graph.degree(node) == 2:
                graph.delete_node(node)
        node_index = graph.node_index()
        cycles = network_find_cycles(graph, breakpoints=graph.leaves())
        points = graph.nodes_attributes("xyz")
        cycles[:] = [[node_index[node] for node in cycle] for cycle in cycles]
        form = cls.from_vertices_and_faces(points, cycles)
        form.edges_attribute("_is_edge", False, keys=list(form.edges_on_boundary()))
        form.edges_attribute("is_external", True, keys=form.leaf_edges())
        form.graph = graph
        return form

    # --------------------------------------------------------------------------
    # vertices
    # --------------------------------------------------------------------------

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
                if self.edge_attribute((key, nbr), "_is_edge"):
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
                if not self.edge_attribute((u, v), "_is_edge"):
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
            return self.edge_attribute(edge, "q")
        self.edge_attribute(edge, "q", q)

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
        q = self.edge_attribute(edge, "q")
        if force is None:
            return q * length
        self.edge_attribute(edge, "is_ind", True)
        self.edge_attribute(edge, "q", force / length)

    # --------------------------------------------------------------------------
    # Convenience functions for retrieving the attributes of the formdiagram.
    # --------------------------------------------------------------------------

    def q(self):
        return self.edges_attribute("q")

    def xy(self):
        return self.vertices_attributes("xy")

    def fixed(self):
        return list(self.vertices_where({"is_fixed": True}))

    def constrained(self):
        return [key for key, attr in self.vertices(True) if attr["cx"] or attr["cy"]]

    def constraints(self):
        cx = self.vertices_attribute("cx")
        cy = self.vertices_attribute("cy")
        return cx, cy

    def ind(self):
        return list(self.edges_where({"is_ind": True}))

    # --------------------------------------------------------------------------
    # Identify features of the formdiagram based on geometrical inputs.
    # --------------------------------------------------------------------------

    def identify_constraints(self, tol=10e-4):
        """Identify constraints on the Form Diagram based on the geometry.
        External loads define a line-load which constraint vertices in x, or y.

        Parameters
        ----------
        tol : float, optional
            Tolerance to define if leaves lay in a vertical, or horizontal line.
            The default value is `10E-4`.

        Returns
        -------
        None
            The FormDiagram is modified in place.
        """
        fixed = self.fixed()
        leaves = self.leaves()
        for edge in self.leaf_edges():
            sp, ep = self.edge_coordinates(*edge)
            line = Line(sp, ep)
            dx = ep[0] - sp[0]
            dy = ep[1] - sp[1]
            length = (dx**2 + dy**2) ** 0.5
            self.edge_attribute(edge, "target_vector", [dx / length, dy / length])
            self.edge_attribute(edge, "is_load", True)  # by default loads are leaves connected to non fixed vertices
            if edge[0] in fixed or edge[1] in fixed:
                self.edge_attribute(
                    edge, "is_reaction", True
                )  # by default reactions are leaves connected to fixed vertices
                self.edge_attribute(edge, "is_load", False)
                continue
            if edge[0] in leaves:
                self.vertex_attribute(edge[1], "line_constraint", line)
            else:
                self.vertex_attribute(edge[0], "line_constraint", line)

    # def identify_fixed(self, points=None, fix_degree=1):
    #     for key, attr in self.vertices(True):
    #         attr['is_fixed'] = self.vertex_degree(key) <= fix_degree
    #     if points:
    #         xy_key = {}
    #         for key in self.vertices():
    #             gkey = geometric_key_xy(self.vertex_attributes(key, 'xy'))
    #             xy_key[gkey] = key
    #         for xy in points:
    #             gkey = geometric_key_xy(xy)
    #             if gkey in xy_key:
    #                 key = xy_key[gkey]
    #                 self.vertex[key]['is_fixed'] = True

    # def identify_constraints(self, points=None):
    #     if points:
    #         xy_key = {}
    #         for key in self.vertices():
    #             gkey = geometric_key_xy(self.vertex_attributes(key, 'xy'))
    #             xy_key[gkey] = key
    #         for xy in points:
    #             gkey = geometric_key_xy(xy)
    #             if gkey in xy_key:
    #                 key = xy_key[gkey]
    #                 self.vertex[key]['cx'] = 1.0
    #                 self.vertex[key]['cy'] = 1.0


# ==============================================================================
# Main
# ==============================================================================

if __name__ == "__main__":
    pass
