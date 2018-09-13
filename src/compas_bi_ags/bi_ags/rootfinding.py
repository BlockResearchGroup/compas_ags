from compas_ags.ags.graphstatics import *

import sys

try:
    from numpy import array
    from numpy import eye
    from numpy import zeros
    from numpy import float64
    from numpy import matrix
    from numpy.linalg import cond

    from scipy.linalg import solve
    from scipy.linalg import lstsq

    from scipy.sparse import diags
except ImportError:
    if 'ironpython' not in sys.version.lower():
        raise


from compas.geometry import angle_vectors_xy

from compas.numerical import connectivity_matrix
from compas.numerical import equilibrium_matrix
from compas.numerical import normrow
from compas.numerical import laplacian_matrix
from compas.numerical import spsolve_with_known
from compas.numerical import solve_with_known

import compas_bi_ags.utilities.errorhandler as eh
import compas_bi_ags.utilities.helpers as hlp
from compas_ags.ags.graphstatics import form_update_q_from_qind, force_update_from_form

__author__    = ['Vedad Alic', ]
__license__   = 'MIT License'
__email__     = 'vedad.alic@construction.lth.se'

__all__ = [
    'compute_jacobian',
    'get_red_residual_and_jacobian',
    'update_coordinates',
    'compute_form_from_force_newton'
]

import numpy as np


def compute_form_from_force_newton(form, force, _X_goal, tol=1e5, constraints=None):
    r"""Update the form diagram after a modification of the force diagram.

    Compute the geometry of the form diagram from the geometry of the force diagram
    and some constraints, including non-linear.
    The form diagram is computed by formulating the root-finding approach presented
    in bi-dir AGS. Newton's method is used to solve for the form diagram.

    The algorithm fails if it is over-constrained or if the initial guess is too far
    from any root.

    Parameters
    ----------
    form : compas_ags.formdiagram.FormDiagram
        The form diagram to update.
    force : compas_bi_ags.diagrams.forcediagram.ForceDiagram
        The force diagram on which the update is based.
    _X_goal
        Contains the target force diagram coordinates in *Fortran* order (first all _x-coordinates, then all _y-coordinates).
    tol
    constraints : compas_bi_ags.bi_ags.constraints.ConstraintsCollection
        A collection of form diagram constraints,
    """
    xy = array(form.xy(), dtype=float64).reshape((-1, 2))
    X = np.vstack((np.asmatrix(xy[:, 0]).transpose(), np.asmatrix(xy[:, 1]).transpose()))

    eps = np.spacing(1)

    # Check if the anchored vertex of the force diagram should be moved
    _vcount = force.number_of_vertices()
    _k_i = force.key_index()
    _known = _k_i[force.anchor()]
    _bc = [_known, _vcount + _known]
    _xy = array(force.xy(), dtype=float64)
    _xy_goal = _X_goal.reshape((2, -1)).T
    r = np.vstack((np.asmatrix(_xy[:, 0]).transpose(), np.asmatrix(_xy[:, 1]).transpose())) - _X_goal
    if np.linalg.norm(r[_bc]) > eps*1e2:
        update_coordinates(force, _xy_goal)  # Move the anchored vertex

    # Begin Newton
    diff = 100
    n_iter = 1
    while diff > (eps * tol):
        red_jacobian, red_r, zero_columns = get_red_residual_and_jacobian(form, force, _X_goal, constraints)

        # Do the least squares solution
        dx = np.linalg.lstsq(red_jacobian, -red_r)[0]

        # Add back zeros for zero columns
        for zero_column in zero_columns:
            dx = np.insert(dx, zero_column, 0.0, axis=0)

        X = X + dx

        xy = X.reshape((2, -1)).T
        update_coordinates(form, xy)

        diff = np.linalg.norm(red_r)
        if n_iter > 20:
            raise eh.SolutionError('Did not converge')

        print('i: {0:0} diff: {1:.2e}'.format(n_iter, float(diff)))
        n_iter += 1

    print('Converged in {0} iterations'.format(n_iter))


