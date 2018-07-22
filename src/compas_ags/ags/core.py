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

    from scipy.linalg import solve
    from scipy.linalg import lstsq

except ImportError:
    if 'ironpython' not in sys.version.lower():
        raise

from compas.numerical import normalizerow


__author__    = ['Tom Van Mele', ]
__copyright__ = 'Copyright 2016 - Block Research Group, ETH Zurich'
__license__   = 'MIT License'
__email__     = 'vanmelet@ethz.ch'


__all__ = [
    'update_q_from_qind',
    'update_form_from_force'
]


EPS  = 1 / sys.float_info.epsilon


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

    Notes
    -----
    The force densities are updated in-place.

    Examples
    --------
    .. code-block:: python

        #

    """
    m  = E.shape[0] - len(dep)
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


def update_form_from_force(xy, _xy, free, leaves, i_j, ij_e, _C, kmax=100):
    _uv = _C.dot(_xy)
    _t  = normalizerow(_uv)
    I   = eye(2, dtype=float64)
    xy0 = array(xy, copy=True)
    A   = zeros((2 * len(free), 2 * len(free)), dtype=float64)
    b   = zeros((2 * len(free), 1), dtype=float64)

    # update the free vertices
    for k in range(kmax):
        row = 0

        for i in free:
            R = zeros((2, 2), dtype=float64)
            q = zeros((2, 1), dtype=float64)

            # add line constraints based on connected edges
            for j in i_j[i]:
                if j in leaves:
                    continue
                n  = _t[ij_e[(i, j)], None]
                p  = xy[j, None]
                r  = I - n.T.dot(n)
                R += r
                q += r.dot(p.T)

            # add line constraints as specified
            A[row: row + 2, row: row + 2] = R
            b[row: row + 2] = q
            row += 2

        res      = solve(A.T.dot(A), A.T.dot(b))
        xy[free] = res.reshape((-1, 2), order='C')

    # reconnect leaves
    for i in leaves:
        j     = i_j[i][0]
        xy[i] = xy[j] + xy0[i] - xy0[j]


# ==============================================================================
# Main
# ==============================================================================

if __name__ == "__main__":
    pass
