from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

from time import time

from numpy import abs
from numpy import array
from numpy import dot
from numpy import float64
from numpy import matmul as mm
from numpy import newaxis
from numpy import sum
from numpy import sqrt
from numpy import tile
from numpy import transpose
from numpy import zeros
from numpy.linalg import pinv

from scipy.optimize import fmin_slsqp

from scipy.sparse import diags
from scipy.sparse.linalg import inv

from compas.numerical import connectivity_matrix
from compas.numerical import equilibrium_matrix
from compas.numerical import normrow
from compas.numerical import devo_numpy

from compas_ags.ags import identify_dof
from compas_ags.ags import update_forcediagram

from compas_ags.diagrams import compute_z
from compas_ags.diagrams import update_thrustdiagram


__author__     = ['Tom Van Mele <van.mele@arch.ethz.ch>',
                  'Andrew Liew <liew@arch.ethz.ch>']
__copyright__  = 'Copyright 2017, BLOCK Research Group - ETH Zurich'
__license__    = 'MIT License'
__email__      = 'van.mele@arch.ethz.ch'


__all__ = [
    'compute_loadpath3',

]


def compute_loadpath3(form, force):
    k_i   = form.key_index()
    xyz   = array(form.get_vertices_attributes('xyz'), dtype=float64)
    edges = [(k_i[u], k_i[v]) for u, v in form.edges()]
    C     = connectivity_matrix(edges, 'csr')
    q     = array(form.q(), dtype=float64).reshape((-1, 1))

    # leaves   = set(form.leaves())
    # internal = [i for i, u, v in enumerate(form.edges()) if u not in leaves and v not in leaves]

    l  = normrow(C.dot(xyz))
    f  = q * l
    # li = l[internal]
    # fi = f[internal]
    # return li.T.dot(fi)[0, 0]

    return l.T.dot(f)[0, 0]


def optimise_loadpath3(form,
                       force,
                       solver='devo',
                       gradient=False,
                       qmin=1e-6,
                       qmax=10,
                       population=20,
                       steps=100,
                       results=None,
                       qid0=None):
    """Finds the optimised loadpath for a FormDiagram with given loads.

    Parameters
    ----------
    form : FormDiagram
        The form diagram.
    force : ForceDiagram
        The force diagram.
    solver : {'devo', 'slsqp'}, optional
        Solver to use.
    gradient : bool, optional
        Use analytical gradient (True) or approximation (False).
        Default is ``False``.
    qmin : float, optional
        Minimum qid value. Default is ``1e-6``.
    qmax : float, optional
        Maximum qid value. Default is ``10``.
    population : int, optional
        Number of agents for Differential Evolution.
        Default is ``10``.
    steps : int, optional
        Number of iteration steps.
        Default is ``100``.
    results : str, optional
        Path for saving results.
        Default is ``None``.
    qid0 : obj, optional
        Initial starting point qid0 (for slsqp).
        Default is ``None``.

    Returns
    -------
    float
        Optimum load-path value.
    array
        Optimum qids

    Notes
    -----
    ...

    References
    ----------
    ...

    Examples
    --------
    .. code-block:: python

        #

    """
    k, ind, dep, uv = get_ind_dep(form)
    k_i = form.key_index()
    edges = [(k_i[u], k_i[v]) for u, v in form.edges()]
    fixed = [k_i[key] for key in form.fixed()]
    free = list(set(range(form.number_of_vertices())) - set(fixed))
    xy = array(form.xy())
    C = connectivity_matrix(edges, 'csr')
    E = equilibrium_matrix(C, xy, free, 'csr')
    lh = normrow(C.dot(xy))
    bounds = [[qmin, qmax]] * k
    i_uv = form.index_uv()
    args = (i_uv, ind, dep, E, form, lh, fixed, free, C)
    form.update_default_edge_attributes({'q': 1.0})

    tic = time()
    print('\n' + '-' * 50)
    if solver == 'devo':
        print('Differential Evolution started...')
        fopt, qopt = diff_evo(form, force, bounds, population, steps, results, args)
        print('\n' + '-' * 50)
        print('Differential Evolution finished : {0:.4g} s'.format(time() - tic))
    elif solver == 'slsqp':
        print('SLSQP started...')
        fopt, qopt = slsqp(form, force, qid0, bounds, gradient, steps, args, uv)
        print('\n' + '-' * 50)
        print('SLSQP finished : {0:.4g} s'.format(time() - tic))

    q = update_q(form, E, dep, ind, qopt)

    update_form_force(form, force, i_uv, q, lh)

    print('fopt: {0:.3g}'.format(fopt))
    print('All branches compressive: {0}'.format(all(q >= 0)))
    print('Maximum qid: {0:.3g}'.format(max(qopt)))
    print('-' * 50 + '\n')

    return fopt, qopt


