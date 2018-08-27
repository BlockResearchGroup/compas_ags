from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

import sys

try:
    from numpy import array
    from numpy import eye
    from numpy import zeros
    from numpy import float64
    from numpy.linalg import cond
    from numpy import matrix
    from scipy.linalg import solve
    from scipy.linalg import lstsq

    from scipy.sparse import diags
except ImportError:
    if 'ironpython' not in sys.version.lower():
        raise    

from compas.geometry import angle_vectors_xy

from compas.numerical import connectivity_matrix
from compas.numerical import equilibrium_matrix
from compas.numerical import spsolve_with_known
from compas.numerical import normrow
from compas.numerical import normalizerow
from compas.numerical import dof
from compas.numerical import rref_sympy as rref
from compas.numerical import nonpivots

from compas_ags.ags import update_q_from_qind
from compas_ags.ags import update_form_from_force
from compas.numerical import laplacian_matrix


__author__     = ['Tom Van Mele', ]
__copyright__  = 'Copyright 2014, BLOCK Research Group - ETH Zurich'
__license__    = 'MIT license'
__email__      = 'vanmelet@ethz.ch'


__all__ = [
    'form_identify_dof',
    'form_identify_dof_xfunc',
    'form_count_dof',
    'form_count_dof_xfunc',
    'form_update_q_from_qind',
    'form_update_q_from_qind_xfunc',
    'form_update_from_force',
    'form_update_from_force_xfunc',

    'force_update_from_form',
    'force_update_from_form_xfunc',
    'form_update_from_force_direct'
]


EPS  = 1 / sys.float_info.epsilon


# ==============================================================================
# xfuncs
# ==============================================================================


def form_identify_dof_xfunc(formdata, *args, **kwargs):
    from compas_tna.diagrams import FormDiagram
    form = FormDiagram.from_data(formdata)
    return form_identify_dof(form, *args, **kwargs)


def form_count_dof_xfunc(formdata, *args, **kwargs):
    from compas_tna.diagrams import FormDiagram
    form = FormDiagram.from_data(formdata)
    return form_count_dof(form, *args, **kwargs)


def form_update_q_from_qind_xfunc(formdata, *args, **kwargs):
    from compas_ags.diagrams import FormDiagram
    form = FormDiagram.from_data(form)
    form_update_q_from_qind(form, *args, **kwargs)
    return form.to_data()


def form_update_from_force_xfunc(form, force, *args, **kwargs):
    from compas_ags.diagrams import FormDiagram
    from compas_ags.diagrams import ForceDiagram
    form = FormDiagram.from_data(form)
    force = ForceDiagram.from_data(force)
    form_update_from_force(form, force, *args, **kwargs)
    return form.to_data()


def force_update_from_form_xfunc(force, form, *args, **kwargs):
    from compas_ags.diagrams import FormDiagram
    from compas_ags.diagrams import ForceDiagram
    form = FormDiagram.from_data(form)
    force = ForceDiagram.from_data(force)
    force_update_from_form(force, form, *args, **kwargs)
    return force.to_data()


# ==============================================================================
# analysis form diagram
# ==============================================================================


def form_identify_dof(form):
    r"""Identify the DOF of a form diagram.

    Parameters
    ----------
    form : FormDiagram
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


    If ``k == 0`` and ``m == 0``, the system described by the equilibrium matrix
    is statically determined.
    If ``k > 0`` and ``m == 0``, the system is statically indetermined with `k`
    idependent states of stress.
    If ``k == 0`` asnd ``m > 0``, the system is unstable, with `m` independent
    mechanisms.

    The dimension of a vector space (such as the null space) is the number of
    vectors of a basis of that vector space. A set of vectors forms a basis of a
    vector space if they are linearly independent vectors and every vector of the
    space is a linear combination of this set.

    References
    ----------
    ...

    See Also
    --------
    :func:`count_dof`

    Examples
    --------
    .. code-block:: python

        #

    """
    k_i   = form.key_index()
    xy    = form.get_vertices_attributes('xy')
    fixed = [k_i[key] for key in form.fixed()]
    free  = list(set(range(len(form.vertex))) - set(fixed))
    edges = [(k_i[u], k_i[v]) for u, v in form.edges_where({'is_edge': True})]
    C     = connectivity_matrix(edges)
    E     = equilibrium_matrix(C, xy, free)
    k, m  = dof(E)
    ind   = nonpivots(rref(E))
    return k, m, [edges[i] for i in ind]


