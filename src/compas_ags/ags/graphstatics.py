from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

from numpy import array
from numpy import float64
from numpy import delete
from numpy import vstack
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
from compas.numerical import nullspace as matrix_nullspace

from compas_ags.ags.core import update_q_from_qind
from compas_ags.ags.core import update_primal_from_dual
from compas_ags.ags.core import get_jacobian_and_residual
from compas_ags.ags.core import compute_jacobian
from compas_ags.ags.core import parallelise_edges

from compas_ags.exceptions import SolutionError


__all__ = [
    "form_identify_dof",
    "form_count_dof",
    "form_update_q_from_qind",
    "form_update_from_force",
    "form_update_from_force_newton",
    "force_update_from_form",
    "force_update_from_constraints",
    "update_diagrams_from_constraints",
]


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

    xy = form.vertices_attributes("xy")
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

    xy = form.vertices_attributes("xy")
    fixed = [vertex_index[vertex] for vertex in form.leaves()]
    free = list(set(range(form.number_of_vertices())) - set(fixed))
    edges = [(vertex_index[u], vertex_index[v]) for u, v in form.edges()]
    C = connectivity_matrix(edges)
    E = equilibrium_matrix(C, xy, free)

    k, m = dof(E)

    return int(k), int(m)


def form_compute_nullspace(form, force, constraints=None):
    r"""Compute the nullspaces of a form diagram assuming a set of constraints.

    It returns a list with the displacements that apply to the form diagram representing
    how the latter can be moved in the plan without modifying the force diagram and
    considering the set of constraints applied. It corresponds to the nullspace of the
    Jacobian :math:`\partial \mathbf{X}^* / \partial \mathbf{X}` matrix as computed in [1].

    Parameters
    ----------
    form : :class:`FormDiagram`
        The form diagram.
    force : :class:`ForceDiagram`
        The force diagram.
    constraints: :class:`ConstraintsCollection`, optional
        A collection of form diagram constraints.
        The default is ``None``, in which case no constraints are considered.

    Returns
    -------
    nullspaces [list of arrays (vcount x 2)]
        The null displacement fields applied to the form diagram considering applied constraints.

    Notes
    -----
    Among the nullspaces, the unrestrained rigid-body displacements available are always
    included and other unrestrained displacement fields that preserve the orientation
    of all edges keeping reciprocity between form and force diagram. The displacement fields
    are unit vectors and can be rescaled to visialisation purposes.

    References
    ----------
    .. [1] Alic, V. and Åkesson, D., 2017. Bi-directional algebraic graphic statics. Computer-Aided Design, 93, pp.26-37.

    Examples
    --------
    >>>
    """
    jacobian = compute_jacobian(form, force)  # Jacobian matrix of size (2 _vcount, 2 vcount)
    if constraints:
        (cj, _) = constraints.compute_constraints()
        jacobian = vstack((jacobian, cj))  # Add rows to the Jacobian matrix representing constraints

    # Remove the rows of the jacobian to account for the anchored vertex in the force diagram (influence x and y directions)
    _vcount = force.number_of_vertices()
    _k_i = force.key_index()
    _anchor = _k_i[force.anchor()]
    _anchor_xy = [_anchor, _vcount + _anchor]

    reduced_jacobian = delete(jacobian, _anchor_xy, axis=0)

    nullstates = matrix_nullspace(reduced_jacobian).T  # unit vectors representing the possible nullstates

    nullspaces = []
    for nullstate in nullstates:  # reshaping the nullstates a list of (vcount x 2) arrays
        xy = nullstate.reshape((2, -1)).T
        nullspaces.append(xy)

    return nullspaces


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
    form: :class:`FormDiagram`
        The updated form diagram with force densities stored as attributes of the edges.

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
    C = connectivity_matrix(edges, "csr")
    E = equilibrium_matrix(C, xy, free, "csr")

    update_q_from_qind(E, q, dep, ind)

    uv = C.dot(xy)
    lengths = normrow(uv)
    forces = q * lengths

    for edge in form.edges():
        index = edge_index[edge]
        form.edge_attributes(edge, ["q", "f", "l"], [q[index, 0], forces[index, 0], lengths[index, 0]])

    return form


