from compas_ags.ags.graphstatics import *

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

import compas_ags.utilities.errorHandler as eh
import compas_ags.utilities.helpers as hlp
from compas_ags.ags.graphstatics import form_update_q_from_qind, force_update_from_form

__all__ = [
    'compute_jacobian',
    'get_red_residual_and_jacobian',
    'form_update_from_force',
    'update_coordinates',
    'compute_form_from_force_newton'
]

import numpy as np

def compute_form_from_force_newton(form, force, Xs_goal, tol=1e5):
    xy = array(form.xy(), dtype=float64).reshape((-1, 2))
    X_start = np.vstack(( np.asmatrix(xy[:,0]).transpose(), np.asmatrix(xy[:,1]).transpose()))
    X = X_start

    diff = 100
    n_iter = 1
    eps = np.spacing(1)

    while diff > (eps * tol):
        red_jacobian, red_r, zero_columns = get_red_residual_and_jacobian(form,force,Xs_goal)

        # Do the least squares solution
        dx = np.linalg.lstsq(red_jacobian, -red_r)[0]

        # Add back zeros for zero columns
        for zero_column in zero_columns:
            dx = np.insert(dx, zero_column, 0.0, axis=0)

        X = X + dx

        nx = xy.shape[0]
        ny = xy.shape[0]
        xy[:, 0] = X[:nx].T
        xy[:, 1] = X[nx:(nx + ny)].T
        update_coordinates(form, xy)

        diff = np.linalg.norm(red_r)
        if n_iter > 20:
            raise eh.SolutionError('Did not converge')

        print('i: {0:0} diff: {1:.2e}'.format(n_iter, float(diff)))
        n_iter += 1

    print('Converged in {0} iterations'.format(n_iter))

def get_red_residual_and_jacobian(form,force,Xs_goal):

    # TODO: Scramble vertices

    jacobian = compute_jacobian(form, force)

    _vcount = force.number_of_vertices()
    bc = [_vcount - 1, _vcount * 2 - 1]
    _xy = array(force.xy(), dtype=float64)
    r = np.vstack(( np.asmatrix(_xy[:,0]).transpose(), np.asmatrix(_xy[:,1]).transpose())) - Xs_goal

    # TODO: Add constraints

    hlp.check_solutions(jacobian,r)
    # Remove rows due to fixed vertex in the force diagram
    red_r = np.delete(r, bc, axis=0)
    red_jacobian = np.delete(jacobian, bc, axis=0)
    # Remove zero columns from jacobian
    zero_columns = []
    for i, jacobian_column in enumerate(np.sum(np.abs(jacobian), axis=0)):
        if jacobian_column < 1e-5:
            zero_columns.append(i)
    red_jacobian = np.delete(red_jacobian, zero_columns, axis=1)
    return red_jacobian, red_r, zero_columns

def compute_jacobian(form,force):
    # Update force diagram based on form
    form_update_q_from_qind(form)
    force_update_from_form(force, form)

    # --------------------------------------------------------------------------
    # form diagram
    # --------------------------------------------------------------------------
    vcount = form.number_of_vertices()
    k_i = form.key_index()
    leaves = [k_i[key] for key in form.leaves()]
    free   = list(set(range(form.number_of_vertices()))  - set(leaves))
    vicount = len(free)
    edges = [(k_i[u], k_i[v]) for u, v in form.edges()]
    xy = array(form.xy(), dtype=float64).reshape((-1, 2))
    ecount = len(edges)
    C = connectivity_matrix(edges, 'array')
    E = equilibrium_matrix(C, xy, free, 'array')
    uv = C.dot(xy)
    u = np.asmatrix(uv[:,0]).transpose()
    v = np.asmatrix(uv[:,1]).transpose()
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
    #_L = np.asmatrix(_L)
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

            dAdxi = np.zeros((vicount * 2, ecount))
            dAdxi[idx,:] = np.asmatrix(Ci) * np.asmatrix(dXdxi)  # Always half the matrix 0 depending on j (x/y)

            dAddxi = dAdxi[:, dependent_edges_idx]
            dAiddxi = dAdxi[:, independent_edges_idx]

            AdInvPre = np.linalg.inv(np.asmatrix(Ed))
            AdInv = - AdInvPre * (np.asmatrix(dAddxi) * AdInvPre)

            dqddxi = -AdInv * (Eid * np.asmatrix(qid)) - AdInvPre * (dAiddxi * np.asmatrix(qid))
            dqdxi = np.zeros((ecount, 1))
            dqdxi[dependent_edges_idx] = dqddxi
            dqdxi[independent_edges_idx] = 0
            dQdxi = np.asmatrix(np.diag(dqdxi[:, 0]))

            dXdiTop = np.zeros((_L.shape[0]))
            dXdiBot = np.zeros((_L.shape[0]))
            if j == 0:
                dXdiTop = solve_with_known(_L, np.array(_C * (dQdxi * u + Q * dxdxi)).flatten(), dXdiTop, _known)
                dXdiBot = solve_with_known(_L, np.array(_C * (dQdxi * v)).flatten(), dXdiBot, _known)
            elif j == 1:
                dXdiTop = solve_with_known(_L, np.array(_C * (dQdxi * u)).flatten(), dXdiTop, _known)
                dXdiBot = solve_with_known(_L, np.array(_C * (dQdxi * v + Q * dxdxi)).flatten(), dXdiBot, _known)

            dXdi = np.hstack((dXdiTop, dXdiBot))
            jacobian[:, i + j * vcount] = dXdi
    return jacobian

def update_coordinates(diagram, xy):
    k_i = diagram.key_index()
    for key, attr in diagram.vertices(True):
        index = k_i[key]
        attr['x'] = xy[index, 0]
        attr['y'] = xy[index, 1]

def _compute_jacobian_numerically(form, force):
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
        jacobian[:,i] = dX.A1
    return jacobian


def _comp_perturbed_force_coordinates_from_form(form, force, X):
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
    _X = np.vstack((np.asmatrix(_xy[:,0]).transpose(), np.asmatrix(_xy[:,1]).transpose()))

    # Revert to current coordinates
    update_coordinates(form, xyo)
    update_coordinates(force, _xyo)

    return _X







