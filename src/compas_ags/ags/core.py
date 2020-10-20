from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

import sys

from numpy import array
from numpy import eye
from numpy import zeros
from numpy import float64
from numpy.linalg import cond

from scipy.linalg import solve
from scipy.linalg import lstsq

from compas.numerical import normrow
from compas.numerical import normalizerow

from compas.geometry import midpoint_point_point_xy


__all__ = [
    'update_q_from_qind',
    'update_form_from_force'
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


def update_form_from_force(xy, _xy, free, leaves, i_nbrs, ij_e, _C, kmax=100):
    r"""Update the coordinates of a form diagram using the coordinates of the corresponding force diagram.

    Parameters
    ----------
    xy : array-like
        XY coordinates of the vertices of the form diagram.
    _xy : array-like
        XY coordinates of the vertices of the force diagram.
    free : list
        The free vertices of the form diagram.
    leaves : list
        The leaves of the form diagram.
    i_nbrs : list of list of int
        Vertex neighbours per vertex.
    ij_e : dict
        Edge index for every vertex pair.
    _C : sparse matrix in csr format
        The connectivity matrix of the force diagram.
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
    geometry of the force diagram. The objective is to compute new locations
    for the vertices of the form diagram such that the corrsponding lines of the
    form and force diagram are parallel while any geometric constraints imposed on
    the form diagram are satisfied.

    The location of each vertex of the form diagram is computed as the intersection
    of the lines connected to it. Each of the connected lines is based at the connected
    neighbouring vertex and taken parallel to the corresponding line in the force
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
        # each free vertex location of the form diagram is computed as the intersection
        # of the connected lines. each of these lines is based at the corresponding
        # connected neighbouring vertex and taken parallel to the corresponding
        # edge in the force diagram.
        # the intersection is the point that minimises the distance to all connected
        # lines.
        for i in free:
            R = zeros((2, 2), dtype=float64)
            q = zeros((2, 1), dtype=float64)

            # add line constraints based on connected edges
            for j in i_nbrs[i]:
                if j in leaves:
                    continue

                n = _t[ij_e[(i, j)], None]  # the direction of the line (the line parallel to the corresponding line in the force diagram)
                _l = _uv[ij_e[(i, j)], None]

                if normrow(_l)[0, 0] < 0.001:
                    continue

                r = I - n.T.dot(n)          # projection into the orthogonal space of the direction vector
                a = xy[j, None]             # a point on the line (the neighbour of the vertex)
                R += r
                q += r.dot(a.T)

            A[row: row + 2, row: row + 2] = R
            b[row: row + 2] = q
            row += 2

            # p = solve(R.T.dot(R), R.T.dot(q))
            # xy[i] = p.reshape((-1, 2), order='C')

        # res = solve(A.T.dot(A), A.T.dot(b))
        # xy[free] = res.reshape((-1, 2), order='C')
        res = lstsq(A, b)
        xy[free] = res[0].reshape((-1, 2), order='C')

    # reconnect leaves
    for i in leaves:
        j = i_nbrs[i][0]
        xy[i] = xy[j] + xy0[i] - xy0[j]


def parallelise_edges(xy, edges, targets, i_nbrs, ij_e, fixed=None, kmax=100, lmin=None, lmax=None, callback=None):
    """Parallelise the edges of a mesh to given target vectors.

    Parameters
    ----------
    xy : list
        The XY coordinates of the vertices of the edges.
    edges : list
        The edges as pairs of indices in ``xy``.
    targets : list
        A target vector for every edge.
    i_nbrs : dict
        A list of neighbours per vertex.
    ij_e : dict
        An edge index per vertex pair.
    fixed : list, optional
        The fixed nodes of the mesh.
        Default is ``None``.
    kmax : int, optional
        Maximum number of iterations.
        Default is ``100``.
    lmin : list, optional
        Minimum length per edge.
        Default is ``None``.
    lmax : list, optional
        Maximum length per edge.
        Default is ``None``.
    callback : callable, optional
        A user-defined callback function to be executed after every iteration.
        Default is ``None``.

    Returns
    -------
    None

    Examples
    --------
    >>>
    """
    if callback:
        if not callable(callback):
            raise Exception('The provided callback is not callable.')

    fixed = fixed or []
    fixed = set(fixed)

    n = len(xy)

    for k in range(kmax):
        xy0 = [[x, y] for x, y in xy]
        uv = [[xy[j][0] - xy[i][0], xy[j][1] - xy[i][1]] for i, j in edges]
        lengths = [(dx**2 + dy**2)**0.5 for dx, dy in uv]

        if lmin:
            lengths[:] = [max(a, b) for a, b in zip(lengths, lmin)]

        if lmax:
            lengths[:] = [min(a, b) for a, b in zip(lengths, lmax)]

        for j in range(n):
            if j in fixed:
                continue

            nbrs = i_nbrs[j]
            x, y = 0.0, 0.0

            for i in nbrs:
                ax, ay = xy0[i]

                if (i, j) in ij_e:
                    e = ij_e[(i, j)]
                    l = lengths[e]  # noqa: E741
                    tx, ty = targets[e]
                    x += ax + l * tx
                    y += ay + l * ty

                else:
                    e = ij_e[(j, i)]
                    l = lengths[e]  # noqa: E741
                    tx, ty = targets[e]
                    x += ax - l * tx
                    y += ay - l * ty

            xy[j][0] = x / len(nbrs)
            xy[j][1] = y / len(nbrs)

        for (i, j) in ij_e:
            e = ij_e[(i, j)]

            if lengths[e] == 0.0:
                c = midpoint_point_point_xy(xy[i], xy[j])
                xy[i][:] = c[:][:2]
                xy[j][:] = c[:][:2]

        if callback:
            callback(k, xy, edges)


# ==============================================================================
# Main
# ==============================================================================

if __name__ == "__main__":
    pass
