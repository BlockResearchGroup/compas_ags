from abc import ABC, abstractmethod
import numpy as np
import math


__all__ = [
    "ConstraintsCollection",
    "HorizontalFix",
    "VerticalFix",
    "AngleFix",
    "LengthFix",
    "SetLength",
]


class AbstractConstraint(ABC):
    """Base class for Form Diagram constraints.

    Parameters
    -----------
    form: :class:`FormDiagram`

    """

    def __init__(self, form):
        super().__init__()
        self.form = form
        self.vcount = form.number_of_vertices()
        self.vertex_index = form.vertex_index()
        self._color = (21, 36, 198)
        self._width = 1.0
        self._style = "--"

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
    then all _y-coordinates).

    Parameters
    -----------
    form: :class:`FormDiagram`

    References
    ----------
    .. [1] Alic, V. and Åkesson, D., 2017. Bi-directional algebraic graphic statics. Computer-Aided Design, 93, pp.26-37.

    """

    def __init__(self, form):
        self.constraints = []
        self.form = form

    def add_constraint(self, constraint):
        self.constraints.append(constraint)

    def compute_constraints(self):
        jac = np.zeros((0, self.constraints[0].number_of_cols))
        res = np.zeros((0, 1))
        for constraint in self.constraints:
            j, r = constraint.compute_constraint()
            jac = np.vstack((jac, j))
            res = np.vstack((res, r))
        return jac, res

    def update_constraints(self):
        for constraint in self.constraints:
            constraint.update_constraint_goal()

    def constraints_from_form(self):
        """Automate set up of constraint collection based on diagram's attributes"""

        # fix x and y coordinates of the fixed vertices
        for key in self.form.vertices_where({"is_fixed": True}):
            self.add_constraint(HorizontalFix(self.form, key))
            self.add_constraint(VerticalFix(self.form, key))

        # fix x or y coordinates of the non-fixed vertices
        for key in self.form.vertices_where({"is_fixed_x": True, "is_fixed": False}):
            self.add_constraint(HorizontalFix(self.form, key))
        for key in self.form.vertices_where({"is_fixed_y": True, "is_fixed": False}):
            self.add_constraint(VerticalFix(self.form, key))

        self.constrain_dependent_leaf_edges_lengths()

    def get_lines(self):
        """Get lines to draw in viewer."""
        lines = []
        for constraint in self.constraints:
            constraint_lines = constraint.get_lines()
            if constraint_lines:
                lines = lines + constraint_lines
        return lines

    def constrain_dependent_leaf_edges_lengths(self):
        leaves = self.form.leaves()
        dependent_leaf_edges = []
        for i, (u, v) in enumerate(self.form.edges()):
            if u in leaves or v in leaves:
                if not self.form.edge_attribute((u, v), "is_ind"):
                    dependent_leaf_edges.append((u, v))
        for edge in dependent_leaf_edges:
            self.add_constraint(LengthFix(self.form, edge))


class HorizontalFix(AbstractConstraint):
    """Constraint that keeps x-coordinate of a vertex fixed.

    Parameters
    -----------
    form: :class:`FormDiagram`
        The Form Diagram to constraint
    vertex: int
        Idenfifier ofthe vertex to fix.

    """

    def __init__(self, form, vertex):
        super().__init__(form)
        self.vertex = vertex
        self.x = None
        self.set_initial_position()

    def set_initial_position(self):
        self.x = self.form.vertex_attribute(self.vertex, "x")

    def compute_constraint(self):
        constraint_jac_row = np.zeros((1, self.number_of_cols))
        idx = self.vertex_index[self.vertex]
        constraint_jac_row[0, idx] = 1
        r = self.form.vertex_attribute(self.vertex, "x") - self.x
        return constraint_jac_row, r

    def update_constraint_goal(self):
        self.set_initial_position()

    def get_lines(self):
        constraint_lines = []
        s = self.form.vertex_coordinates(self.vertex, "xy")
        e = self.form.vertex_coordinates(self.vertex, "xy")
        s[1] += 1
        e[1] -= 1
        constraint_lines.append(
            {
                "start": s,
                "end": e,
                "width": self._width,
                "color": self._color,
                "style": self._style,
            }
        )
        return constraint_lines


class VerticalFix(AbstractConstraint):
    """Constraint that keeps y-coordinate of a vertex fixed.

    Parameters
    -----------
    form: :class:`FormDiagram`
        The Form Diagram to constraint
    vertex: int
        Idenfifier ofthe vertex to fix.

    """

    def __init__(self, form, vertex):
        super().__init__(form)
        self.vertex = vertex
        self.y = None
        self.set_initial_position()

    def set_initial_position(self):
        self.y = self.form.vertex_attribute(self.vertex, "y")

    def compute_constraint(self):
        constraint_jac_row = np.zeros((1, self.number_of_cols))
        idx = self.vertex_index[self.vertex] + self.vcount
        constraint_jac_row[0, idx] = 1
        r = self.form.vertex_attribute(self.vertex, "y") - self.y
        return constraint_jac_row, r

    def update_constraint_goal(self):
        self.set_initial_position()

    def get_lines(self):
        constraint_lines = []
        s = self.form.vertex_coordinates(self.vertex, "xy")
        e = self.form.vertex_coordinates(self.vertex, "xy")
        s[0] += 1
        e[0] -= 1
        constraint_lines.append(
            {
                "start": s,
                "end": e,
                "width": self._width,
                "color": self._color,
                "style": self._style,
            }
        )
        return constraint_lines


