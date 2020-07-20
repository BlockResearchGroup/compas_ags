from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

from abc import ABC, abstractmethod
import numpy as np
from compas_ags.diagrams.formdiagram import FormDiagram


__author__ = ['Vedad Alic', ]
__email__ = 'vedad.alic@construction.lth.se'


__all__ = [
    'ConstraintsCollection',
    'HorizontalFix',
    'VerticalFix'
]


class AbstractConstraint(ABC):
    """Used to derive form diagram constraints. The derived constraints
    must implement the compute_constraint and update_constraint_goal methods.

    Parameters
    ----------
    form : :class:`compas_ags.diagrams.FormDiagram`
        The form diagram to which the constraints are applied.

    Attributes
    ----------
    form : :class:`compas_ags.diagrams.FormDiagram`
        The form diagram to which the constraints are applied.
    """

    def __init__(self, form):
        super().__init__()
        self.form = form
        self._color = '#1524c6'
        self._width = 1.0
        self._style = '--'

    @abstractmethod
    def compute_constraint(self):
        """Computes the residual and Jacobian matrix of the constraint."""
        pass

    @abstractmethod
    def update_constraint_goal(self):
        """Update constraint values based on current form diagram"""
        pass

    @property
    def number_of_cols(self):
        vcount = self.form.number_of_vertices()
        return 2 * vcount

    def get_lines(self):
        """Get lines to draw in viewer."""
        pass


class ConstraintsCollection(object):
    """Computes the Jacobian d_X/dX and residual r of the added constraints
    where X contains the form diagram coordinates in *Fortran* order
    (first all x-coordinates, then all y-coordinates) and _X contains the
    force diagram coordinates in *Fortran* order (first all _x-coordinates,
    then all _y-coordinates)
    """

    def __init__(self, form):
        self.constraints = []  # type: list[AbstractConstraint]
        self.form = form   # type: FormDiagram

    def add_constraint(self, constraint):
        self.constraints.append(constraint)

    def compute_constraints(self):
        jac = np.zeros((0, self.constraints[0].number_of_cols))
        res = np.zeros((0, 1))
        for constraint in self.constraints:
            (j, r) = constraint.compute_constraint()
            jac = np.vstack((jac, j))
            res = np.vstack((res, r))
        return jac, res

    def update_constraints(self):
        for constraint in self.constraints:
            constraint.update_constraint_goal()

    def get_lines(self):
        """Get lines to draw in viewer."""
        lines = []
        for constraint in self.constraints:
            line = constraint.get_lines()
            if line:
                lines = lines + line
        return lines

    def constrain_dependent_leaf_edges_lengths(self):
        leaves = self.form.leaves()
        dependent_leaf_edges = []
        for i, (u, v) in enumerate(self.form.edges()):
            if u in leaves or v in leaves:
                if not self.form.edge_attribute((u, v), 'is_ind'):
                    dependent_leaf_edges.append(i)
        for e in dependent_leaf_edges:
            self.add_constraint(LengthFix(self.form, e))


class HorizontalFix(AbstractConstraint):
    """Keeps the x-coordinate of the vertex fixed"""

    def __init__(self, form, vertex):
        super().__init__(form)
        self.vertex = vertex
        self.set_initial_position()

    def set_initial_position(self):
        self.P = self.form.vertex_coordinates(self.vertex, 'xy')[0]

    def compute_constraint(self):
        constraint_jac_row = np.zeros((1, self.number_of_cols))
        idx = self.form.key_index()[self.vertex]
        constraint_jac_row[0, idx] = 1
        r = self.form.vertex_coordinates(self.vertex, 'xy')[0] - self.P
        return constraint_jac_row, r

    def update_constraint_goal(self):
        self.set_initial_position()

    def get_lines(self):
        constraint_lines = []
        s = self.form.vertex_coordinates(self.vertex, 'xy')
        e = self.form.vertex_coordinates(self.vertex, 'xy')
        s[1] += 1
        e[1] -= 1
        constraint_lines.append({
            'start': s,
            'end': e,
            'width': self._width,
            'color': self._color,
            'style': self._style,
        })
        return constraint_lines


class VerticalFix(AbstractConstraint):
    """Keeps the y-coordinate of the vertex fixed"""

    def __init__(self, form, vertex):
        super().__init__(form)
        self.vertex = vertex
        self.set_initial_position()

    def set_initial_position(self):
        self.P = self.form.vertex_coordinates(self.vertex, 'xy')[1]

    def compute_constraint(self):
        constraint_jac_row = np.zeros((1, self.number_of_cols))
        idx = self.form.key_index()[self.vertex] + self.form.number_of_vertices()
        constraint_jac_row[0, idx] = 1
        r = self.form.vertex_coordinates(self.vertex, 'xy')[1] - self.P
        return constraint_jac_row, r

    def update_constraint_goal(self):
        self.set_initial_position()

    def get_lines(self):
        constraint_lines = []
        s = self.form.vertex_coordinates(self.vertex, 'xy')
        e = self.form.vertex_coordinates(self.vertex, 'xy')
        s[0] += 1
        e[0] -= 1
        constraint_lines.append({
            'start': s,
            'end': e,
            'width': self._width,
            'color': self._color,
            'style': self._style,
        })
        return constraint_lines


class LengthFix(AbstractConstraint):
    """Keeps the edge length fixed"""

    def __init__(self, form, edge):
        super().__init__(form)
        self.edge = edge
        self.set_initial_length()

    def update_constraint_goal(self):
        self.set_initial_length()

    def set_initial_length(self):
        u, v = list(self.form.edges())[self.edge]
        s = self.form.vertex_coordinates(u, 'xy')
        e = self.form.vertex_coordinates(v, 'xy')
        dx = s[0] - e[0]
        dy = s[1] - e[1]
        self.L = np.sqrt(dx ** 2 + dy ** 2)  # Initial length

    def compute_constraint(self):
        constraint_jac_row = np.zeros((1, self.number_of_cols))

        u, v = list(self.form.edges())[self.edge]
        s = self.form.vertex_coordinates(u, 'xy')
        e = self.form.vertex_coordinates(v, 'xy')
        dx = s[0] - e[0]
        dy = s[1] - e[1]
        l = np.sqrt(dx ** 2 + dy ** 2)  # Current length

        constraint_jac_row[0, u] = dx / l  # x0
        constraint_jac_row[0, v] = -dx / l  # x1
        constraint_jac_row[0, u + self.form.number_of_vertices()] = dy / l  # y0
        constraint_jac_row[0, v + self.form.number_of_vertices()] = -dy / l  # y1
        r = l - self.L

        return constraint_jac_row, r


class SetLength(LengthFix):
    """Sets the edge length to L"""

    def __init__(self, form, edge, L):
        super().__init__(form, edge)
        self.L = L

    def update_constraint_goal(self):
        pass


# ==============================================================================
# Main
# ==============================================================================

if __name__ == '__main__':
    pass