def get_red_residual_and_jacobian(form, force, _X_goal, constraints=None):
    r"""Compute the Jacobian and residual.

    Computes the residual and the Jacobian :math:`\partial \mathbf{X}^* / \partial \mathbf{X}`
    where :math:`\mathbf{X}` contains the form diagram coordinates in *Fortran* order
    (first all :math:`\mathbf{x}`-coordinates, then all :math:`\mathbf{y}`-coordinates) and :math:`\mathbf{X}^*` contains the
    force diagram coordinates in *Fortran* order (first all :math:`\mathbf{x}^*`-coordinates,
    then all :math:`\mathbf{y}^*`-coordinates).

    Parameters
    ----------
    form : compas_ags.formdiagram.FormDiagram
        The form diagram to update.
    force : compas_ags.forcediagram.ForceDiagram
        The force diagram on which the update is based.
    _X_goal
        contains the target force diagram coordinates in *Fortran* order (first all _x-coordinates, then all _y-coordinates).
    constraints : compas_ags.ags.constraints.ConstraintsCollection
        A collection of form diagram constraints,

    Returns
    -------
    red_jacobian
        Jacobian with the rows corresponding the the anchor vertex remove and zero columns removed
    red_r
        Residual with the rows corresponding the the anchor vertex removed
    zero_columns
        Indices of removed columns from Jacobian
    """

    # TODO: Scramble vertices

    jacobian = compute_jacobian(form, force)

    _vcount = force.number_of_vertices()
    _k_i = force.key_index()
    _known = _k_i[force.anchor()]
    _bc = [_known, _vcount + _known]
    _xy = array(force.xy(), dtype=float64)
    r = np.vstack((np.asmatrix(_xy[:, 0]).transpose(), np.asmatrix(_xy[:, 1]).transpose())) - _X_goal

    if constraints:
        (cj, cr) = constraints.compute_constraints()
        jacobian = np.vstack((jacobian, cj))
        r = np.vstack((r, cr))

    hlp.check_solutions(jacobian, r)
    # Remove rows due to fixed vertex in the force diagram
    red_r = np.delete(r, _bc, axis=0)
    red_jacobian = np.delete(jacobian, _bc, axis=0)
    # Remove zero columns from jacobian
    zero_columns = []
    for i, jacobian_column in enumerate(np.sum(np.abs(jacobian), axis=0)):
        if jacobian_column < 1e-5:
            zero_columns.append(i)
    red_jacobian = np.delete(red_jacobian, zero_columns, axis=1)
    return red_jacobian, red_r, zero_columns


