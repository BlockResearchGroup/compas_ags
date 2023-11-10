from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

import sys

from numpy import array
from numpy import eye
from numpy import zeros
from numpy import float64
from numpy import delete
from numpy import vstack
from numpy import diag
from numpy import hstack
from numpy.linalg import inv
from numpy.linalg import cond
from numpy.linalg import matrix_rank

from scipy.linalg import solve
from scipy.linalg import lstsq

from compas.numerical import normrow
from compas.numerical import normalizerow
from compas.numerical import connectivity_matrix
from compas.numerical import equilibrium_matrix
from compas.numerical import laplacian_matrix
from compas.numerical import solve_with_known
from compas.geometry import midpoint_point_point_xy
from compas.geometry import project_point_line_xy

from compas_ags.exceptions import SolutionError


__all__ = [
    "update_q_from_qind",
    "update_primal_from_dual",
    "get_jacobian_and_residual",
    "compute_jacobian",
    "parallelise_edges",
]


EPS = 1 / sys.float_info.epsilon


def update_q_from_qind(E, q, dep, ind):
    """Update the full set of force densities using the values of the independent edges.

    Parameters
    ----------
    E : sparse csr matrix
        The equilibrium matrix.
    q : array
        The force densities of the edges.
    dep : list
        The indices of the dependent edges.
    ind : list
        The indices of the independent edges.

    Returns
    -------
    None
        The force densities are modified in-place.

    Examples
    --------
    >>>
    """
    m = E.shape[0] - len(dep)
    qi = q[ind]
    Ei = E[:, ind]
    Ed = E[:, dep]
    if m > 0:
        Edt = Ed.transpose()
        A = Edt.dot(Ed).toarray()
        b = Edt.dot(Ei).dot(qi)
    else:
        A = Ed.toarray()
        b = Ei.dot(qi)
    if cond(A) > EPS:
        res = lstsq(-A, b)
        qd = res[0]
    else:
        qd = solve(-A, b)
    q[dep] = qd


