from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

import sys

try:
    from numpy import array
    from numpy import float64

    from scipy.optimize import minimize
except ImportError:
    if 'ironpython' not in sys.version.lower():
        raise

from compas.geometry import angle_vectors_xy

from compas.numerical import connectivity_matrix
from compas.numerical import normrow

from compas_ags.ags import update_form_from_force


__author__ = ['Tom Van Mele', 'Andrew Liew>']
__email__  = 'vanmelet@ethz.ch'


__all__ = [
    'compute_loadpath',
    'compute_external_work',
    'compute_internal_work',
    'compute_internal_work_tension',
    'compute_internal_work_compression',
    'optimise_loadpath'
]


def compute_loadpath(form, force):
    """Compute the internal work of a structure.

    Parameters
    ----------
    form : FormDiagram
        The form diagram.
    force : ForceDiagram
        The force diagram.

    Returns
    -------
    float
        The internal work done by the structure.

    See Also
    --------
    :func:`compute_internal_work`

    """
    return compute_internal_work(form, force)


def compute_external_work(form, force):
    """Compute the external work of a structure.

    Parameters
    ----------
    form : FormDiagram
        The form diagram.
    force : ForceDiagram
        The force diagram.

    Returns
    -------
    float
        The external work done by the structure.

    Notes
    -----
    The external work done by a structure is equal to the work done by the external
    forces. This is equal to the sum of the dot products of the force vectors and
    the vectors defined by the force application point and a fixed arbitrary point.

    References
    ----------
    ...

    See Also
    --------
    :func:`compute_internal_work`

    Examples
    --------
    .. code-block:: python

        #

    """
    k_i   = form.key_index()
    xy    = array(form.xy(), dtype=float64)
    edges = [(k_i[u], k_i[v]) for u, v in form.edges()]
    C     = connectivity_matrix(edges, 'csr')
    q     = array(form.q(), dtype=float64).reshape((-1, 1))

    leaves   = set(form.leaves())
    external = [i for i, (u, v) in enumerate(form.edges()) if u in leaves or v in leaves]
    leaves   = [k_i[key] for key in leaves]

    l = normrow(C.dot(xy))
    f = q * l
    w = 0

    for e in external:
        i, j = edges[e]
        if j in leaves:
            sp, ep = xy[i], xy[j]
        else:
            sp, ep = xy[j], xy[i]
        v = f[e, 0] * (ep - sp) / l[e]
        w += sp.dot(v)

    return w


def compute_internal_work(form, force):
    """Compute the work done by the internal forces of a structure.

    Parameters
    ----------
    form : FormDiagram
        The form diagram.
    force : ForceDiagram
        The force diagram.

    Returns
    -------
    float
        The internal work done by the structure.

    Notes
    -----
    ...

    References
    ----------
    ...

    See Also
    --------
    :func:`compute_external_work`

    Examples
    --------
    .. code-block:: python

        #

    """
    k_i   = form.key_index()
    xy    = array(form.xy(), dtype=float64)
    edges = [(k_i[u], k_i[v]) for u, v in form.edges()]
    C     = connectivity_matrix(edges, 'csr')

    _xy    = force.xy()
    _edges = force.ordered_edges(form)
    _C     = connectivity_matrix(_edges, 'csr')

    leaves   = set(form.leaves())
    internal = [i for i, (u, v) in enumerate(form.edges()) if u not in leaves and v not in leaves]

    l   = normrow(C.dot(xy))
    _l  = normrow(_C.dot(_xy))
    li  = l[internal]
    _li = _l[internal]

    return li.T.dot(_li)[0, 0]


def compute_internal_work_tension(form, force):
    """Compute the work done by the internal tensile forces of a structure.

    Parameters
    ----------
    form : FormDiagram
        The form diagram.
    force : ForceDiagram
        The force diagram.

    Returns
    -------
    float
        The internal work done by the tensile forces in a structure.

    Notes
    -----
    ...

    References
    ----------
    ...

    See Also
    --------
    :func:`compute_internal_work_compression`

    Examples
    --------
    .. code-block:: python

        #

    """
    k_i   = form.key_index()
    xy    = array(form.xy(), dtype=float64)
    edges = [(k_i[u], k_i[v]) for u, v in form.edges()]
    C     = connectivity_matrix(edges, 'csr')
    q     = array(form.q(), dtype=float64).reshape((-1, 1))

    _xy    = force.xy()
    _edges = force.ordered_edges(form)
    _C     = connectivity_matrix(_edges, 'csr')

    leaves   = set(form.leaves())
    internal = [i for i, (u, v) in enumerate(form.edges()) if u not in leaves and v not in leaves]
    tension  = [i for i in internal if q[i, 0] > 0]

    l   = normrow(C.dot(xy))
    _l  = normrow(_C.dot(_xy))
    li  = l[tension]
    _li = _l[tension]

    return li.T.dot(_li)[0, 0]


