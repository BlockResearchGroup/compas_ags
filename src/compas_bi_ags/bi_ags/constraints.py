from abc import ABC, abstractmethod

import numpy as np

from compas_ags.diagrams.formdiagram import FormDiagram

__author__    = ['Vedad Alic', ]
__license__   = 'MIT License'
__email__     = 'vedad.alic@construction.lth.se'

__all__ = [
    'ConstraintsCollection',
    'HorizontalFix',
    'VerticalFix'
]


class AbstractConstraint(ABC):
    """
    Used to derive form diagram constraints. The derived constraints
    must implement the compute_constraint method.
    """
    def __init__(self, form):
        super().__init__()
        self.form = form  # type: FormDiagram

        # --------------------------------------------------------------------------
        # Drawing properties
        # --------------------------------------------------------------------------
        self._color = '#1524c6'
        self._width = 1.0
        self._style = '--'

    @abstractmethod
    def compute_constraint(self):
        """Computes the residual and Jacobian matrix of the constraint.
        """
        pass

    @property
    def number_of_cols(self):
        vcount = self.form.number_of_vertices()
        return 2 * vcount

    def get_lines(self):
        """Get lines to draw in viewer."""
        pass


class ConstraintsCollection:
    """
    Computes the Jacobian d_X/dX and residual r of the added constraints
    where X contains the form diagram coordinates in *Fortran* order
    (first all x-coordinates, then all y-coordinates) and _X contains the
    force diagram coordinates in *Fortran* order (first all _x-coordinates,
    then all _y-coordinates)
    """
    def __init__(self):
        self.constraints = []

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

    def get_lines(self):
        """Get lines to draw in viewer."""
        lines = []
        for constraint in self.constraints:
            line = constraint.get_lines()
            if line:
                lines = lines + line
        return lines


class HorizontalFix(AbstractConstraint):
    """Keeps the x-coordinate of the vertex fixed"""
    def __init__(self, form, vertex):
        super().__init__(form)
        self.vertex = vertex

    def compute_constraint(self):
        constraint_jac_row = np.zeros((1, self.number_of_cols))
        idx = self.form.key_index()[self.vertex]
        constraint_jac_row[0, idx] = 1
        return constraint_jac_row, 0.0

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

    def compute_constraint(self):
        constraint_jac_row = np.zeros((1, self.number_of_cols))
        idx = self.form.key_index()[self.vertex] + self.form.number_of_vertices()
        constraint_jac_row[0, idx] = 1
        return constraint_jac_row, 0.0

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