def update_primal_from_dual(
    xy,
    _xy,
    free,
    i_nbrs,
    ij_e,
    _C,
    line_constraints=None,
    target_lengths=[],
    target_vectors=[],
    leaves=[],
    kmax=100,
):
    r"""Update the coordinates of the primal diagram using the coordinates of the corresponding dual diagram.
    This function apply to both sides, i.e. it can be used to update the form diagram from the geometry of the force
    diagram or to update the force diagram from the geometry of the force diagram.

    Parameters
    ----------
    xy : array-like
        XY coordinates of the vertices of the primal diagram.
    _xy : array-like
        XY coordinates of the vertices of the dual diagram.
    i_nbrs : list of list of int
        Vertex neighbours per vertex.
    ij_e : dict
        Edge index for every vertex pair.
    _C : sparse matrix in csr format
        The connectivity matrix of the force diagram.
    line_constraints : list, optional
        Line constraints applied to the free nodes.
        Default is an ``None`` in which case no line constraints are considered.
    target_lengths : list, optional
        Target lengths / target forces of the edges.
        Default is an empty list, which considers that no target lengths are considered.
    target_vectors : list, optional
        Target vectors of the edges.
        Default is an empty list, which considers that no target vectors are considered.
    leaves : list, optional
        The leaves of the primal diagram.
        Default is an empty list, which considers that no leaves are considered.
    kmax : int, optional
        Maximum number of iterations.
        Default is ``100``.

    Returns
    -------
    None
        The vertex coordinates are modified in-place.

    Notes
    -----
    This function should be used to update the form diagram after modifying the
    geometry of the force diagram. Or to update the force diagram geometrically to
    become reciprocal to the form diagram. The objective is to compute new locations
    for the vertices of the primal diagram such that the corrsponding lines of the
    primal and dual diagram are parallel while any geometric constraints imposed on
    the primal diagram are satisfied. Note that form, and force can assume position
    of primal and dual interchagable.

    The location of each vertex of the primal diagram is computed as the intersection
    of the lines connected to it. Each of the connected lines is based at the connected
    neighbouring vertex and taken parallel to the corresponding line in the dual
    diagram.

    For a point :math:`\mathbf{p}`, which is the least-squares intersection of *K*
    lines, with every line *j* defined by a point :math:`\mathbf{a}_{j}` on the line
    and a direction vector :math:`\mathbf{n}_{j}`, we can write

    .. math::

        \mathbf{R} \mathbf{p} = \mathbf{q}

    with

    .. math::

        \mathbf{R} = \displaystyle\sum_{j=1}^{K}(\mathbf{I} - \mathbf{n}_{j}\mathbf{n}_{j}^{T})
        \quad,\quad
        \mathbf{q} = \displaystyle\sum_{j=1}^{K}(\mathbf{I} - \mathbf{n}_{j}\mathbf{n}_{j}^{T})\mathbf{a}_{j}

    This system of linear equations can be solved using the normal equations

    .. math::

        \mathbf{p} = (\mathbf{R}^{T}\mathbf{R})^{-1}\mathbf{R}^{T}\mathbf{q}

    Examples
    --------
    >>>
    """
    _uv = _C.dot(_xy)
    _t = normalizerow(_uv)
    I = eye(2, dtype=float64)  # noqa: E741
    xy0 = array(xy, copy=True)
    A = zeros((2 * len(free), 2 * len(free)), dtype=float64)
    b = zeros((2 * len(free), 1), dtype=float64)

    # update the free vertices
    for k in range(kmax):
        row = 0

        # in order for the two diagrams to have parallel corresponding edges,
        # each free vertex location of the primal diagram is computed as the intersection
        # of the connected lines. each of these lines is based at the corresponding
        # connected neighbouring vertex and taken parallel to the corresponding
        # edge in the dual diagram.
        # the intersection is the point that minimises the distance to all connected
        # lines.
        for count in range(len(free)):
            i = free[count]
            R = zeros((2, 2), dtype=float64)
            q = zeros((2, 1), dtype=float64)

            # add line constraints based on connected edges
            for j in i_nbrs[i]:
                if j in leaves:
                    continue

                n = _t[
                    ij_e[(i, j)], None
                ]  # the direction of the line (the line parallel to the corresponding line in the force diagram)
                _l = _uv[ij_e[(i, j)], None]

                if normrow(_l)[0, 0] < 0.001:
                    continue

                if target_lengths:
                    if target_lengths[ij_e[(i, j)]] == 0.0:
                        continue

                if target_vectors:
                    if target_vectors[ij_e[(i, j)]]:
                        n = array(target_vectors[ij_e[(i, j)]]).reshape(1, -1)

                r = I - n.T.dot(n)  # projection into the orthogonal space of the direction vector
                a = xy[j, None]  # a point on the line (the neighbour of the vertex)
                R += r
                q += r.dot(a.T)

            if line_constraints:
                line = line_constraints[count]
                if line:
                    n_ = array(line.direction[:2]).reshape(1, 2)
                    r = I - n_.T.dot(n_)
                    pt = array(line.start[:2]).reshape(1, 2)
                    R += r
                    q += r.dot(pt.T)

            A[row : row + 2, row : row + 2] = R
            b[row : row + 2] = q
            row += 2

            # p = solve(R.T.dot(R), R.T.dot(q))
            # xy[i] = p.reshape((-1, 2), order='C')

        res = lstsq(A, b)
        xy_lstsq = res[0].reshape((-1, 2), order="C")
        xy[free] = xy_lstsq

    # reconnect leaves
    for i in leaves:
        j = i_nbrs[i][0]
        xy[i] = xy[j] + xy0[i] - xy0[j]