def compute_jacobian(form, force):
    r"""Compute the Jacobian matrix.

    The actual computation of the Jacobian :math:`\partial \mathbf{X}^* / \partial \mathbf{X}`
    where :math:`\mathbf{X}` contains the form diagram coordinates in *Fortran* order
    (first all :math:`\mathbf{x}`-coordinates, then all :math:`\mathbf{y}`-coordinates) and :math:`\mathbf{X}^*` contains the
    force diagram coordinates in *Fortran* order (first all :math:`\mathbf{x}^*`-coordinates,
    then all :math:`\mathbf{y}^*`-coordinates).

    Parameters
    ----------
    form : compas_ags.diagrams.formdiagram.FormDiagram
        The form diagram.
    force : compas_bi_ags.diagrams.forcediagram.ForceDiagram
        The force diagram.

    Returns
    -------
    jacobian
        Jacobian matrix ( 2 * _vcount, 2 * vcount)
    """
    # Update force diagram based on form
    form_update_q_from_qind(form)
    force_update_from_form(force, form)

    # --------------------------------------------------------------------------
    # form diagram
    # --------------------------------------------------------------------------
    vcount = form.number_of_vertices()
    k_i = form.key_index()
    leaves = [k_i[key] for key in form.leaves()]
    free   = list(set(range(form.number_of_vertices())) - set(leaves))
    vicount = len(free)
    edges = [(k_i[u], k_i[v]) for u, v in form.edges()]
    xy = array(form.xy(), dtype=float64).reshape((-1, 2))
    ecount = len(edges)
    C = connectivity_matrix(edges, 'array')
    E = equilibrium_matrix(C, xy, free, 'array')
    uv = C.dot(xy)
    u = np.asmatrix(uv[:, 0]).transpose()
    v = np.asmatrix(uv[:, 1]).transpose()
    C = C.transpose()
    Ci = C[free, :]

    q = array(form.q(), dtype=float64).reshape((-1, 1))
    Q = np.diag(np.asmatrix(q).getA1())
    Q = np.asmatrix(Q)

    independent_edges = list(form.edges_where({'is_ind': True}))
    independent_edges_idx = [edges.index(i) for i in independent_edges]
    dependent_edges_idx = list(set(range(ecount)) - set(independent_edges_idx))

    Ed = E[:, dependent_edges_idx]
    Eid = E[:, independent_edges_idx]
    qid = q[independent_edges_idx]

    # --------------------------------------------------------------------------
    # force diagram
    # --------------------------------------------------------------------------
    _vcount = force.number_of_vertices()
    _edges = force.ordered_edges(form)
    _L = laplacian_matrix(_edges, normalize=False, rtype='array')
    _C = connectivity_matrix(_edges, 'array')
    _C = _C.transpose()
    _C = np.asmatrix(_C)
    _k_i   = force.key_index()
    _known = [_k_i[force.anchor()]]

    # --------------------------------------------------------------------------
    # Jacobian
    # --------------------------------------------------------------------------
    jacobian = np.zeros((_vcount * 2, vcount * 2))
    for j in range(2):  # Loop for x and y
        idx = list(range(j * vicount, (j + 1) * vicount))
        for i in range(vcount):
            dXdxi = np.diag(C[i, :])
            dxdxi = np.transpose(np.asmatrix(C[i, :]))

            dEdXi = np.zeros((vicount * 2, ecount))
            dEdXi[idx, :] = np.asmatrix(Ci) * np.asmatrix(dXdxi)  # Always half the matrix 0 depending on j (x/y)

            dEdXi_d = dEdXi[:, dependent_edges_idx]
            dEdXi_id = dEdXi[:, independent_edges_idx]

            EdInv = np.linalg.inv(np.asmatrix(Ed))
            dEdXiInv = - EdInv * (np.asmatrix(dEdXi_d) * EdInv)

            dqdXi_d = -dEdXiInv * (Eid * np.asmatrix(qid)) - EdInv * (dEdXi_id * np.asmatrix(qid))
            dqdXi = np.zeros((ecount, 1))
            dqdXi[dependent_edges_idx] = dqdXi_d
            dqdXi[independent_edges_idx] = 0
            dQdXi = np.asmatrix(np.diag(dqdXi[:, 0]))

            d_XdXiTop = np.zeros((_L.shape[0]))
            d_XdXiBot = np.zeros((_L.shape[0]))
            if j == 0:
                d_XdXiTop = solve_with_known(_L, np.array(_C * (dQdXi * u + Q * dxdxi)).flatten(), d_XdXiTop, _known)
                d_XdXiBot = solve_with_known(_L, np.array(_C * (dQdXi * v)).flatten(), d_XdXiBot, _known)
            elif j == 1:
                d_XdXiTop = solve_with_known(_L, np.array(_C * (dQdXi * u)).flatten(), d_XdXiTop, _known)
                d_XdXiBot = solve_with_known(_L, np.array(_C * (dQdXi * v + Q * dxdxi)).flatten(), d_XdXiBot, _known)

            d_XdXi = np.hstack((d_XdXiTop, d_XdXiBot))
            jacobian[:, i + j * vcount] = d_XdXi
    return jacobian


