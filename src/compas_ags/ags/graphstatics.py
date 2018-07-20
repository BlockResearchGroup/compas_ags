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


__author__     = ['Tom Van Mele', ]
__copyright__  = 'Copyright 2014, BLOCK Research Group - ETH Zurich'
__license__    = 'MIT license'
__email__      = 'vanmelet@ethz.ch'


__all__ = [
    'identify_dof',
    'identify_dof_xfunc',
    'count_dof',
    'count_dof_xfunc',
    'update_q_from_qind',
    'update_q_from_qind_xfunc',
    'update_forcedensity',
    'update_forcedensity_xfunc',
    'update_formdiagram',
    'update_formdiagram_xfunc',
    'update_forcediagram',
    'update_forcediagram_xfunc',
    'modify_formdiagram',
    'modify_formdiagram_xfunc',
    'modify_forcediagram',
    'modify_forcediagram_xfunc',
]


EPS  = 1 / sys.float_info.epsilon


def identify_dof_xfunc(formdata):
    from compas_tna.diagrams import FormDiagram
    form = FormDiagram.from_data(formdata)
    return identify_dof(form)


def count_dof_xfunc(formdata):
    from compas_tna.diagrams import FormDiagram
    form = FormDiagram.from_data(formdata)
    return count_dof(form)


def update_q_from_qind_xfunc(form):
    pass


def update_forcedensity_xfunc(form):
    from compas_ags.diagrams import FormDiagram
    form = FormDiagram.from_data(form)
    update_forcedensity(form)
    return form.to_data()


def update_formdiagram_xfunc(form, force, kmax=100):
    from compas_ags.diagrams import FormDiagram
    from compas_ags.diagrams import ForceDiagram
    form = FormDiagram.from_data(form)
    force = ForceDiagram.from_data(force)
    update_formdiagram(form, force, kmax=kmax)
    return form.to_data()


def update_forcediagram_xfunc(force, form):
    from compas_ags.ags.diagrams.formdiagram import FormDiagram
    from compas_ags.ags.diagrams.forcediagram import ForceDiagram
    form = FormDiagram.from_data(form)
    force = ForceDiagram.from_data(force)
    update_forcediagram(force, form)
    return force.to_data()


def identify_dof(form):
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


def count_dof(form):
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
    xy    = form.xy()
    fixed = [k_i[key] for key in form.fixed()]
    free  = list(set(range(len(form.vertex))) - set(fixed))
    edges = [(k_i[u], k_i[v]) for u, v in form.edges()]
    C     = connectivity_matrix(edges)
    E     = equilibrium_matrix(C, xy, free)
    k, m  = dof(E)
    return k, m


# ==============================================================================
# update
# ==============================================================================


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


def update_forcedensity(form):
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


def update_formdiagram(form, force, kmax=100):
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
    i_j    = {i: [k_i[n] for n in form.vertex_neighbours(k)] for i, k in enumerate(form.vertices())}
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
    _update_formdiagram(xy, _xy, free, leaves, i_j, ij_e, _C, kmax=kmax)
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


def _update_formdiagram(xy, _xy, free, leaves, i_j, ij_e, _C, kmax=100):
    _uv = _C.dot(_xy)
    _t  = normalizerow(_uv)
    I   = eye(2, dtype=float64)
    xy0 = xy.copy()
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


def update_forcediagram(force, form):
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


# ==============================================================================
# modify
# ==============================================================================


def modify_formdiagram_xfunc():
    pass


def modify_formdiagram():
    pass


def modify_forcediagram():
    pass


def modify_forcediagram_xfunc():
    pass


# ==============================================================================
# Debugging
# ==============================================================================

if __name__ == "__main__":

    pass