def parallelise_edges(
    xy,
    edges,
    i_nbrs,
    ij_e,
    target_vectors,
    target_lengths,
    fixed=None,
    line_constraints=None,
    kmax=100,
    callback=None,
):
    """Parallelise the edges of a mesh to given target vectors.

    Parameters
    ----------
    xy : list
        The XY coordinates of the vertices of the edges.
    edges : list
        The edges as pairs of indices in ``xy``.
    i_nbrs : dict
        A list of neighbours per vertex.
    ij_e : dict
        An edge index per vertex pair.
    target_vectors : list
        A list with an entry for each edge representing the target vector or ``None``.
    target_lengths : list
        A list with an entry for each edge representing the target length or ``None``.
    fixed : list, optional
        The fixed nodes of the mesh.
        Default is ``None``.
    line_constraints : list, optional
        Line constraints applied to the free nodes.
        Default is an ``None`` in which case no line constraints are considered.
    kmax : int, optional
        Maximum number of iterations.
        Default is ``100``.
    callback : callable, optional
        A user-defined callback function to be executed after every iteration.
        Default is ``None``.

    Returns
    -------
    None

    Notes
    -----
    This implementation is based on the function ``compas_tna.equilibrium.parallelisation.parallelise_edges``.

    Examples
    --------
    >>>
    """
    if callback:
        if not callable(callback):
            raise Exception("The provided callback is not callable.")

    n = len(xy)

    for k in range(kmax):
        xy0 = [[x, y] for x, y in xy]
        uv = [[xy[j][0] - xy[i][0], xy[j][1] - xy[i][1]] for i, j in edges]
        lengths = [(dx**2 + dy**2) ** 0.5 for dx, dy in uv]

        for j in range(n):
            if j in fixed:
                continue

            nbrs = i_nbrs[j]
            x, y = 0.0, 0.0

            len_nbrs = 0
            for i in nbrs:
                if (i, j) in ij_e:
                    e = ij_e[(i, j)]
                    u, v = i, j
                    signe = +1.0
                else:
                    e = ij_e[(j, i)]
                    u, v = j, i
                    signe = -1.0

                if target_lengths[e] is not None:  # edges with constraint on length ...
                    lij = target_lengths[e]
                    if target_vectors[e]:  # edges with constraint on length + orientation
                        tx, ty = target_vectors[e]
                    else:  # edges with constraint on length only
                        if lengths[e] == 0.0:
                            tx = ty = 0.0
                        else:
                            tx = (xy0[v][0] - xy0[u][0]) / lengths[e]
                            ty = (xy0[v][1] - xy0[u][1]) / lengths[e]  # check if xy0 is indeed better than xy
                else:
                    if target_vectors[e]:  # edges with constraint on orientation only
                        tx, ty = target_vectors[e]
                        lij = lengths[e]
                    else:
                        continue  # edges to discard

                ax, ay = xy0[i]
                x += ax + signe * lij * tx
                y += ay + signe * lij * ty
                len_nbrs += 1

            if len_nbrs > 0:
                xy[j][0] = x / len_nbrs
                xy[j][1] = y / len_nbrs

                # check if line constraints are applied and project result
                if line_constraints:
                    line = line_constraints[j]
                    if line:
                        pt_proj = project_point_line_xy(xy[j], line)
                        xy[j][0] = pt_proj[0]
                        xy[j][1] = pt_proj[1]

        for i, j in ij_e:
            e = ij_e[(i, j)]

            if lengths[e] == 0.0 or target_lengths[e] == 0.0:
                c = midpoint_point_point_xy(xy[i], xy[j])
                xy[i][:] = c[:][:2]
                xy[j][:] = c[:][:2]

        if callback:
            callback(k, xy, edges)