def form_update_from_force(form, force, kmax=100):
    r"""Update the form diagram after a modification of the force diagram.

    Parameters
    ----------
    form: :class:`FormDiagram`
        The form diagram to update.
    force : :class:`ForceDiagram`
        The force diagram on which the update is based.
    kmax: int, optional
        Maximum number of least-square iterations for solving the duality form-force.
        The default value is ``20``.

    Returns
    -------
    form: :class:`FormDiagram`
        The form diagram with updated force densities.
    force: :class:`ForceDiagram`
        The updated force diagram.

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
    i_j = {
        index: [vertex_index[nbr] for nbr in form.vertex_neighbors(vertex)]
        for index, vertex in enumerate(form.vertices())
    }
    ij_e = {(vertex_index[u], vertex_index[v]): edge_index[u, v] for u, v in edge_index}
    ij_e.update({(vertex_index[v], vertex_index[u]): edge_index[u, v] for u, v in edge_index})

    xy = array(form.xy(), dtype=float64)
    edges = [(vertex_index[u], vertex_index[v]) for u, v in form.edges()]
    C = connectivity_matrix(edges, "csr")
    # --------------------------------------------------------------------------
    # constraints
    # --------------------------------------------------------------------------
    leaves = [vertex_index[vertex] for vertex in form.leaves()]
    fixed = [vertex_index[vertex] for vertex in form.fixed()]
    free = list(set(range(form.number_of_vertices())) - set(fixed) - set(leaves))
    line_constraints_all = form.vertices_attribute("line_constraint")
    line_constraints = [line_constraints_all[i] for i in free]
    target_vectors = form.edges_attribute("target_vector")
    # --------------------------------------------------------------------------
    # force diagram
    # --------------------------------------------------------------------------
    _vertex_index = force.vertex_index()
    _edge_index = force.edge_index(form)
    _edge_index.update({(v, u): _edge_index[u, v] for u, v in _edge_index})

    _xy = array(force.xy(), dtype=float64)
    _edges = force.ordered_edges(form)
    _edges[:] = [(_vertex_index[u], _vertex_index[v]) for u, v in _edges]
    _C = connectivity_matrix(_edges, "csr")
    # --------------------------------------------------------------------------
    # compute the coordinates of thet *free* vertices
    # as a function of the fixed vertices and the previous coordinates of the *free* vertices
    # re-add the leaves and leaf-edges
    # --------------------------------------------------------------------------
    update_primal_from_dual(
        xy,
        _xy,
        free,
        i_j,
        ij_e,
        _C,
        line_constraints=line_constraints,
        target_vectors=target_vectors,
        leaves=leaves,
        kmax=kmax,
    )
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
        attr["x"] = xy[index, 0]
        attr["y"] = xy[index, 1]
    for edge, attr in form.edges(True):
        index = edge_index[edge]
        attr["l"] = lengths[index, 0]
        attr["a"] = angles[index]
        if angles[index] < 90:
            attr["f"] = forces[index, 0]
            attr["q"] = q[index, 0]
        else:
            attr["f"] = -forces[index, 0]
            attr["q"] = -q[index, 0]
    # --------------------------------------------------------------------------
    # update force diagram
    # --------------------------------------------------------------------------
    for edge, attr in force.edges(True):
        index = _edge_index[edge]
        attr["a"] = angles[index]
        attr["l"] = forces[index, 0]

    return form, force


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
    form: :class:`FormDiagram`
        The updated form diagram.

    References
    ----------
    .. [1] Alic, V. and Åkesson, D., 2017. Bi-directional algebraic graphic statics. Computer-Aided Design, 93, pp.26-37.

    Examples
    --------
    >>>

    """
    X = array(form.vertices_attribute("x") + form.vertices_attribute("y")).reshape(-1, 1)
    _X_goal = array(force.vertices_attribute("x") + force.vertices_attribute("y")).reshape(-1, 1)

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
            form.vertex_attribute(vertex, "x", X[i].item())
            form.vertex_attribute(vertex, "y", X[i + vcount].item())

        diff = norm(red_r)
        if n_iter > max_iter:
            raise SolutionError("Did not converge")

        print("i: {0:0} diff: {1:.2e}".format(n_iter, float(diff)))
        n_iter += 1

    print("Converged in {0} iterations".format(n_iter))

    return form


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
    force: :class:`ForceDiagram`
        The updated force diagram.
    """
    # --------------------------------------------------------------------------
    # form diagram
    # --------------------------------------------------------------------------
    vertex_index = form.vertex_index()

    xy = array(form.xy(), dtype=float64)
    edges = [[vertex_index[u], vertex_index[v]] for u, v in form.edges_where({"_is_edge": True})]
    C = connectivity_matrix(edges, "csr")
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
    _C = connectivity_matrix(_edges, "csr")
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
        attr["x"] = _xy[index, 0]
        attr["y"] = _xy[index, 1]

    return force


def force_update_from_form_geometrical(force, form, kmax=100):
    """Update the force diagram after modifying the (geometry of) the form diagram.

    Parameters
    ----------
    force : :class:`ForceDiagram`
        The force diagram on which the update is based.
    form : :class:`FormDiagram`
        The form diagram to update.
    kmax: int, optional
        Maximum number of least-square iterations for solving the duality form-force.
        The default value is ``20``.

    Returns
    -------
    force :class:`ForceDiagram`
        The updated force diagram.
    """
    # --------------------------------------------------------------------------
    # form diagram
    # --------------------------------------------------------------------------
    vertex_index = form.vertex_index()

    xy = array(form.xy(), dtype=float64)
    edges = [(vertex_index[u], vertex_index[v]) for u, v in form.edges()]
    C = connectivity_matrix(edges, "csr")

    # --------------------------------------------------------------------------
    # force diagram
    # --------------------------------------------------------------------------
    _vertex_index = force.vertex_index()
    _edge_index = force.edge_index(form)
    _edge_index.update({(v, u): _edge_index[u, v] for u, v in _edge_index})

    _xy = array(force.xy(), dtype=float64)
    _edges = force.ordered_edges(form)
    _edges[:] = [(_vertex_index[u], _vertex_index[v]) for u, v in _edges]

    _i_j = {
        index: [_vertex_index[nbr] for nbr in force.vertex_neighbors(vertex)]
        for index, vertex in enumerate(force.vertices())
    }
    _ij_e = {(_vertex_index[u], _vertex_index[v]): _edge_index[u, v] for u, v in _edge_index}
    _ij_e.update({(_vertex_index[v], _vertex_index[u]): _edge_index[u, v] for u, v in _edge_index})

    # --------------------------------------------------------------------------
    # constraints
    # --------------------------------------------------------------------------
    _fixed = [_vertex_index[vertex] for vertex in force.fixed()]
    _free = list(set(range(force.number_of_vertices())) - set(_fixed))
    # _fixed_x = [_vertex_index[vertex] for vertex in force.fixed_x()]
    # _fixed_y = [_vertex_index[vertex] for vertex in force.fixed_y()]
    _line_constraints_all = force.vertices_attribute("line_constraint")
    _line_constraints = [_line_constraints_all[i] for i in _free]
    _target_lengths = form.edges_attribute("target_force")
    _target_vectors = [force.edge_attribute(edge, "target_vector") for edge in force.ordered_edges(form)]

    # --------------------------------------------------------------------------
    # compute the coordinates of the *free* vertices of the force diagram
    # as a function of the fixed vertices and the previous coordinates of the *free* vertices
    # --------------------------------------------------------------------------
    update_primal_from_dual(
        _xy,
        xy,
        _free,
        _i_j,
        _ij_e,
        C,
        line_constraints=_line_constraints,
        target_lengths=_target_lengths,
        target_vectors=_target_vectors,
        kmax=kmax,
    )

    # --------------------------------------------------------------------------
    # update force diagram
    # --------------------------------------------------------------------------
    for vertex, attr in force.vertices(True):
        index = _vertex_index[vertex]
        attr["x"] = _xy[index, 0]
        attr["y"] = _xy[index, 1]

    return force


def force_update_from_constraints(force, kmax=100):
    """Update the force diagram from constraints on length and orientation imposed in the form diagram,
    and already carried out as attributes in the force diagram.

    Parameters
    ----------
    force : :class:`ForceDiagram`
        The force diagram on which the update is based.
    kmax: int, optional
        Maximum number of parallelisation iterations for updating the force diagram.
        The default value is ``100``.

    Returns
    -------
    force :class:`ForceDiagram`
        The updated force diagram.
    """

    # --------------------------------------------------------------------------
    # parameters from force diagram
    # --------------------------------------------------------------------------
    _k_i = force.vertex_index()
    _xy = force.vertices_attributes("xy")
    _edges = list(force.edges())
    _edges = [(_k_i[u], _k_i[v]) for u, v in _edges]
    _i_nbrs = {_k_i[key]: [_k_i[nbr] for nbr in force.vertex_neighbors(key)] for key in force.vertices()}
    _uv_i = {uv: index for index, uv in enumerate(_edges)}
    _ij_e = {(u, v): index for (u, v), index in iter(_uv_i.items())}

    # --------------------------------------------------------------------------
    # fixity from constraints on force diagram
    # --------------------------------------------------------------------------
    fixed_force = [key for key in force.vertices_where({"is_fixed": True})]
    _fixed = [_k_i[key] for key in fixed_force]
    line_constraints = force.vertices_attribute("line_constraint")

    # --------------------------------------------------------------------------
    # edge orientations and edge target lengths
    # --------------------------------------------------------------------------
    target_lengths = [force.dual_edge_targetforce(edge) for edge in force.edges()]
    target_vectors = force.edges_attribute("target_vector")

    # --------------------------------------------------------------------------
    # Paralelise edge given force targets and/or target_lengths
    # --------------------------------------------------------------------------
    parallelise_edges(
        _xy,
        _edges,
        _i_nbrs,
        _ij_e,
        target_vectors,
        target_lengths,
        fixed=_fixed,
        line_constraints=line_constraints,
        kmax=kmax,
    )

    # --------------------------------------------------------------------------
    # update force diagram geometry
    # --------------------------------------------------------------------------
    for key in force.vertices():
        i = _k_i[key]
        x, y = _xy[i]
        force.vertex_attribute(key, "x", x)
        force.vertex_attribute(key, "y", y)

    return force


# ==============================================================================
# dual modifications
# ==============================================================================


def update_diagrams_from_constraints(form, force, max_iter=20, kmax=20, callback=None):
    """Update the form and force diagram after constraints / or movements are imposed to the diagrams.

    Parameters
    ----------
    form : :class:`FormDiagram`
        The form diagram.
    force : :class:`ForceDiagram`
        The force diagram.
    max_iter: int, optional
        Maximum number of iterations to update the diagrams.
        The default value is ``20``.
    kmax: int, optional
        Maximum number of least-square iterations for solving the duality form-force.
        The default value is ``20``.
    callback: callable, optional
        Callable function at the end of each iteration.
        The default value is ``None``.

    Returns
    -------
    form: :class:`FormDiagram`
        The updated form diagram.
    force: :class:`ForceDiagram`
        The updated force diagram.
    """

    form.dual = force
    force.dual = form

    niter = 0

    while niter < max_iter:
        # Propose a force diagram based on constraints -> Using paralellise
        force_update_from_constraints(force)

        if callback:
            callback(form, force)

        # Find geometrical dual form diagram respecting form constraints -> Using Least-Squares
        form_update_from_force(form, force, kmax=kmax)

        if callback:
            callback(form, force)

        # Find geometrical dual force diagram respecting force constraints -> Using Least-Squares
        force_update_from_form_geometrical(force, form, kmax=kmax)

        if callback:
            callback(form, force)

        niter += 1

    return form, force


# ==============================================================================
# Main
# ==============================================================================

if __name__ == "__main__":
    pass
