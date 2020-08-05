from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

from compas.datastructures import mesh_dual
from compas_ags.diagrams import Diagram


__all__ = ['ForceDiagram']


class ForceDiagram(Diagram):
    """Mesh-based data structure for force diagrams in AGS.
    """

    def __init__(self):
        super(ForceDiagram, self).__init__()
        self.attributes.update({
            'name': 'Force'})
        self.update_default_vertex_attributes({
            'is_fixed': False,
            'is_param': False})
        self.update_default_edge_attributes({
            'l': 0.0,
            'lmin': 1e-7,
            'lmax': 1e+7})

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
        return self.vertices_attributes('xy')

    def fixed(self):
        """The identifiers of the fixed vertices.

        Returns
        -------
        list
        """
        return list(self.vertices_where({'is_fixed': True}))

    # --------------------------------------------------------------------------
    # Helpers
    # --------------------------------------------------------------------------

    def dual_edge(self, edge):
        for u, v in self.dual.face_halfedges(edge[0]):
            if self.dual.halfedge[v][u] == edge[1]:
                return u, v

    def is_dual_edge_external(self, edge):
        return self.dual.edge_attribute(self.dual_edge(edge), 'is_external')

    def is_dual_edge_reaction(self, edge):
        return self.dual.edge_attribute(self.dual_edge(edge), 'is_reaction')

    def is_dual_edge_load(self, edge):
        return self.dual.edge_attribute(self.dual_edge(edge), 'is_load')

    def is_dual_edge_ind(self, edge):
        return self.dual.edge_attribute(self.dual_edge(edge), 'is_ind')

    def dual_edge_f(self, edge):
        return self.dual.edge_attribute(self.dual_edge(edge), 'f')

    def edge_index(self, form=None):
        if not form:
            return {edge: index for index, edge in enumerate(self.edges())}
        edge_index = dict()
        for index, (u, v) in enumerate(form.edges()):
            f1 = form.halfedge[u][v]
            f2 = form.halfedge[v][u]
            edge_index[f1, f2] = index
        return edge_index

    def ordered_edges(self, form):
        edge_index = self.edge_index(form=form)
        index_edge = {index: edge for edge, index in edge_index.items()}
        edges = [index_edge[index] for index in range(self.number_of_edges())]
        return edges

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

if __name__ == '__main__':
    pass