def form_count_dof(form):
    r"""Count the number of degrees of freedom of a form diagram.

    Parameters
    ----------
    form : FormDiagram
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

    References
    ----------
    ...

    See Also
    --------
    :func:`identify_dof`

    Examples
    --------
    .. code_block:: python

        #

    """
    k_i   = form.key_index()
    xy    = form.get_vertices_attributes('xy')
    fixed = [k_i[key] for key in form.fixed()]
    free  = list(set(range(len(form.vertex))) - set(fixed))
    edges = [(k_i[u], k_i[v]) for u, v in form.edges_where({'is_edge': True})]
    C     = connectivity_matrix(edges)
    E     = equilibrium_matrix(C, xy, free)
    k, m  = dof(E)
    return k, m


# ==============================================================================
# update form diagram
# ==============================================================================


def form_update_q_from_qind(form):
    """Update the force densities of the dependent edges of a form diagram using
    the values of the independent ones.

    Parameters
    ----------
    form : FormDiagram
        The form diagram.

    Returns
    -------
    None

    Notes
    -----
    The force densities are stored as attributes of the edges.

    Examples
    --------
    .. code-block:: python

        #

    """
    k_i      = form.key_index()
    uv_index = form.uv_index()
    vcount   = form.number_of_vertices()
    ecount   = form.number_of_edges()
    fixed    = form.leaves()
    fixed    = [k_i[key] for key in fixed]
    free     = list(set(range(vcount)) - set(fixed))
    ind      = [index for index, (u, v, attr) in enumerate(form.edges(True)) if attr['is_ind']]
    dep      = list(set(range(ecount)) - set(ind))
    edges    = [(k_i[u], k_i[v]) for u, v in form.edges()]
    xy       = array(form.xy(), dtype=float64).reshape((-1, 2))
    q        = array(form.q(), dtype=float64).reshape((-1, 1))
    C        = connectivity_matrix(edges, 'csr')
    E        = equilibrium_matrix(C, xy, free, 'csr')

    update_q_from_qind(E, q, dep, ind)

    uv = C.dot(xy)
    l  = normrow(uv)
    f  = q * l

    for u, v, attr in form.edges(True):
        index = uv_index[(u, v)]
        attr['q'] = q[index, 0]
        attr['f'] = f[index, 0]
        attr['l'] = l[index, 0]


