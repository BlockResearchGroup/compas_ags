from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

import sys

from numpy import array
from numpy import float64
from numpy.linalg import lstsq
from numpy.linalg import norm

from scipy.sparse import diags

from compas.geometry import angle_vectors_xy

from compas.numerical import connectivity_matrix
from compas.numerical import equilibrium_matrix
from compas.numerical import spsolve_with_known
from compas.numerical import normrow
from compas.numerical import dof
from compas.numerical import rref_sympy as rref
from compas.numerical import nonpivots

from compas_ags.diagrams import FormDiagram
from compas_ags.diagrams import ForceDiagram

from compas_ags.ags.core import update_q_from_qind
from compas_ags.ags.core import update_form_from_force
from compas_ags.ags.core import get_jacobian_and_residual

from compas_ags.exceptions import SolutionError


__all__ = [
    'form_identify_dof',
    'form_count_dof',
    'form_update_q_from_qind',
    'form_update_from_force',
    'form_update_from_force_newton',
    'force_update_from_form',

    'form_update_q_from_qind_proxy',
    'form_update_from_force_proxy',
    'form_update_from_force_newton_proxy',
    'force_update_from_form_proxy',
]


EPS = 1 / sys.float_info.epsilon


# ==============================================================================
# proxy
# ==============================================================================


def form_update_q_from_qind_proxy(formdata, *args, **kwargs):
    form = FormDiagram.from_data(formdata)
    form_update_q_from_qind(form, *args, **kwargs)
    return form.to_data()


def form_update_from_force_proxy(formdata, forcedata, *args, **kwargs):
    form = FormDiagram.from_data(formdata)
    force = ForceDiagram.from_data(forcedata)
    form_update_from_force(form, force, *args, **kwargs)
    return form.to_data()


def force_update_from_form_proxy(forcedata, formdata, *args, **kwargs):
    form = FormDiagram.from_data(formdata)
    force = ForceDiagram.from_data(forcedata)
    force_update_from_form(force, form, *args, **kwargs)
    return force.to_data()


def form_update_from_force_newton_proxy(forcedata, formdata, *args, **kwargs):
    form = FormDiagram.from_data(formdata)
    force = ForceDiagram.from_data(forcedata)
    form_update_from_force_newton(force, form, *args, **kwargs)  # Still need dealing with constraints
    return force.to_data()


# ==============================================================================
# analysis form diagram
# ==============================================================================


def form_identify_dof(form):
    r"""Identify the DOF of a form diagram.

    Parameters
    ----------
    form: :class:`FormDiagram`
        The form diagram.

    Returns
    -------
    k : int
        Dimension of the null space (nullity) of the equilibrium matrix.
        Number of independent states of self-stress.
    m : int
        Size of the left null space of the equilibrium matrix.
        Number of (infenitesimal) mechanisms.
    ind : list
        Indices of the independent edges.

    Notes
    -----
    The equilibrium matrix of the form diagram is

    .. math::

        \mathbf{E}
        =
        \begin{bmatrix}
        \mathbf{C}_{i}^{t}\mathbf{U} \\
        \mathbf{C}_{i}^{t}\mathbf{V}
        \end{bmatrix}

    If ``k == 0`` and ``m == 0``, the system described by the equilibrium matrix is statically determined.
    If ``k > 0`` and ``m == 0``, the system is statically indetermined with `k` idependent states of stress.
    If ``k == 0`` and ``m > 0``, the system is unstable, with `m` independent mechanisms.

    The dimension of a vector space (such as the null space) is the number of
    vectors of a basis of that vector space. A set of vectors forms a basis of a
    vector space if they are linearly independent vectors and every vector of the
    space is a linear combination of this set.

    Examples
    --------
    >>>
    """
    vertex_index = form.vertex_index()

    xy = form.vertices_attributes('xy')
    fixed = [vertex_index[vertex] for vertex in form.fixed()]
    free = list(set(range(form.number_of_vertices())) - set(fixed))
    edges = [(vertex_index[u], vertex_index[v]) for u, v in form.edges()]
    C = connectivity_matrix(edges)
    E = equilibrium_matrix(C, xy, free)

    k, m = dof(E)
    ind = nonpivots(rref(E))

    return int(k), int(m), [edges[i] for i in ind]


