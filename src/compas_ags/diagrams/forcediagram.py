from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

from compas.datastructures import mesh_dual
from compas_ags.diagrams import Diagram


__all__ = ['ForceDiagram']


class ForceDiagram(Diagram):
    """Diagram for representing the force diagram in Graphic Statics.

    Parameters
    ----------
    None

    Attributes
    ----------
    dual : :class:`compas_ags.diagrams.FormDiagram`
        The dual of the force diagram is a form diagram.

    Notes
    -----
    The force diagram has only 1 constructor function: ``ForceDiagram.from_formdiagram``

    Examples
    --------
    >>> from compas_ags.diagrams import FormGraph
    >>> from compas_ags.diagrams import FormDiagram
    >>> from compas_ags.diagrams import ForceDiagram

    >>> graph = FormGraph.from_lines(...)
    >>> form = FormDiagram.from_graph(graph)
    >>> force = ForceDiagram.from_formdiagram(form)
    >>> force.dual is form
    True
    """

    def __init__(self):
        super(ForceDiagram, self).__init__()
        self.attributes.update({
            'name': 'ForceDiagram'})
        self.update_default_vertex_attributes({
            'is_fixed': False,
            'is_anchor': False,
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
        :class:``
        """
        forcediagram = mesh_dual(formdiagram, cls)
        forcediagram.dual = formdiagram
        return forcediagram

    # --------------------------------------------------------------------------
    # Convenience functions for retrieving attributes of the force diagram.
    # --------------------------------------------------------------------------

    def xy(self):
        return [self.vertex_coordinates(key, 'xy') for key in self.vertices()]

    def fixed(self):
        return [key for key, attr in self.vertices(True) if attr['is_fixed']]

    def anchor(self):
        for key, attr in self.vertices(True):
            if attr['is_anchor']:
                return key
        return key

    def set_fixed(self, keys):
        for key, attr in self.vertices(True):
            attr['is_fixed'] = key in keys

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

    def uv_index(self, form=None):
        if not form:
            return {(u, v): index for index, (u, v) in enumerate(self.edges())}
        uv_index = dict()
        for index, (u, v) in enumerate(form.edges()):
            f1 = form.halfedge[u][v]
            f2 = form.halfedge[v][u]
            uv_index[(f1, f2)] = index
        return uv_index

    def ordered_edges(self, form, index=True):
        key_index = self.key_index()
        uv_index = self.uv_index(form=form)
        index_uv = dict((i, uv) for uv, i in uv_index.items())
        edges = [index_uv[i] for i in range(self.number_of_edges())]
        if not index:
            return edges
        return [[key_index[u], key_index[v]] for u, v in edges]

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
        import numpy as np
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


# ==============================================================================
# Main
# ==============================================================================

if __name__ == '__main__':
    pass