def get_ind_dep(form):
    """ Get independent and dependent branches of a FormDiagram.

    Parameters:
        form (obj): FormDiagram for degrees-of-freedom information.

    Returns:
        int: Number of degrees-of-freedom.
        list: Independent branches.
        list: Dependent branches.
        list: u v values of the independent branches.
    """
    k, m, uv = identify_dof(form, indexed=False)
    uv_i = form.uv_index()
    for u, v in uv:
        form.edge[u][v]['is_ind'] = True
    ind = [uv_i[(u, v)] for u, v in uv]
    dep = list(set(range(form.number_of_edges())) - set(ind))
    print('Form diagram has {0} DoF'.format(k))
    return k, ind, dep, uv


def qpositive(qid, *args):
    """ Function for non-negativity of force densities q.

    Parameters:
        qid (list): Independent force densities.

    Returns:
        array: q values to be >= 0.
    """
    i_uv, ind, dep, E, form = args[:5]
    q = update_q(form, E, dep, ind, qid)
    return q.ravel() - 10**(-6)


def slsqp(form, force, qid0, bounds, gradient, iterations, args, uv):
    """ Finds the optimised loadpath for a FormDiagram with given loads by SLSQP.

    Parameters:
        form (obj): FormDiagram.
        force (obj): ForceDiagram.
        qid0 (obj): Initial starting point qid0.
        bounds (list): [qmin, qmax] values for each DoF.
        gradient (bool): Use analytical gradient (True) or approximation (False).
        iterations (int): Number of iterations.
        args (tuple): Sequence of additional arguments.
        uv (list): The u, v values of the independent branches.

    Returns:
        float: Optimum load-path value.
        array: Optimum qids
    """
    i_uv, ind, dep, E, form, lh, fixed, free, C = args
    if not gradient:
        opt = fmin_slsqp(fint, qid0, args=args, disp=2, bounds=bounds, full_output=1, iter=iterations, f_ieqcons=qpositive)
    else:
        keys = list(form.vertices())
        xyz = array(form.get_vertices_attributes(['x', 'y', 'z'], keys=keys))
        pz = array(form.get_vertices_attribute('pz', keys=keys))[free]
        x = xyz[:, 0][:, newaxis]
        y = xyz[:, 1][:, newaxis]
        z = xyz[:, 2][:, newaxis]
        xb = x[fixed]
        yb = y[fixed]
        zb = z[fixed]
        xt = transpose(x)
        yt = transpose(y)
        Cb = C[:, fixed]
        Ci = C[:, free]
        Ct = C.transpose()
        Cit = Ci.transpose()
        Cbt = Cb.transpose()
        m = C.shape[0]
        K = zeros((m, len(ind)))
        uv_i = form.uv_index()
        c = 0
        for u, v in uv:
            K[uv_i[(u, v)], c] = 1
            c += 1
        K[dep, :] = dot(-pinv(E[:, dep].toarray()), E[:, ind].toarray())
        ei = zeros((m, m, 1))
        Ei = zeros((m, m, m))
        mr = range(m)
        ei[mr, mr, 0] = 1
        Ei[mr, mr, mr] = 1
        st = (m, 1, 1)
        K_ = tile(K, st)
        EiK_ = mm(Ei, K_)
        xbt_ = tile(transpose(xb), st)
        ybt_ = tile(transpose(yb), st)
        zbt_ = tile(transpose(zb), st)
        pzt_ = tile(transpose(pz), st)
        eipzt_ = mm(ei, pzt_)
        Cit_ = tile(Cit.toarray(), st)
        Cbt_ = tile(Cbt.toarray(), st)
        Cbtei_ = mm(Cbt_, ei)
        CtEiK_ = mm(mm(tile(Ct.toarray(), st), Ei), K_)
        xbtCbteixtCtEiK_ = mm(mm(mm(xbt_, Cbtei_), tile(xt, st)), CtEiK_)
        ybtCbteiytCtEiK_ = mm(mm(mm(ybt_, Cbtei_), tile(yt, st)), CtEiK_)
        args = (i_uv, ind, dep, E, form, C, Cb, Ci, Ct, Cit, xt, xb, yt, yb, zb, pz,
                Cit_, Cbt_, pzt_, eipzt_, EiK_, zbt_, xbtCbteixtCtEiK_, ybtCbteiytCtEiK_)
        opt = fmin_slsqp(fext, qid0, args=args, disp=2, bounds=bounds, full_output=1, iter=iterations, f_ieqcons=qpositive, fprime=gext)
    qopt = opt[0]
    fopt = opt[1]
    return fopt, qopt


