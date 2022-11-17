from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

from compas.datastructures import mesh_dual
from compas_ags.diagrams import Diagram
from compas.geometry import Line


__all__ = ["ForceDiagram"]


class ForceDiagram(Diagram):
    """Mesh-based data structure for force diagrams in AGS."""

    def __init__(self):
        super(ForceDiagram, self).__init__()
        self.attributes.update({"name": "Force"})
        self.update_default_vertex_attributes({"is_fixed": False, "line_constraint": None, "is_param": False})
        self.update_default_edge_attributes({"l": 0.0, "target_vector": None})

    # --------------------------------------------------------------------------
    # Constructors
    # --------------------------------------------------------------------------

    @classmethod
    def from_formdiagram(cls, formdiagram):
        """Construct a force diagram from a form diagram.

        Parameters
        ----------
        formdiagram : :class:`compas_tna.diagrams.FormDiagram`
            The form diagram.

        Returns
        -------
        :class:`compas_ags.diagrams.ForceDiagram`
        """
        forcediagram = mesh_dual(formdiagram, cls)
        forcediagram.dual = formdiagram
        formdiagram.dual = forcediagram
        return forcediagram

    # --------------------------------------------------------------------------
    # Convenience functions for retrieving attributes of the force diagram.
    # --------------------------------------------------------------------------

    def xy(self):
        """The XY coordinates of the vertices.

        Returns
        -------
        list
        """
        return self.vertices_attributes("xy")

    def fixed(self):
        """The identifiers of the fixed vertices.

        Returns
        -------
        list
        """
        return list(self.vertices_where({"is_fixed": True}))

    def anchor(self):
        """Get an anchor to the force diagram.

        Returns
        -------
        int
        """
        return next(self.vertices())

    # --------------------------------------------------------------------------
    # Helpers
    # --------------------------------------------------------------------------

    def edges_where_dual(self, conditions, data=False):
        """Get edges for which a certain condition or set of conditions is true for the corresponding edges in the diagram's dual.

        Parameters
        ----------
        conditions : dict
            A set of conditions in the form of key-value pairs.
            The keys should be attribute names. The values can be attribute
            values or ranges of attribute values in the form of min/max pairs.
        data : bool, optional
            Yield the edges and their data attributes.
            Default is ``False``.

        Yields
        ------
        2-tuple
            The next edge as a (u, v) tuple, if ``data=False``.
            The next edge as a ((u, v), data) tuple, if ``data=True``.

        Examples
        --------
        >>>

        """
        for edge in list(self.edges()):
            is_match = True

            dual_edge = self.dual_edge(edge)
            dual_edge_attr = self.dual.edge_attributes(dual_edge)

            for cond_name, cond_value in conditions.items():
                dual_method = getattr(self.dual, cond_name, None)

                if dual_method and callable(dual_method):
                    dual_value = dual_method(dual_edge)
                elif cond_name in dual_edge_attr:
                    dual_value = dual_edge_attr[cond_name]
                else:
                    is_match = False
                    break

                if isinstance(dual_value, list):
                    if cond_value not in dual_value:
                        is_match = False
                        break
                elif isinstance(cond_value, (tuple, list)):
                    minval, maxval = cond_value
                    if dual_value < minval or dual_value > maxval:
                        is_match = False
                        break
                else:
                    if cond_value != dual_value:
                        is_match = False
                        break

            if is_match:
                if data:
                    yield edge, self.edge_attributes(edge)
                else:
                    yield edge

    def dual_edge(self, edge):
        """Find the cooresponding edge in the diagram's dual.

        Parameters
        ----------
        edge : tuple of int
            The edge identifier.

        Returns
        -------
        tuple (int, int) or None
            The identifier of the dual edge if it exists.
        """
        for u, v in self.dual.face_halfedges(edge[0]):
            if self.dual.halfedge[v][u] == edge[1]:
                if self.dual.has_edge((u, v)):
                    return u, v
                return v, u

    def is_dual_edge_external(self, edge):
        """Verify if the corresponding edge in the diagram's dual is marked as "external".

        Parameters
        ----------
        edge : tuple of int
            The edge identifier.

        Returns
        -------
        bool
        """
        return self.dual.edge_attribute(self.dual_edge(edge), "is_external")

    def is_dual_edge_reaction(self, edge):
        """Verify if the corresponding edge in the diagram's dual is marked as "reaction".

        Parameters
        ----------
        edge : tuple of int
            The edge identifier.

        Returns
        -------
        bool
        """
        return self.dual.edge_attribute(self.dual_edge(edge), "is_reaction")

    def is_dual_edge_load(self, edge):
        """Verify if the corresponding edge in the diagram's dual is marked as "load".

        Parameters
        ----------
        edge : tuple of int
            The edge identifier.

        Returns
        -------
        bool
        """
        return self.dual.edge_attribute(self.dual_edge(edge), "is_load")

    def is_dual_edge_ind(self, edge):
        """Verify if the corresponding edge in the diagram's dual is marked as "independent".

        Parameters
        ----------
        edge : tuple of int
            The edge identifier.

        Returns
        -------
        bool
        """
        return self.dual.edge_attribute(self.dual_edge(edge), "is_ind")

    def dual_edge_force(self, edge):
        """Retrieve the force in the corresponding edge of the diagram's dual.

        Parameters
        ----------
        edge : tuple(int, int)
            The edge identifier.

        Returns
        -------
        float
        """
        return self.dual.edge_attribute(self.dual_edge(edge), "f")

    def dual_edge_angledeviation(self, edge):
        """Retrieve the angle deviation in the corresponding edge of the diagram's dual.

        Parameters
        ----------
        edge : tuple(int, int)
            The edge identifier.

        Returns
        -------
        float
        """
        return self.dual.edge_attribute(self.dual_edge(edge), "a")

    def dual_edge_targetforce(self, edge):
        """Retrieve the target force in the corresponding edge of the diagram's dual.

        Parameters
        ----------
        edge : tuple(int, int)
            The edge identifier.

        Returns
        -------
        float
        """
        return self.dual.edge_attribute(self.dual_edge(edge), "target_force")

    def edge_index(self, form=None):
        """Construct a mapping between the identifiers of edges and the corresponding indices in a list of edges.

        Parameters
        ----------
        form : :class:`compas_ags.diagrams.FormDiagram`, optional
            If a form diagra is provided as reference, the list of edges is ordered such that it corresponds
            to the natural ordering of edges in the form diagram.

        Returns
        -------
        dict
            Mapping between edge identifiers and the correpsonding indices of the edges in a list.

        """
        if not form:
            return {edge: index for index, edge in enumerate(self.edges())}
        edge_index = dict()
        for index, (u, v) in enumerate(form.edges()):
            f1 = form.halfedge[u][v]
            f2 = form.halfedge[v][u]
            edge_index[f1, f2] = index
            # the weird side-effect of this is that edges get rotated if necessary
        return edge_index

    def ordered_edges(self, form):
        """ "Construct a list of edges with the same order as the corresponding edges of the form diagram.

        Parameters
        ----------
        form : :class:`compas_ags.diagrams.FormDiagram`

        Returns
        -------
        list
        """
        edge_index = self.edge_index(form=form)
        index_edge = {index: edge for edge, index in edge_index.items()}
        edges = [index_edge[index] for index in range(self.number_of_edges())]
        return edges

    # --------------------------------------------------------------------------
    # Helpers
    # --------------------------------------------------------------------------

    def constraints_from_dual(self, tol=10e-4):
        """ "Reflect constraints from the form diagram in the force diagram.

        Returns
        -------
        ForceDiagram is modified in place.
        """
        edge_index = self.dual.edge_index()
        ordered_edges = self.ordered_edges(self.dual)
        edges_orient = []

        for edge in self.edges_where_dual({"is_ind": True}):  # Fix vertices of dual independent edge
            self.vertices_attribute("is_fixed", True, keys=edge)
            edges_orient.append(edge)

        for edge in self.edges_where_dual(
            {"is_load": True}
        ):  # If loads are orthogonal the force dual edge gets constrained
            self.edge_attribute(edge, "is_load", True)
            edges_orient.append(edge)
            sp, ep = self.edge_coordinates(*edge)
            line = Line(sp, ep)
            self.vertices_attribute("line_constraint", value=line, keys=edge)

        for edge in self.edges_where_dual({"is_reaction": True}):
            self.edge_attribute(edge, "is_reaction", True)
            edges_orient.append(edge)

        for form_edge in self.dual.edges():
            target_vector = self.dual.edge_attribute(form_edge, "target_vector")
            index = edge_index[form_edge]
            force_edge = ordered_edges[index]
            if target_vector is not None:
                edges_orient.append(force_edge)

        for edge in edges_orient:
            edge = edge if edge in list(self.edges()) else (edge[1], edge[0])
            sp, ep = self.edge_coordinates(*edge)
            dx = ep[0] - sp[0]
            dy = ep[1] - sp[1]
            length = (dx**2 + dy**2) ** 0.5
            self.edge_attribute(edge, "target_vector", [dx / length, dy / length])

    # def compute_constraints(self, form, M):
    #     r"""Computes the form diagram constraints used
    #     in compas_bi_ags.bi_ags.graphstatics.form_update_from_force_direct

    #     Parameters
    #     ----------
    #     form : compas_ags.diagrams.formdiagram.FormDiagram
    #         The form diagram to update.
    #     M
    #         The matrix described in compas_bi_ags.bi_ags.graphstatics.form_update_from_force_direct
    #     """
    #     import numpy as np
    #     nr_col_jac = M.shape[1]
    #     constraint_rows = np.zeros((0, M.shape[1]))
    #     residual = np.zeros((0, 1))
    #     vcount = form.number_of_vertices()

    #     # Currently this computes two constraints per fixed vertex in the form diagram.
    #     for i, (key, attr) in enumerate(form.vertices(True)):
    #         if not attr['is_fixed']:
    #             continue

    #         # Handle x
    #         constraint_jac_row = np.zeros(
    #             (1, nr_col_jac))  # Added row for jacobian
    #         # Lock horizontal position
    #         constraint_jac_row[0, i] = 1
    #         constraint_rows = np.vstack((constraint_rows, constraint_jac_row))
    #         residual = np.vstack((residual, attr['x']))

    #         # Handle y
    #         constraint_jac_row = np.zeros(
    #             (1, nr_col_jac))  # Added row for jacobian
    #         # Lock horizontal position
    #         constraint_jac_row[0, i+vcount] = 1
    #         constraint_rows = np.vstack((constraint_rows, constraint_jac_row))
    #         residual = np.vstack((residual, attr['y']))
    #     return constraint_rows, residual


# ==============================================================================
# Main
# ==============================================================================

if __name__ == "__main__":
    pass