def get_jacobian_and_residual(form, force, _X_goal, constraints=None):
    r"""Compute the Jacobian matrix and residual.

    Computes the residual and the Jacobian matrix :math:`\partial \mathbf{X}^* / \partial \mathbf{X}`
    where :math:`\mathbf{X}` contains the form diagram coordinates in *Fortran* order
    (first all :math:`\mathbf{x}`-coordinates, then all :math:`\mathbf{y}`-coordinates) and :math:`\mathbf{X}^*` contains the
    force diagram coordinates in *Fortran* order (first all :math:`\mathbf{x}^*`-coordinates,
    then all :math:`\mathbf{y}^*`-coordinates). Jacobian and residual have the rows corresponding to the
    force diagrarm anchor vertex removed.

    Parameters
    ----------
    form: :class:`FormDiagram`
        The form diagram to update.
    force: :class:`ForceDiagram`
        The force diagram on which the update is based.
    _X_goal: array [2*n]
        Contains the target force diagram coordinates (:math:`\mathbf{X}^*`) in *Fortran* order
        (first all :math:`\mathbf{x}^*`-coordinates, then all :math:`\mathbf{y}^*`-coordinates).
    constraints: :class:`ConstraintsCollection`, optional
        A collection of form diagram constraints.
        The default is ``None``, in which case no constraints are considered.

    Returns
    -------
    red_jacobian, red_r: tuple of arrays
        Jacobian matrix and residual vector as arrays.
        The rows corresponding to the anchor of the force diagram are removed

    References
    ----------
    .. [1] Alic, V. and Åkesson, D., 2017. Bi-directional algebraic graphic statics. Computer-Aided Design, 93, pp.26-37.

    Examples
    --------
    >>>
    """

    jacobian = compute_jacobian(form, force)

    _vcount = force.number_of_vertices()
    _k_i = force.key_index()
    _known = _k_i[force.anchor()]
    _bc = [_known, _vcount + _known]
    _X_iteration = array(force.vertices_attribute("x") + force.vertices_attribute("y")).reshape(-1, 1)
    r = _X_iteration - _X_goal

    if constraints:
        (cj, cr) = constraints.compute_constraints()
        jacobian = vstack((jacobian, cj))
        r = vstack((r, cr))

    # Check rank of augmented matrix
    rank_jac = matrix_rank(jacobian)
    rank_aug = matrix_rank(hstack([jacobian, r]))

    if rank_jac < rank_aug:
        raise SolutionError("ERROR: Rank Augmented > Rank Jacobian")

    # Remove rows due to anchored vertex in the force diagram
    red_r = delete(r, _bc, axis=0)
    red_jacobian = delete(jacobian, _bc, axis=0)

    return red_jacobian, red_r