def fext(qid, *args):
    """ Calculates the external loadpath for a given qid set.

    Parameters:
        qid (list): Independent force densities.
        args (tuple): Sequence of additional arguments.

    Returns:
        float: Scalar load-path value.
    """
    i_uv, ind, dep, E, form, C, Cb, Ci, Ct, Cit, xt, xb, yt, yb, zb, pz = args[:16]
    q = update_q(form, E, dep, ind, qid)
    Q = diags(q)
    Db = Cit.dot(Q).dot(Cb)
    Di = Cit.dot(Q).dot(Ci)
    CtQCb = (Ct.dot(Q)).dot(Cb)
    pztDiinv = mm(transpose(pz), inv(Di).toarray())
    f = (mm(xt, CtQCb.dot(xb)) + mm(yt, CtQCb.dot(yb)) + mm(pztDiinv, pz) - mm(pztDiinv, Db.dot(zb)))
    return f[0][0]


def gext(qid, *args):
    """ Calculates the gradient of the external loadpath for a given qid set.

    Parameters:
        qid (list): Independent force densities.
        args (tuple): Sequence of additional arguments.

    Returns:
        array: Load-path gradient at given qid.
    """
    i_uv, ind, dep, E, form, C, Cb, Ci, Ct, Cit, xt, xb, yt, yb, zb, pz, \
        Cit_, Cbt_, pzt_, eipzt_, EiK_, zbt_, xbtCbteixtCtEiK_, ybtCbteiytCtEiK_ = args
    q = update_q(form, E, dep, ind, qid)
    Q = diags(q)
    Db = Cit.dot(Q).dot(Cb)
    Di = Cit.dot(Q).dot(Ci)
    st = (C.shape[0], 1, 1)
    Dbt_ = tile((Db.transpose()).toarray(), st)
    DiinvCit_ = mm(tile(inv(Di).toarray(), st), Cit_)
    eipztDiinvCitEiK_ = mm(eipzt_, mm(DiinvCit_, EiK_))
    g = sum(xbtCbteixtCtEiK_ + ybtCbteiytCtEiK_ - mm(mm(pzt_, DiinvCit_), eipztDiinvCitEiK_) +
            mm(mm(zbt_, (mm(Dbt_, DiinvCit_) - Cbt_)), eipztDiinvCitEiK_), axis=0)[0]
    return g