def form_update_from_force(form, force, kmax=100):
    r"""Update the form diagram after a modification of the force diagram.

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


    Parameters
    ----------
    form : compas_ags.formdiagram.FormDiagram
        The form diagram to update.
    force : compas_ags.forcediagram.ForceDiagram
        The force diagram on which the update is based.

    """
    # --------------------------------------------------------------------------
    # form diagram
    # --------------------------------------------------------------------------
    k_i    = form.key_index()
    #i_j    = {i: [k_i[n] for n in form.vertex_neighbours(k)] for i, k in enumerate(form.vertices())}
    uv_e   = form.uv_index()
    ij_e   = {(k_i[u], k_i[v]): uv_e[(u, v)] for u, v in uv_e}
    xy     = array(form.xy(), dtype=float64)
    edges  = [(k_i[u], k_i[v]) for u, v in form.edges()]
    C      = connectivity_matrix(edges, 'csr')
    # add opposite edges for convenience...
    ij_e.update({(k_i[v], k_i[u]): uv_e[(u, v)] for u, v in uv_e})
    # --------------------------------------------------------------------------
    # constraints
    # --------------------------------------------------------------------------
    leaves = [k_i[key] for key in form.leaves()]
    fixed  = [k_i[key] for key in form.fixed()]
    free   = list(set(range(form.number_of_vertices())) - set(fixed) - set(leaves))
    # --------------------------------------------------------------------------
    # force diagram
    # --------------------------------------------------------------------------
    _i_k   = {index: key for index, key in enumerate(force.vertices())}
    _xy    = array(force.xy(), dtype=float64)
    _edges = force.ordered_edges(form)
    _uv_e  = {(_i_k[i], _i_k[j]): e for e, (i, j) in enumerate(_edges)}
    _C     = connectivity_matrix(_edges, 'csr')
    # --------------------------------------------------------------------------
    # compute the coordinates of thet *free* vertices
    # as a function of the fixed vertices and the previous coordinates of the *free* vertices
    # re-add the leaves and leaf-edges
    # --------------------------------------------------------------------------
    update_form_from_force(xy, _xy, free, leaves, i_j, ij_e, _C, kmax=kmax)
    # --------------------------------------------------------------------------
    # update
    # --------------------------------------------------------------------------
    uv  = C.dot(xy)
    _uv = _C.dot(_xy)
    a   = [angle_vectors_xy(uv[i], _uv[i]) for i in range(len(edges))]
    l   = normrow(uv)
    _l  = normrow(_uv)
    q   = _l / l
    # --------------------------------------------------------------------------
    # update form diagram
    # --------------------------------------------------------------------------
    for key, attr in form.vertices(True):
        index = k_i[key]
        attr['x'] = xy[index, 0]
        attr['y'] = xy[index, 1]
    for u, v, attr in form.edges(True):
        e = uv_e[(u, v)]
        attr['l'] = l[e, 0]
        attr['a'] = a[e]
        if a[e] < 90:
            attr['f'] = _l[e, 0]
            attr['q'] = q[e, 0]
        else:
            attr['f'] = - _l[e, 0]
            attr['q'] = - q[e, 0]
    # --------------------------------------------------------------------------
    # update force diagram
    # --------------------------------------------------------------------------
    for u, v, attr in force.edges(True):
        e = _uv_e[(u, v)]
        attr['a'] = a[e]
        attr['l'] = _l[e, 0]


# ==============================================================================
# update force diagram
# ==============================================================================


def force_update_from_form(force, form):
    """Update the force diagram after modifying the (force densities of) the form diagram."""
    # --------------------------------------------------------------------------
    # form diagram
    # --------------------------------------------------------------------------
    k_i   = form.key_index()
    xy    = array(form.xy(), dtype=float64)
    edges = [[k_i[u], k_i[v]] for u, v in form.edges()]
    C     = connectivity_matrix(edges, 'csr')
    Q     = diags([form.q()], [0])
    uv    = C.dot(xy)
    # --------------------------------------------------------------------------
    # force diagram
    # --------------------------------------------------------------------------
    _k_i   = force.key_index()
    _known = [_k_i[force.anchor()]]
    _xy    = array(force.xy(), dtype=float64)
    _edges = force.ordered_edges(form)
    _C     = connectivity_matrix(_edges, 'csr')
    _Ct    = _C.transpose()
    # --------------------------------------------------------------------------
    # compute reciprocal for given q
    # --------------------------------------------------------------------------
    _xy = spsolve_with_known(_Ct.dot(_C), _Ct.dot(Q).dot(uv), _xy, _known)
    # --------------------------------------------------------------------------
    # update force diagram
    # --------------------------------------------------------------------------
    for key, attr in force.vertices(True):
        i = _k_i[key]
        attr['x'] = _xy[i, 0]
        attr['y'] = _xy[i, 1]