def form_count_dof(form):
    r"""Count the number of degrees of freedom of a form diagram.

    Parameters
    ----------
    form: :class:`FormDiagram`
        The form diagram.

    Returns
    -------
    k : int
        Dimension of the null space (*nullity*) of the equilibrium matrix of the
        form diagram.
    m : int
        Dimension of the left null space of the equilibrium matrix of the form
        diagram.

    Notes
    -----
    The equilibrium matrix of the form diagram is

    .. math::

        \mathbf{E}
        =
        \begin{bmatrix}
        \mathbf{C}_{i}^{t}\mathbf{U} \\
        \mathbf{C}_{i}^{t}\mathbf{V}
        \end{bmatrix}

    Examples
    --------
    >>>
    """
    vertex_index = form.vertex_index()

    xy = form.vertices_attributes('xy')
    fixed = [vertex_index[vertex] for vertex in form.leaves()]
    free = list(set(range(form.number_of_vertices())) - set(fixed))
    edges = [(vertex_index[u], vertex_index[v]) for u, v in form.edges()]
    C = connectivity_matrix(edges)
    E = equilibrium_matrix(C, xy, free)

    k, m = dof(E)

    return int(k), int(m)


# ==============================================================================
# update form diagram
# ==============================================================================


def form_update_q_from_qind(form):
    """Update the force densities of the dependent edges of a form diagram using
    the values of the independent ones.

    Parameters
    ----------
    form: :class:`FormDiagram`
        The form diagram.

    Returns
    -------
    None
        The updated force densities are stored as attributes of the edges of the form diagram.

    Examples
    --------
    >>>
    """
    vertex_index = form.vertex_index()
    edge_index = form.edge_index()

    vcount = form.number_of_vertices()
    ecount = form.number_of_edges()
    fixed = form.leaves()
    fixed = [vertex_index[vertex] for vertex in fixed]
    free = list(set(range(vcount)) - set(fixed))
    ind = [edge_index[edge] for edge in form.ind()]
    dep = list(set(range(ecount)) - set(ind))
    edges = [(vertex_index[u], vertex_index[v]) for u, v in form.edges()]
    xy = array(form.xy(), dtype=float64).reshape((-1, 2))
    q = array(form.q(), dtype=float64).reshape((-1, 1))
    C = connectivity_matrix(edges, 'csr')
    E = equilibrium_matrix(C, xy, free, 'csr')

    update_q_from_qind(E, q, dep, ind)

    uv = C.dot(xy)
    lengths = normrow(uv)
    forces = q * lengths

    for edge in form.edges():
        index = edge_index[edge]
        form.edge_attributes(edge, ['q', 'f', 'l'], [q[index, 0], forces[index, 0], lengths[index, 0]])