def fint(qid, *args):
    """ Calculates the internal load-path for a given qid set.

    Parameters:
        qid (list): Independent force densities.
        args (tuple): Sequence of additional arguments.

    Returns:
        float: Scalar load-path value.
    """
    i_uv, ind, dep, E, form, lh, fixed, free, C = args
    q = update_q(form, E, dep, ind, qid)
    keys = list(form.vertices())
    xyz = array(form.get_vertices_attributes(['x', 'y', 'z'], keys=keys))
    p = array(form.get_vertices_attributes(['px', 'py', 'pz'], keys=keys))
    compute_z(xyz, diags(q), C, p, free, fixed)
    l2 = lh**2 + C.dot(xyz[:, 2][:, newaxis])**2
    f = dot(abs(transpose(q)), l2)
    if any(q < 0):
        return 10**6 + sum(q[q < 0]**2)
    return f


def update_q(form, E, dep, ind, qid):
    """ Update the qdep from qid values.

    Parameters:
        form (obj): FormDiagram.
        E (array): Equillibrium matrix.
        dep (list): Dependent branches.
        ind (list): Independent branches.
        qid (list): Independent force densities.

    Returns:
        array: Updated q values.
    """
    q = array(form.q())
    q[ind] = qid
    Adinv = pinv(E[:, dep].toarray())
    Aid = E[:, ind].toarray()
    q[dep] = dot(dot(-Adinv, Aid), q[ind])
    return q


def diff_evo(form, force, bounds, population, steps, results, args):
    """ Finds the optimised loadpath for a FormDiagram with given loads by Differential Evolution.

    Parameters:
        form (obj): FormDiagram.
        force (obj): ForceDiagram.
        bounds (list): [qmin, qmax] values for each DoF.
        population (int): Number of agents.
        steps (int): Number of iteration steps.
        results (str): Path for saving results.
        args (tuple): Sequence of additional arguments.

    Returns:
        float: Optimum load-path value.
        array: Optimum qids
    """
    fopt, qopt = devo_numpy(fint, bounds=bounds, population=population, iterations=steps, results=results, args=args)
    return fopt, qopt


def update_form_force(form, force, i_uv, q, lh):
    """ Updates the form and force diagrams.

    Parameters:
        form (obj): FormDiagram to update.
        force (obj): ForceDiagram to update.
        i_uv (dic): Index to u v dictionary.
        q (array): Final force densities.
        lh (array): Horizontal lengths.

    Returns:
        None
    """
    f = q * lh.ravel()
    for c, qc in enumerate(q):
        u, v = i_uv[c]
        form.set_edge_attributes(u, v, {
            'q': float(qc),
            'f': float(f[c]),
            'l': float(lh[c])})
    update_thrustdiagram(form, force)
    update_forcediagram(force, form)


def global_scale(form):
    """ Applies the optimum global scale for a given form diagram.

    Parameters:
        form (obj): FormDiagram with applied force densities.

    Returns:
        float: Updated load path value.
        list: Updated force densities.
    """
    k_i = form.key_index()
    edges = [(k_i[u], k_i[v]) for u, v in form.edges()]
    C = connectivity_matrix(edges, 'csr')
    xy = array(form.xy())
    lh = normrow(C.dot(xy))
    q = array(form.q())
    qt = q.transpose()
    update_thrustdiagram(form, [])
    xyz0 = array(form.get_vertices_attributes(['x', 'y', 'z'], keys=list(form.vertices())))
    z0 = xyz0[:, 2][:, newaxis]
    w0 = C.dot(z0)
    rmin = sqrt(dot(qt, lh**2) / (dot(qt, w0**2)))
    z = z0 * rmin
    l2 = lh**2 + C.dot(z)**2
    q /= rmin
    fopt = dot(q.transpose(), l2)
    i_k = form.index_key()
    for i in range(len(z0)):
        form.vertex[i_k[i]]['z'] = float(z[i])
    f = q * lh.ravel()
    uv_i = form.uv_index()
    for u, v, attr in form.edges(True):
        i = uv_i[(u, v)]
        attr['q'] = float(q[i])
        attr['f'] = float(f[i])
    return fopt, list(q)


# ==============================================================================
# Debugging
# ==============================================================================

if __name__ == "__main__":
    pass