def form_update_from_force_direct(form, force):
    # --------------------------------------------------------------------------
    # form diagram
    # --------------------------------------------------------------------------
    k_i = form.key_index()
    # i_j = {i: [k_i[n] for n in form.vertex_neighbours(k)] for i, k in enumerate(form.vertices())}
    uv_e = form.uv_index()
    ij_e = {(k_i[u], k_i[v]): uv_e[(u, v)] for u, v in uv_e}
    edges = [(k_i[u], k_i[v]) for u, v in form.edges()]
    C = connectivity_matrix(edges, 'array')
    # add opposite edges for convenience...
    ij_e.update({(k_i[v], k_i[u]): uv_e[(u, v)] for u, v in uv_e})
    edges = [(k_i[u], k_i[v]) for u, v in form.edges()]
    xy = array(form.xy(), dtype=float64).reshape((-1, 2))
    q = array(form.q(), dtype=float64).reshape((-1, 1))
    # --------------------------------------------------------------------------
    # force diagram
    # --------------------------------------------------------------------------
    _i_k = {index: key for index, key in enumerate(force.vertices())}
    _xy = array(force.xy(), dtype=float64)
    _edges = force.ordered_edges(form)
    _uv_e = {(_i_k[i], _i_k[j]): e for e, (i, j) in enumerate(_edges)}
    _vcount = force.number_of_vertices()
    _C = connectivity_matrix(_edges, 'array')
    _e_v = force.external_vertices(form)
    _free = list(set(range(_vcount)) - set(_e_v))

    # --------------------------------------------------------------------------
    # compute the coordinates of the form based on the force diagram
    # with linear constraints
    # --------------------------------------------------------------------------

    # Compute dual equilibrium matrix and Laplacian matrix
    import numpy as np
    _E = equilibrium_matrix(_C, _xy, _free, 'array')
    L = laplacian_matrix(edges, normalize=False, rtype='array')

    # Get dual coordinate difference vectors
    _uv = _C.dot(_xy)
    _U = np.diag(_uv[:, 0])
    _V = np.diag(_uv[:, 1])

    # Get reciprocal force densities
    from compas_ags.utilities.errorHandler import SolutionError
    if any(abs(q) < 1e-14):
        raise SolutionError('Found zero force density, direct solution not possible.')
    q = np.divide(1, q)

    # Formulate the equation system
    z = np.zeros(L.shape)
    z2 = np.zeros((_E.shape[0], L.shape[1]))
    M = np.bmat([[L, z, -C.T.dot(_U)],
                 [z, L, -C.T.dot(_V)],
                 [z2, z2, _E]])
    rhs = np.zeros((M.shape[0], 1))
    X = np.vstack((matrix(xy)[:, 0], matrix(xy)[:, 1], matrix(q)[:, 0]))

    # Add constraints
    constraint_rows, res = force.compute_constraints(form, M)
    M = np.vstack((M, constraint_rows))
    rhs = np.vstack((rhs, res))

    # Get independent variables
    from compas_ags.utilities.helpers import get_independent_stress, check_solutions
    nr_free_edges_force, free_vars, dependent_vars = get_independent_stress(
        M)

    # Partition system
    Mid = M[:, free_vars]
    Md = M[:, dependent_vars]
    Xid = X[free_vars]

    # Check that solution exists
    check_solutions(M, rhs)

    # Solve
    Xd = np.asarray(np.linalg.lstsq(Md, rhs - Mid * Xid)[0])
    X[dependent_vars] = Xd

    # Store solution
    nx = xy.shape[0]
    ny = xy.shape[0]
    xy[:, 0] = X[:nx].T
    xy[:, 1] = X[nx:(nx + ny)].T

    # --------------------------------------------------------------------------
    # update
    # --------------------------------------------------------------------------
    uv = C.dot(xy)
    _uv = _C.dot(_xy)
    a = [angle_vectors_xy(uv[i], _uv[i]) for i in range(len(edges))]
    l = normrow(uv)
    _l = normrow(_uv)
    q = _l / l
    # --------------------------------------------------------------------------
    # update form diagram
    # --------------------------------------------------------------------------
    for key, attr in form.vertices(True):
        index = k_i[key]
        attr['x'] = xy[index, 0]
        attr['y'] = xy[index, 1]
    for u, v, attr in form.edges(True):
        e = uv_e[(u, v)]
        attr['l'] = l[e, 0]
        attr['a'] = a[e]
        if a[e] < 90:
            attr['f'] = _l[e, 0]
            attr['q'] = q[e, 0]
        else:
            attr['f'] = - _l[e, 0]
            attr['q'] = - q[e, 0]
    # --------------------------------------------------------------------------
    # update force diagram
    # --------------------------------------------------------------------------
    for u, v, attr in force.edges(True):
        e = _uv_e[(u, v)]
        attr['a'] = a[e]
        attr['l'] = _l[e, 0]


# ==============================================================================
# Debugging
# ==============================================================================

if __name__ == "__main__":

    pass
