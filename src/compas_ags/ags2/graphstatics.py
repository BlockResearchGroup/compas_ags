from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

import sys

# try:
#     from numpy import array
#     from numpy import eye
#     from numpy import zeros
#     from numpy import float64
#     from numpy.linalg import cond
#     from numpy import matrix
#     from scipy.linalg import solve
#     from scipy.linalg import lstsq

#     from scipy.sparse import diags
# except ImportError:
#     if 'ironpython' not in sys.version.lower():
#         raise

from numpy import array
from numpy import eye
from numpy import zeros
from numpy import float64
from numpy.linalg import cond
from numpy import matrix
from scipy.linalg import solve
from scipy.linalg import lstsq

from scipy.sparse import diags

from compas_ags.ags.graphstatics import *
from compas.geometry import angle_vectors_xy
from compas.numerical import connectivity_matrix
from compas.numerical import equilibrium_matrix
from compas.numerical import normrow
from compas.numerical import laplacian_matrix



__author__     = ['Vedad Alic', ]
__license__    = 'MIT license'
__email__      = 'vedad.alic@outlook.com'


__all__ = [
    'form_update_from_force_direct'
]


EPS  = 1 / sys.float_info.epsilon



def form_update_from_force_direct(form, force):
    r"""Update the form diagram after a modification of the force diagram.

    Compute the geometry of the form diagram from the geometry of the force diagram
    and some constraints (location of fixed points).
    The form diagram is computed by formulating the reciprocal relationships to
    the approach in described in AGS. In order to include the constraints, the
    reciprocal force densities and form diagram coordinates are solved for at
    the same time, by formulating the equation system:

    .. math::

        \mathbf{M}\mathbf{X} = \mathbf{r}

    with :math:`\mathbf{M}` containing the coefficients of the system of equations
    including constraints, :math:`\mathbf{X}` the coordinates of the vertices of
    the form diagram and the reciprocal force densities, in *Fortran* order
    (first all :math:`\mathbf{x}`-coordinates, then all :math:`\mathbf{y}`-coordinates, then all reciprocal force
    densities, :math:`\mathbf{q}^{-1}`), and  :math:`\mathbf{r}` contains the residual (all zeroes except
    for the constraint rows).

    The addition of constraints reduces the number of independent edges, which
    must be identified during the solving procedure. Additionally, the algorithm
    fails if any force density is zero (corresponding to a zero-length edge in
    the force diagram) or if it is over-constrained.

    Parameters
    ----------
    form : compas_ags.diagrams.formdiagram.FormDiagram
        The form diagram to update.
    force : compas_ags.diagrams.forcediagram.ForceDiagram
        The force diagram on which the update is based.

    """
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
    from compas_ags.utilities.errorhandler import SolutionError
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
    nr_free_vars, free_vars, dependent_vars = get_independent_stress(M)
    #k, m  = dof(M)
    #ind   = nonpivots(rref(M))

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