def form_update_from_force(form, force, kmax=100):
    r"""Update the form diagram after a modification of the force diagram.

    Parameters
    ----------
    form: :class:`FormDiagram`
        The form diagram to update.
    force : :class:`ForceDiagram`
        The force diagram on which the update is based.

    Returns
    -------
    None
        The form and force diagram are updated in-place.

    Notes
    -----
    Compute the geometry of the form diagram from the geometry of the form diagram
    and some constraints (location of fixed points).
    Since both diagrams are reciprocal, the coordinates of each vertex of the form
    diagram can be expressed as the intersection of three or more lines parallel
    to the corresponding edges of the force diagram.
    Essentially, this boils down to solving the following problem:

    .. math::

        \mathbf{A}\mathbf{x} = \mathbf{b}

    with :math:`\mathbf{A}` the coefficients of the x and y-coordinate of the  ,
    :math:`\mathbf{x}` the coordinates of the vertices of the form diagram,
    in *Fortran* order (first all x-coordinates, then all y-coordinates),
    and  :math:`\mathbf{b}` ....

    Examples
    --------
    >>>
    """
    # --------------------------------------------------------------------------
    # form diagram
    # --------------------------------------------------------------------------
    vertex_index = form.vertex_index()
    edge_index = form.edge_index()
    i_j = {index: [vertex_index[nbr] for nbr in form.vertex_neighbors(vertex)] for index, vertex in enumerate(form.vertices())}
    ij_e = {(vertex_index[u], vertex_index[v]): edge_index[u, v] for u, v in edge_index}
    ij_e.update({(vertex_index[v], vertex_index[u]): edge_index[u, v] for u, v in edge_index})

    xy = array(form.xy(), dtype=float64)
    edges = [(vertex_index[u], vertex_index[v]) for u, v in form.edges()]
    C = connectivity_matrix(edges, 'csr')
    # --------------------------------------------------------------------------
    # constraints
    # --------------------------------------------------------------------------
    leaves = [vertex_index[vertex] for vertex in form.leaves()]
    fixed = [vertex_index[vertex] for vertex in form.fixed()]
    free = list(set(range(form.number_of_vertices())) - set(fixed) - set(leaves))
    fixed_x = [vertex_index[vertex] for vertex in form.fixed_x()]
    fixed_y = [vertex_index[vertex] for vertex in form.fixed_y()]
    # --------------------------------------------------------------------------
    # force diagram
    # --------------------------------------------------------------------------
    _vertex_index = force.vertex_index()
    _edge_index = force.edge_index(form)
    _edge_index.update({(v, u): _edge_index[u, v] for u, v in _edge_index})

    _xy = array(force.xy(), dtype=float64)
    _edges = force.ordered_edges(form)
    _edges[:] = [(_vertex_index[u], _vertex_index[v]) for u, v in _edges]
    _C = connectivity_matrix(_edges, 'csr')
    # --------------------------------------------------------------------------
    # compute the coordinates of thet *free* vertices
    # as a function of the fixed vertices and the previous coordinates of the *free* vertices
    # re-add the leaves and leaf-edges
    # --------------------------------------------------------------------------
    update_form_from_force(xy, _xy, free, fixed_x, fixed_y, leaves, i_j, ij_e, _C, kmax=kmax)
    # --------------------------------------------------------------------------
    # update
    # --------------------------------------------------------------------------
    uv = C.dot(xy)
    _uv = _C.dot(_xy)
    angles = [angle_vectors_xy(a, b, deg=True) for a, b in zip(uv, _uv)]
    lengths = normrow(uv)
    forces = normrow(_uv)
    q = forces / lengths
    # --------------------------------------------------------------------------
    # update form diagram
    # --------------------------------------------------------------------------
    for vertex, attr in form.vertices(True):
        index = vertex_index[vertex]
        attr['x'] = xy[index, 0]
        attr['y'] = xy[index, 1]
    for edge, attr in form.edges(True):
        index = edge_index[edge]
        attr['l'] = lengths[index, 0]
        attr['a'] = angles[index]
        if angles[index] < 90:
            attr['f'] = forces[index, 0]
            attr['q'] = q[index, 0]
        else:
            attr['f'] = - forces[index, 0]
            attr['q'] = - q[index, 0]
    # --------------------------------------------------------------------------
    # update force diagram
    # --------------------------------------------------------------------------
    for edge, attr in force.edges(True):
        index = _edge_index[edge]
        attr['a'] = angles[index]
        attr['l'] = forces[index, 0]