def update_coordinates(diagram, xy):
    r"""Update diagram coordinates.

    Parameters
    ----------
    diagram : compas_ags.diagrams.formdiagram.FormDiagram or compas_bi_ags.diagrams.forcediagram.ForceDiagram
        The form or force diagram.
    xy
        form or force coordinates array, size (nvertices x 2)

    Returns
    -------
    None
    """
    k_i = diagram.key_index()
    for key, attr in diagram.vertices(True):
        index = k_i[key]
        attr['x'] = xy[index, 0]
        attr['y'] = xy[index, 1]


def _compute_jacobian_numerically(form, force):
    r"""Compute the Jacobian matrix.

    The actual computation of the Jacobían d_X/dX
    where X contains the form diagram coordinates in *Fortran* order
    (first all x-coordinates, then all y-coordinates) and _X contains the
    force diagram coordinates in *Fortran* order (first all _x-coordinates,
    then all _y-coordinates)

    The Jacobian is computed numerically using forward differences.

    Parameters
    ----------
    form : compas_ags.diagrams.formdiagram.FormDiagram
        The form diagram.
    force : compas_bi_ags.diagrams.forcediagram.ForceDiagram
        The force diagram.

    Returns
    -------
    jacobian
        Jacobian matrix ( 2 * _vcount, 2 * vcount)
    """
    # Update force diagram
    form_update_q_from_qind(form)
    force_update_from_form(force, form)

    # Get current coordinates
    xy = array(form.xy(), dtype=float64).reshape((-1, 2))
    X = np.vstack((np.asmatrix(xy[:, 0]).transpose(), np.asmatrix(xy[:, 1]).transpose()))
    _X = _comp_perturbed_force_coordinates_from_form(form, force, X)
    vcount = form.number_of_vertices()
    _vcount = force.number_of_vertices()

    # --------------------------------------------------------------------------
    # Jacobian from forward differencing
    # --------------------------------------------------------------------------
    jacobian = np.zeros((_vcount * 2, vcount * 2))
    nv = len(X)
    for i in range(nv):
        du = np.zeros(X.shape)
        du[i] = 1
        _Xi_pert = _comp_perturbed_force_coordinates_from_form(form, force, X + du * 1e-10)
        dX = np.divide(_Xi_pert - _X, 1e-10)
        jacobian[:, i] = dX.A1
    return jacobian


def _comp_perturbed_force_coordinates_from_form(form, force, X):
    r"""Compute force diagram coordinates based on X.

    Used to compute perturbed force diagram coordinates by sending
    in perturbed form diagram coordinates. Useful for computing the
    Jacobian matrix numerically.

    Parameters
    ----------
    form : compas_ags.formdiagram.FormDiagram
        The form diagram.
    force : compas_ags.forcediagram.ForceDiagram
        The force diagram.
    X
        Perturbed form diagram coordinates in *Fortran* order (first all x-coordinates, then all y-coordinates).

    Returns
    -------
    _X
        Perturbed force diagram coordinates in *Fortran* order (first all _x-coordinates, then all _y-coordinates).
    """
    # Save current coordinates
    xyo = array(form.xy(), dtype=float64).reshape((-1, 2))
    _xyo = array(force.xy(), dtype=float64)

    # Perturb form and update force
    nx = xyo.shape[0]
    ny = xyo.shape[0]
    xy = array(form.xy(), dtype=float64).reshape((-1, 2))
    xy[:, 0] = X[:nx].T
    xy[:, 1] = X[nx:(nx + ny)].T
    update_coordinates(form, xy)
    form_update_q_from_qind(form)
    force_update_from_form(force, form)
    _xy = array(force.xy(), dtype=float64)
    _X = np.vstack((np.asmatrix(_xy[:, 0]).transpose(), np.asmatrix(_xy[:, 1]).transpose()))

    # Revert to current coordinates
    update_coordinates(form, xyo)
    update_coordinates(force, _xyo)

    return _X