class AngleFix(AbstractConstraint):
    """Constraint that keeps vertex fixed along an inclined line.

    Parameters
    -----------
    form: :class:`FormDiagram`
        The Form Diagram to constraint
    vertex: int
        Idenfifier ofthe vertex to fix.
    angle: float
        Angle (clockwise) to fix the vertex to.

    """

    def __init__(self, form, vertex, angle):
        super().__init__(form)
        self.vertex = vertex
        self.angle = angle
        self.x = None
        self.y = None
        self.set_initial_position()

    def set_initial_position(self):
        self.x = self.form.vertex_attribute(self.vertex, "x")
        self.y = self.form.vertex_attribute(self.vertex, "y")

    def compute_constraint(self):
        constraint_jac_row = np.zeros((1, self.number_of_cols))

        theta = math.radians(self.angle)

        idx = self.vertex_index[self.vertex]
        constraint_jac_row[0, idx] = 1 * math.sin(theta)
        r = (self.form.vertex_attribute(self.vertex, "x") - self.x) * math.sin(theta)

        idx = self.vertex_index[self.vertex] + self.vcount
        constraint_jac_row[0, idx] = 1 * math.cos(theta)
        r = (self.form.vertex_attribute(self.vertex, "y") - self.y) * math.cos(theta)
        return constraint_jac_row, r

    def update_constraint_goal(self):
        self.set_initial_position()

    def get_lines(self):
        constraint_lines = []
        s = self.form.vertex_coordinates(self.vertex, "xy")
        e = self.form.vertex_coordinates(self.vertex, "xy")
        theta = math.radians(90 - self.angle)
        s[0] += 1 * math.sin(theta)
        s[1] -= 1 * math.cos(theta)
        e[0] -= 1 * math.sin(theta)
        e[1] += 1 * math.cos(theta)
        constraint_lines.append(
            {
                "start": s,
                "end": e,
                "width": self._width,
                "color": self._color,
                "style": self._style,
            }
        )
        return constraint_lines


class LengthFix(AbstractConstraint):
    """Constraint that keeps the edge length fixed.

    Parameters
    -----------
    form: :class:`FormDiagram`
        The Form Diagram to constraint
    edge : 2-tuple of int
        The identifier of the edge as a pair of vertex identifiers.

    """

    def __init__(self, form, edge):
        super().__init__(form)
        self.edge = edge
        self.length = None
        self.set_initial_length()

    def update_constraint_goal(self):
        self.set_initial_length()

    def set_initial_length(self):
        self.length = self.form.edge_length(*self.edge)  # Initial length

    def compute_constraint(self):
        constraint_jac_row = np.zeros((1, self.number_of_cols))

        s, e = self.form.edge_coordinates(*self.edge)
        dx = s[0] - e[0]
        dy = s[1] - e[1]
        length = math.sqrt(dx**2 + dy**2)  # Current length

        id_u = self.vertex_index[self.edge[0]]
        id_v = self.vertex_index[self.edge[1]]

        constraint_jac_row[0, id_u] = dx / length  # x0
        constraint_jac_row[0, id_v] = -dx / length  # x1
        constraint_jac_row[0, id_u + self.vcount] = dy / length  # y0
        constraint_jac_row[0, id_v + self.vcount] = -dy / length  # y1
        r = length - self.length

        return constraint_jac_row, r


class SetLength(LengthFix):
    """WIP - Constraint that sets the edge length to L.

    Parameters
    -----------
    form: :class:`FormDiagram`
        The Form Diagram to constraint
    edge : 2-tuple of int
        The identifier of the edge as a pair of vertex identifiers.
    length: float
        Length to set to the edge.

    """

    def __init__(self, form, edge, length):
        super().__init__(form, edge)
        self.length = length

    def update_constraint_goal(self):
        pass


class SetOrientation(AbstractConstraint):
    """WIP - Constraint that sets the edge orientation.

    Parameters
    -----------
    form: :class:`FormDiagram`
        The Form Diagram to constraint
    edge : 2-tuple of int
        The identifier of the edge as a pair of vertex identifiers.
    angle: float
        Angle to orient the edge to set to the edge.

    """

    def __init__(self, form, edge, angle):
        super().__init__(form)
        self.edge = edge
        self.angle = angle


# ==============================================================================
# Main
# ==============================================================================

if __name__ == "__main__":
    pass
