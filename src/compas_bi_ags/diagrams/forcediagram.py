from compas_ags.diagrams import ForceDiagram

__all__ = [
    'ForceDiagram'
]

import numpy as np

class ForceDiagram(ForceDiagram):

    # --------------------------------------------------------------------------
    # Convenience functions for retrieving attributes of the force diagram.
    # --------------------------------------------------------------------------

    def set_anchor(self, keys):
        """Set the anchored vertex in the force diagram

        Parameters
        ----------
        keys : list[int]
            Contains the index of the vertex to anchor.
        """
        for key, attr in self.vertices(True):
            attr['is_anchor'] = key in keys

    # --------------------------------------------------------------------------
    # Helpers
    # --------------------------------------------------------------------------

    def external_edges(self, form):
        """Returns the edges incident to leaf vertices

        Parameters
        ----------
        form : compas_ags.diagrams.formdiagram.FormDiagram
            The form diagram to update.

        Returns
        ----------
        e_e : list[int]
            The edges incident to leaf vertices
        """
        leaves = set(form.leaves())
        e_e = []
        for i, (u, v) in enumerate(form.edges()):
            if u in leaves or v in leaves:
                e_e.append(i)
        return e_e

    def external_vertices(self, form):
        """Returns indices of the vertices on the external face of the force diagram

        Parameters
        ----------
        form : compas_ags.diagrams.formdiagram.FormDiagram
            The form diagram to update.

        Returns
        ----------
        e_v : list[int]
            Indices of the vertices on the external face of the force diagram
        """
        external_edges = self.external_edges(form)
        e_v = []
        for i, (u, v) in enumerate(self.ordered_edges(form)):
            if i in external_edges:
                e_v.append(u)
                e_v.append(v)
        return list(set(e_v))

    def compute_constraints(self, form, M):
        r"""Computes the form diagram constraints used 
        in compas_bi_ags.bi_ags.graphstatics.form_update_from_force_direct

        Parameters
        ----------
        form : compas_ags.diagrams.formdiagram.FormDiagram
            The form diagram to update.
        M
            The matrix described in compas_bi_ags.bi_ags.graphstatics.form_update_from_force_direct
        """
        nr_col_jac = M.shape[1]
        constraint_rows = np.zeros((0, M.shape[1]))
        residual = np.zeros((0, 1))
        vcount = form.number_of_vertices()

        # Currently this computes two constraints per fixed vertex in the form diagram.
        for i, (key, attr) in enumerate(form.vertices(True)):
            if not attr['is_fixed']:
                continue

            # Handle x
            constraint_jac_row = np.zeros(
                (1, nr_col_jac))  # Added row for jacobian
            # Lock horizontal position
            constraint_jac_row[0, i] = 1
            constraint_rows = np.vstack((constraint_rows, constraint_jac_row))
            residual = np.vstack((residual, attr['x']))

            # Handle y
            constraint_jac_row = np.zeros(
                (1, nr_col_jac))  # Added row for jacobian
            # Lock horizontal position
            constraint_jac_row[0, i+vcount] = 1
            constraint_rows = np.vstack((constraint_rows, constraint_jac_row))
            residual = np.vstack((residual, attr['y']))
        return constraint_rows, residual