def form_update_from_force_newton(form, force, constraints=None, tol=1e-10, max_iter=20):
    r"""Update the form diagram after a modification of the force diagram.

    Compute the geometry of the form diagram from the geometry of the force diagram
    and some constraints, including non-linear.
    The form diagram is computed by formulating the root-finding approach presented
    in bi-dir AGS [1]_. Newton's method is used to solve for the form diagram.

    The algorithm fails if it is over-constrained or if the initial guess is too far
    from any root.

    Parameters
    ----------
    form: :class:`FormDiagram`
        The form diagram to update.
    force: :class:`ForceDiagram`
        The force diagram containing the vertex modification desired.
    constraints: :class:`ConstraintsCollection`, optional
        A collection of form diagram constraints.
        The default is ``None``, in which case no constraints are considered.
    tol: float, optional
        Stopping criteria tolerance.
        The default value is ``1e-10``.
    max_iter: int, optional
        Maximum number of iterations before stop Newton Method.
        The default value is ``20``.

    Returns
    -------
    None
        The form and force diagram are updated in-place.

    References
    ----------
    .. [1] Alic, V. and Åkesson, D., 2017. Bi-directional algebraic graphic statics. Computer-Aided Design, 93, pp.26-37.

    Examples
    --------
    >>>

    """
    X = array(form.vertices_attribute('x') + form.vertices_attribute('y')).reshape(-1, 1)
    _X_goal = array(force.vertices_attribute('x') + force.vertices_attribute('y')).reshape(-1, 1)

    vcount = form.number_of_vertices()
    index_vertex = form.index_vertex()

    # Begin Newton
    diff = 100
    n_iter = 1
    while diff > tol:
        # Update force diagram based on form at each iteration
        form_update_q_from_qind(form)
        force_update_from_form(force, form)

        # Get jacobian maxtrix and residual vector considering constraints
        red_jacobian, red_r = get_jacobian_and_residual(form, force, _X_goal, constraints)

        # Do the least squares solution
        dx = lstsq(red_jacobian, -red_r)[0]

        X = X + dx

        # Update form diagram at end of iteration
        for i in range(vcount):
            vertex = index_vertex[i]
            form.vertex_attribute(vertex, 'x', X[i].item())
            form.vertex_attribute(vertex, 'y', X[i + vcount].item())

        diff = norm(red_r)
        if n_iter > max_iter:
            raise SolutionError('Did not converge')

        print('i: {0:0} diff: {1:.2e}'.format(n_iter, float(diff)))
        n_iter += 1

    print('Converged in {0} iterations'.format(n_iter))


# ==============================================================================
# update force diagram
# ==============================================================================


def force_update_from_form(force, form):
    """Update the force diagram after modifying the (force densities of) the form diagram.

    Parameters
    ----------
    force : :class:`ForceDiagram`
        The force diagram on which the update is based.
    form : :class:`FormDiagram`
        The form diagram to update.

    Returns
    -------
    None
        The form and force diagram are updated in-place.
    """
    # --------------------------------------------------------------------------
    # form diagram
    # --------------------------------------------------------------------------
    vertex_index = form.vertex_index()

    xy = array(form.xy(), dtype=float64)
    edges = [[vertex_index[u], vertex_index[v]] for u, v in form.edges()]
    C = connectivity_matrix(edges, 'csr')
    Q = diags([form.q()], [0])
    uv = C.dot(xy)
    # --------------------------------------------------------------------------
    # force diagram
    # --------------------------------------------------------------------------
    _vertex_index = force.vertex_index()

    _known = [_vertex_index[force.anchor()]]
    _xy = array(force.xy(), dtype=float64)
    _edges = force.ordered_edges(form)
    _edges[:] = [(_vertex_index[u], _vertex_index[v]) for u, v in _edges]
    _C = connectivity_matrix(_edges, 'csr')
    _Ct = _C.transpose()
    # --------------------------------------------------------------------------
    # compute reciprocal for given q
    # --------------------------------------------------------------------------
    _xy = spsolve_with_known(_Ct.dot(_C), _Ct.dot(Q).dot(uv), _xy, _known)
    # --------------------------------------------------------------------------
    # update force diagram
    # --------------------------------------------------------------------------
    for vertex, attr in force.vertices(True):
        index = _vertex_index[vertex]
        attr['x'] = _xy[index, 0]
        attr['y'] = _xy[index, 1]


# ==============================================================================
# Main
# ==============================================================================

if __name__ == '__main__':
    pass
