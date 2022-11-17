from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

from numpy import array
from numpy import float64

from scipy.optimize import minimize

from compas.geometry import angle_vectors_xy

from compas.numerical import connectivity_matrix
from compas.numerical import normrow

from compas_ags.ags.core import update_primal_from_dual


__all__ = [
    "compute_loadpath",
    "compute_external_work",
    "compute_internal_work",
    "compute_internal_work_tension",
    "compute_internal_work_compression",
    "optimise_loadpath",
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
    """
    return compute_internal_work(form, force)


def compute_external_work(form, force):
    """Compute the external work of a structure.

    The external work done by a structure is equal to the work done by the external
    forces. This is equal to the sum of the dot products of the force vectors and
    the vectors defined by the force application point and a fixed arbitrary point.

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

    Examples
    --------
    >>>

    """
    vertex_index = form.vertex_index()
    xy = array(form.xy(), dtype=float64)
    edges = [(vertex_index[u], vertex_index[v]) for u, v in form.edges()]
    C = connectivity_matrix(edges, "csr")

    _vertex_index = force.vertex_index()
    _xy = force.xy()
    _edges = force.ordered_edges(form)
    _edges[:] = [(_vertex_index[u], _vertex_index[v]) for u, v in _edges]
    _C = connectivity_matrix(_edges, "csr")

    leaves = set(form.leaves())
    external = [i for i, (u, v) in enumerate(form.edges()) if u in leaves or v in leaves]

    lengths = normrow(C.dot(xy))
    forces = normrow(_C.dot(_xy))

    return lengths[external].T.dot(forces[external])[0, 0]


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

    Examples
    --------
    >>>

    """
    vertex_index = form.vertex_index()
    xy = array(form.xy(), dtype=float64)
    edges = [(vertex_index[u], vertex_index[v]) for u, v in form.edges()]
    C = connectivity_matrix(edges, "csr")

    _vertex_index = force.vertex_index()
    _xy = force.xy()
    _edges = force.ordered_edges(form)
    _edges[:] = [(_vertex_index[u], _vertex_index[v]) for u, v in _edges]
    _C = connectivity_matrix(_edges, "csr")

    leaves = set(form.leaves())
    internal = [i for i, (u, v) in enumerate(form.edges()) if u not in leaves and v not in leaves]

    lengths = normrow(C.dot(xy))
    forces = normrow(_C.dot(_xy))

    return lengths[internal].T.dot(forces[internal])[0, 0]


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

    Examples
    --------
    >>>

    """
    vertex_index = form.vertex_index()
    xy = array(form.xy(), dtype=float64)
    edges = [(vertex_index[u], vertex_index[v]) for u, v in form.edges()]
    C = connectivity_matrix(edges, "csr")
    q = array(form.q(), dtype=float64).reshape((-1, 1))

    _vertex_index = force.vertex_index()
    _xy = force.xy()
    _edges = force.ordered_edges(form)
    _edges[:] = [(_vertex_index[u], _vertex_index[v]) for u, v in _edges]
    _C = connectivity_matrix(_edges, "csr")

    leaves = set(form.leaves())
    internal = [i for i, (u, v) in enumerate(form.edges()) if u not in leaves and v not in leaves]
    tension = [i for i in internal if q[i, 0] > 0]

    lengths = normrow(C.dot(xy))
    forces = normrow(_C.dot(_xy))

    return lengths[tension].T.dot(forces[tension])[0, 0]


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

    Examples
    --------
    >>>

    """
    vertex_index = form.vertex_index()
    xy = array(form.xy(), dtype=float64)
    edges = [(vertex_index[u], vertex_index[v]) for u, v in form.edges()]
    C = connectivity_matrix(edges, "csr")
    q = array(form.q(), dtype=float64).reshape((-1, 1))

    _vertex_index = force.vertex_index()
    _xy = force.xy()
    _edges = force.ordered_edges(form)
    _edges[:] = [(_vertex_index[u], _vertex_index[v]) for u, v in _edges]
    _C = connectivity_matrix(_edges, "csr")

    leaves = set(form.leaves())
    internal = [i for i, (u, v) in enumerate(form.edges()) if u not in leaves and v not in leaves]
    compression = [i for i in internal if q[i, 0] < 0]

    lengths = normrow(C.dot(xy))
    forces = normrow(_C.dot(_xy))

    return lengths[compression].T.dot(forces[compression])[0, 0]


def optimise_loadpath(form, force, algo="COBYLA"):
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
    form: :class:`FormDiagram`
        The optimised form diagram.
    force: :class:`ForceDiagram`
        The optimised force diagram.

    Notes
    -----
    In many cases, the number of paramters of the force domain involved in generating
    new solutions in the form domain is smaller than when using the elements of the
    form diagram directly.

    For example, the loadpath of a bridge with a compression arch can be optimised
    using only the x-coordinates of the vertices of the force diagram corresponding
    to internal spaces formed by the segments of the arch, the corresponding deck
    elements, and the hangers connecting them. Any solution generated by these parameters
    will be in equilibrium and automatically have a horizontal bridge deck.

    Although the *BRG* algorithm is the preferred choice, since it is (should be)
    tailored to the problem of optimising loadpaths using the domain of the force
    diagram, it does not have a stable and/or efficient implementation.
    The main problem is the generation of the form diagram, based on a given force
    diagram. For example, when edge forces flip from tension to compression, and
    vice versa, parallelisation is no longer effective.

    """
    vertex_index = form.vertex_index()
    edge_index = form.edge_index()
    i_j = {
        vertex_index[vertex]: [vertex_index[nbr] for nbr in form.vertex_neighbors(vertex)] for vertex in form.vertices()
    }
    ij_e = {(vertex_index[u], vertex_index[v]): edge_index[u, v] for u, v in edge_index}
    ij_e.update({(vertex_index[v], vertex_index[u]): edge_index[u, v] for u, v in edge_index})

    xy = array(form.xy(), dtype=float64)
    edges = [(vertex_index[u], vertex_index[v]) for u, v in form.edges()]
    C = connectivity_matrix(edges, "csr")

    leaves = [vertex_index[key] for key in form.leaves()]
    fixed = [vertex_index[key] for key in form.fixed()]
    free = list(set(range(form.number_of_vertices())) - set(fixed) - set(leaves))
    internal = [
        i for i, (u, v) in enumerate(form.edges()) if vertex_index[u] not in leaves and vertex_index[v] not in leaves
    ]

    _vertex_index = force.vertex_index()
    _edge_index = force.edge_index(form)
    _edge_index.update({(v, u): _edge_index[u, v] for u, v in _edge_index})

    _xy = array(force.xy(), dtype=float64)
    _edges = force.ordered_edges(form)
    _edges[:] = [(_vertex_index[u], _vertex_index[v]) for u, v in _edges]
    _C = connectivity_matrix(_edges, "csr")

    _free = [key for key, attr in force.vertices(True) if attr["is_param"]]
    _free = [_vertex_index[key] for key in _free]

    def objfunc(_x):
        _xy[_free, 0] = _x

        update_primal_from_dual(xy, _xy, free, leaves, i_j, ij_e, _C)

        length = normrow(C.dot(xy))
        force = normrow(_C.dot(_xy))
        lp = length[internal].T.dot(force[internal])[0, 0]

        print(lp)
        return lp

    x0 = _xy[_free, 0]

    result = minimize(objfunc, x0, method=algo, tol=1e-12, options={"maxiter": 1000})  # noqa: F841

    uv = C.dot(xy)
    _uv = _C.dot(_xy)
    angles = [angle_vectors_xy(a, b) for a, b in zip(uv, _uv)]
    lengths = normrow(uv)
    forces = normrow(_uv)
    q = forces / lengths

    for vertex, attr in form.vertices(True):
        index = vertex_index[vertex]
        attr["x"] = xy[index, 0]
        attr["y"] = xy[index, 1]

    for edge, attr in form.edges(True):
        index = edge_index[edge]
        attr["l"] = lengths[index, 0]
        attr["a"] = angles[index]
        if (angles[index] - 3.14159) ** 2 < 0.25 * 3.14159:
            attr["f"] = -forces[index, 0]
            attr["q"] = -q[index, 0]
        else:
            attr["f"] = forces[index, 0]
            attr["q"] = q[index, 0]

    for vertex, attr in force.vertices(True):
        index = _vertex_index[vertex]
        attr["x"] = _xy[index, 0]
        attr["y"] = _xy[index, 1]

    for edge, attr in force.edges(True):
        index = _edge_index[edge]
        attr["a"] = angles[index]
        attr["l"] = forces[index, 0]

    return form, force


# ==============================================================================
# Main
# ==============================================================================

if __name__ == "__main__":
    pass