def compute_internal_work_compression(form, force):
    """Compute the work done by the internal compressive forces of a structure.

    Parameters
    ----------
    form : FormDiagram
        The form diagram.
    force : ForceDiagram
        The force diagram.

    Returns
    -------
    float
        The internal work done by the compressive forces in a structure.

    Notes
    -----
    ...

    References
    ----------
    ...

    See Also
    --------
    :func:`compute_internal_work_tension`

    Examples
    --------
    .. code-block:: python

        #

    """
    k_i   = form.key_index()
    xy    = array(form.xy(), dtype=float64)
    edges = [(k_i[u], k_i[v]) for u, v in form.edges()]
    C     = connectivity_matrix(edges, 'csr')
    q     = array(form.q(), dtype=float64).reshape((-1, 1))

    _xy    = force.xy()
    _edges = force.ordered_edges(form)
    _C     = connectivity_matrix(_edges, 'csr')

    leaves      = set(form.leaves())
    internal    = [i for i, (u, v) in enumerate(form.edges()) if u not in leaves and v not in leaves]
    compression = [i for i in internal if q[i, 0] < 0]

    l   = normrow(C.dot(xy))
    _l  = normrow(_C.dot(_xy))
    li  = l[compression]
    _li = _l[compression]

    return li.T.dot(_li)[0, 0]


def optimise_loadpath(form, force, algo='COBYLA'):
    """Optimise the loadpath using the parameters of the force domain. The parameters
    of the force domain are the coordinates of the vertices of the force diagram.

    Parameters
    ----------
    form : FormDiagram
        The form diagram.
    force : ForceDiagram
        The force diagram.
    algo : {'COBYLA', L-BFGS-B', 'SLSQ', 'MMA', 'GMMA'}, optional
        The optimisation algorithm.

    Returns
    -------
    None

    Notes
    -----
    In many cases, the number of paramters of the force domain involved in generating
    new solutions in the form domain is smaller than when using the elements of the
    form diagram directly.

    For example, the loadpath of a bridge with a compression arch can be optimised
    using only the x-coordinates of the vertices of the force diagram corresponding
    to internal spaces formed by the segments of the arch, the corresponding deck
    elements, and the hangers connecting them. Any solution generated by these parameters
    will be in equilibrium and automatically  have a horizontal bridge deck.

    Although the *BRG* algorithm is the preferred choice, since it is (should be)
    tailored to the problem of optimising loadpaths using the domain of the force
    diagram, it does not have a stable and/or efficient implementation.
    The main problem is the generation of the form diagram, based on a given force
    diagram. For example, when edge forces flip from tension to compression, and
    vice versa, parallelisation is no longer effective.

    """
    k_i    = form.key_index()
    i_j    = dict((i, [k_i[n] for n in form.vertex_neighbors(k)]) for i, k in enumerate(form.vertices()))
    uv_e   = form.uv_index()
    ij_e   = dict(((k_i[u], k_i[v]), uv_e[(u, v)]) for u, v in uv_e)
    xy     = array(form.xy(), dtype=float64)
    edges  = [(k_i[u], k_i[v]) for u, v in form.edges()]
    C      = connectivity_matrix(edges, 'csr')
    # add opposite edges for convenience...
    ij_e.update(dict(((k_i[v], k_i[u]), uv_e[(u, v)]) for u, v in uv_e))

    leaves   = [k_i[key] for key in form.leaves()]
    fixed    = [k_i[key] for key in form.fixed()]
    free     = list(set(range(form.number_of_vertices())) - set(fixed) - set(leaves))
    internal = [i for i, (u, v) in enumerate(form.edges()) if k_i[u] not in leaves and k_i[v] not in leaves]

    _k_i   = dict((key, index) for index, key in enumerate(force.vertices()))
    _i_k   = dict((index, key) for index, key in enumerate(force.vertices()))
    _xy    = array(force.xy(), dtype=float64)
    _edges = force.ordered_edges(form)
    _C     = connectivity_matrix(_edges, 'csr')
    _uv_e  = dict(((_i_k[i], _i_k[j]), e) for e, (i, j) in enumerate(_edges))

    _free = [key for key, attr in force.vertices(True) if attr['is_param']]
    _free = [_k_i[key] for key in _free]

    def objfunc(_x):
        _xy[_free, 0] = _x

        update_form_from_force(xy, _xy, free, leaves, i_j, ij_e, _C)

        l   = normrow(C.dot(xy))
        _l  = normrow(_C.dot(_xy))
        li  = l[internal]
        _li = _l[internal]
        lp  = li.T.dot(_li)[0, 0]

        print(lp)

        return(lp)

    x0     = _xy[_free, 0]
    # bounds = [(None, 0) for i in range(len(_free))]
    res = minimize(
        objfunc,
        x0,
        method=algo,
        tol=1e-12,
        # bounds=bounds,
        options={'maxiter': 1000}
    )

    print(res)

    uv  = C.dot(xy)
    _uv = _C.dot(_xy)
    a   = [angle_vectors_xy(uv[i], _uv[i]) for i in range(len(edges))]

    print(a)

    l   = normrow(uv)
    _l  = normrow(_uv)
    q   = _l / l

    for key, attr in form.vertices(True):
        index = k_i[key]
        attr['x'] = xy[index, 0]
        attr['y'] = xy[index, 1]

    for u, v, attr in form.edges(True):
        e = uv_e[(u, v)]
        attr['l'] = l[e, 0]
        attr['a'] = a[e]
        if (a[e] - 3.14159) ** 2 < 1e-1:
            attr['f'] = - _l[e, 0]
            attr['q'] = - q[e, 0]
        else:
            attr['f'] = _l[e, 0]
            attr['q'] = q[e, 0]

    for key, attr in force.vertices(True):
        index = _k_i[key]
        attr['x'] = _xy[index, 0]
        attr['y'] = _xy[index, 1]

    for u, v, attr in force.edges(True):
        e = _uv_e[(u, v)]
        attr['a'] = a[e]
        attr['l'] = _l[e, 0]


# ==============================================================================
# Main
# ==============================================================================

if __name__ == "__main__":
    pass