def compute_jacobian(form, force):
    r"""Compute the Jacobian matrix.

    The actual computation of the Jacobian matrix :math:`\partial \mathbf{X}^* / \partial \mathbf{X}`
    where :math:`\mathbf{X}` contains the form diagram coordinates in *Fortran* order
    (first all :math:`\mathbf{x}`-coordinates, then all :math:`\mathbf{y}`-coordinates) and :math:`\mathbf{X}^*` contains the
    force diagram coordinates in *Fortran* order (first all :math:`\mathbf{x}^*`-coordinates,
    then all :math:`\mathbf{y}^*`-coordinates).

    Parameters
    ----------
    form: :class:`FormDiagram`
        The form diagram.
    force: :class:`ForceDiagram`
        The force diagram.

    Returns
    -------
    jacobian
        Jacobian matrix (2 * _vcount, 2 * vcount)

    References
    ----------
    .. [1] Alic, V. and Åkesson, D., 2017. Bi-directional algebraic graphic statics. Computer-Aided Design, 93, pp.26-37.

    Examples
    --------
    >>>
    """
    # --------------------------------------------------------------------------
    # form diagram
    # --------------------------------------------------------------------------
    vcount = form.number_of_vertices()
    k_i = form.key_index()
    leaves = [k_i[key] for key in form.leaves()]
    free = list(set(range(form.number_of_vertices())) - set(leaves))
    vicount = len(free)
    edges = [(k_i[u], k_i[v]) for u, v in form.edges()]
    xy = array(form.xy(), dtype=float64).reshape((-1, 2))
    ecount = len(edges)
    C = connectivity_matrix(edges, "array")
    E = equilibrium_matrix(C, xy, free, "array")
    uv = C.dot(xy)
    u = uv[:, 0].reshape(-1, 1)
    v = uv[:, 1].reshape(-1, 1)
    Ct = C.transpose()
    Cti = array(Ct[free, :])

    q = array(form.q(), dtype=float64).reshape((-1, 1))
    Q = diag(q.flatten())  # TODO: Explore sparse (diags)

    independent_edges = [(k_i[u], k_i[v]) for (u, v) in list(form.edges_where({"is_ind": True}))]
    independent_edges_idx = [edges.index(i) for i in independent_edges]
    dependent_edges_idx = list(set(range(ecount)) - set(independent_edges_idx))

    Ed = E[:, dependent_edges_idx]
    Eid = E[:, independent_edges_idx]
    qid = q[independent_edges_idx]
    EdInv = inv(array(Ed))  # TODO: Explore sparse (spinv)

    # --------------------------------------------------------------------------
    # force diagram
    # --------------------------------------------------------------------------
    _vertex_index = force.vertex_index()
    _vcount = force.number_of_vertices()
    _edges = force.ordered_edges(form)
    _edges[:] = [(_vertex_index[u], _vertex_index[v]) for u, v in _edges]
    _L = laplacian_matrix(_edges, normalize=False, rtype="array")
    _C = connectivity_matrix(_edges, "array")
    _Ct = _C.transpose()
    _Ct = array(_Ct)
    _known = [_vertex_index[force.anchor()]]

    # --------------------------------------------------------------------------
    # Jacobian
    # --------------------------------------------------------------------------
    jacobian = zeros((_vcount * 2, vcount * 2))
    for j in range(2):  # Loop for x and y
        idx = list(range(j * vicount, (j + 1) * vicount))
        for i in range(vcount):
            dXdxi = diag(Ct[i, :])
            dxdxi = Ct[i, :].reshape(-1, 1)

            dEdXi = zeros((vicount * 2, ecount))
            dEdXi[idx, :] = Cti.dot(dXdxi)

            dEdXi_d = dEdXi[:, dependent_edges_idx]
            dEdXi_id = dEdXi[:, independent_edges_idx]

            dEdXiInv = -EdInv.dot(dEdXi_d.dot(EdInv))

            dqdXi_d = -dEdXiInv.dot(Eid.dot(qid)) - EdInv.dot(dEdXi_id.dot(qid))
            dqdXi = zeros((ecount, 1))
            dqdXi[dependent_edges_idx] = dqdXi_d
            dqdXi[independent_edges_idx] = 0
            dQdXi = diag(dqdXi[:, 0])

            d_XdXiTop = zeros((_L.shape[0]))
            d_XdXiBot = zeros((_L.shape[0]))

            if j == 0:
                d_XdXiTop = solve_with_known(
                    _L,
                    (_Ct.dot(dQdXi.dot(u) + Q.dot(dxdxi))).flatten(),
                    d_XdXiTop,
                    _known,
                )
                d_XdXiBot = solve_with_known(_L, (_Ct.dot(dQdXi.dot(v))).flatten(), d_XdXiBot, _known)
            elif j == 1:
                d_XdXiTop = solve_with_known(_L, (_Ct.dot(dQdXi.dot(u))).flatten(), d_XdXiTop, _known)
                d_XdXiBot = solve_with_known(
                    _L,
                    (_Ct.dot(dQdXi.dot(v) + Q.dot(dxdxi))).flatten(),
                    d_XdXiBot,
                    _known,
                )

            d_XdXi = hstack((d_XdXiTop, d_XdXiBot))
            jacobian[:, i + j * vcount] = d_XdXi
    return jacobian


# ==============================================================================
# Main
# ==============================================================================

if __name__ == "__main__":
    pass
