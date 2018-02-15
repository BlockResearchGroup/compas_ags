
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from numpy import abs
from numpy import array
from numpy import dot
from numpy import float64
#from numpy import matmul as mm
from numpy import newaxis
from numpy import ones
from numpy import sum
#from numpy import sqrt
#from numpy import tile
from numpy import zeros
from numpy.linalg import pinv

from scipy.optimize import fmin_slsqp
from scipy.sparse import diags
from scipy.sparse.linalg import spsolve
from scipy.sparse import csr_matrix

from compas.numerical import connectivity_matrix
from compas.numerical import devo_numpy
from compas.numerical import equilibrium_matrix
from compas.numerical import ga
from compas.numerical import normrow
from compas.numerical import nonpivots
from compas.numerical import rref

from time import time

import sympy
import os


__author__    = ['Andrew Liew <liew@arch.ethz.ch>', 'Tom Van Mele <van.mele@arch.ethz.ch>', ]
__copyright__ = 'Copyright 2018, BLOCK Research Group - ETH Zurich'
__license__   = 'MIT License'
__email__     = 'liew@arch.ethz.ch'


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


def optimise_loadpath3(form, solver='devo', gradient=False, qmin=1e-6, qmax=10, population=20, steps=100, qid0=None,
                       polish=0):

    """Finds the optimised loadpath for a FormDiagram with given loads.

    Parameters
    ----------
    form : obj
        The FormDiagram.
    solver : str
        'devo', 'ga' or 'slsqp' solver to use.
    gradient : bool
        Use analytical gradient (True) or approximation (False).
    qmin : float
        Minimum qid value.
    qmax : float
        Maximum qid value.
    population : int
        Number of agents for Differential Evolution.
    steps : int
        Number of iteration steps.
    qid0 : list
        Initial starting point qid0 (for slsqp).
    polish : bool
        Use L-BFGS-B polish.

    Returns
    -------
    float
        Optimum load-path value.
    list
        Optimum qids

    """

    # Mapping

    k_i = form.key_index()
    i_k = form.index_key()
    i_uv = form.index_uv()
    uv_i = form.uv_index()

    # Vertices and edges

    n = form.number_of_vertices()
    form.identify_fixed()
    fixed = [k_i[key] for key in form.fixed()]
    free = list(set(range(form.number_of_vertices())) - set(fixed))
    edges = [(k_i[u], k_i[v]) for u, v in form.edges()]

    # Co-ordinates and loads

    xyz = zeros((n, 3))
    pz = zeros(n)
    for key, vertex in form.vertex.items():
        i = k_i[key]
        xyz[i, :] = form.vertex_coordinates(key)
        pz[i] = vertex.get('pz', 1)
    xy = xyz[:, :2]
    z = xyz[:, 2]
    pzfree = pz[free]

    # Connectivity and equillibrium matrices

    C = connectivity_matrix(edges, 'csr')
    Ci = C[:, free]
    Cf = C[:, fixed]
    Cit = Ci.transpose()
    E = equilibrium_matrix(C, xy, free, 'csr').toarray()

    # Independent and dependent branches

    ind = nonpivots(sympy.Matrix(E).rref()[0].tolist())
    dep = list(set(range(form.number_of_edges())) - set(ind))
    for u, v in form.edges():
        if uv_i[(u, v)] in ind:
            form.edge[u][v]['is_ind'] = True
        else:
            form.edge[u][v]['is_ind'] = False
    k = len(ind)
    print('Form diagram has {0} independent branches'.format(len(ind)))

    Adinv = pinv(E[:, dep])
    Aid = E[:, ind]
    _AdinvAid = dot(-Adinv, Aid)
    _AdinvAid = csr_matrix(_AdinvAid)
    lh = normrow(C.dot(xy))
    lh2 = lh**2

    # Set-up

    q = ones((form.number_of_edges(), 1))
    bounds = [[qmin, qmax]] * k
    args = (q, ind, dep, _AdinvAid, C, Ci, Cit, Cf, pzfree, z, fixed, free, lh2)

    # Start optimisation

    print('\n' + '-' * 50)

    if solver == 'devo':

        args += (1,)
        fopt, qopt = diff_evo(form, bounds, population, steps, polish, args)

    if solver == 'ga':

        tic = time()
        args += (1,)
        fopt, qopt = diff_ga(form, bounds, population, steps, args)
        print('Genetic Algorithm finished : {0:.4g} s'.format(time() - tic))

    elif solver == 'slsqp':

        tic = time()
        print('SLSQP started...')
        args += (0,)
        fopt, qopt = slsqp(form, qid0, bounds, gradient, steps, args)
        print('\n' + '-' * 50)
        print('SLSQP finished : {0:.4g} s'.format(time() - tic))

    # Update FormDiagram

    q[ind, 0] = qopt
    q[dep] = _AdinvAid.dot(q[ind])
    z = z_from_qid(z, q, qopt, ind, dep, Ci, Cit, Cf, _AdinvAid, free, fixed, pzfree)

    for c, qi in enumerate(list(q.ravel())):
        u, v = i_uv[c]
        form.edge[u][v]['q'] = qi

    for i in range(n):
        form.vertex[i_k[i]]['z'] = z[i]

    # Print summary

    print('fopt: {0:.3g}'.format(fopt))
    print('All branches compressive: {0}'.format(all(q.ravel() >= 0)))
    print('Maximum qid: {0:.3g}'.format(max(qopt)))
    print('-' * 50 + '\n')

    return fopt, qopt


def fint(qid, *args):

    """ Calculates the internal loadpath for a given qid set.

    Parameters
    ----------
    qid : list
        Independent force densities.
    args : tuple
        Sequence of additional arguments.

    Returns
    -------
    float
        Scalar loadpath value.

    """

    q, ind, dep, _AdinvAid, C, Ci, Cit, Cf, pzfree, z, fixed, free, lh2, penalty = args
    z = z_from_qid(z, q, qid, ind, dep, Ci, Cit, Cf, _AdinvAid, free, fixed, pzfree)
    l2 = lh2 + C.dot(z[:, newaxis])**2
    f = dot(abs(q.transpose()), l2)

    if penalty and any(q[:] < 0):
        return 10.**6 + sum(q[q < 0]**2)
    return float(f[0])


def z_from_qid(z, q, qid, ind, dep, Ci, Cit, Cf, _AdinvAid, free, fixed, pzfree):

    """ Updates z for a given qid set.

    Parameters
    ----------
    z : array
        z co-ordinates
    q : array
        Array of force densities.
    qid : list
        Independent force densities.
    ind : list
        Indices of independent branches.
    dep : list
        Indices of dependent branches.
    Ci : sparse
        Free vertices entries of connectivity matrix.
    Cit : sparse
        Free vertices entries of connectivity matrix transposed.
    Cf : sparse
        Fixed vertices entries of connectivity matrix.
    _AdinvAid : array
        pinv(E[:, dep]) * E[:, ind]
    free : list
        Indices of free vertices.
    fixed : list
        Indices of fixed vertices.
    pzfree : array
        Vertical loads at free vertices.

    Returns
    -------
    array
        Updated z co-ordinates.

    """
    q[ind, 0] = qid
    q[dep] = _AdinvAid.dot(q[ind])
    Q = diags(q[:, 0])
    # b = pzfree - (Cit.dot(Q).dot(Cf)).dot(z[fixed])  # ignore if z[fixed] are all 0
    b = pzfree
    z[free] = spsolve(Cit.dot(Q).dot(Ci), b)

    return z


def qpositive(qid, *args):

    """ Function for non-negativity of force densities q.

    Parameters
    ----------
    qid : list
        Independent force densities.

    Returns
    -------
    array
        q values to be >= 0.

    """

    q, ind, dep, _AdinvAid, C, Ci, Cit, Cf, pzfree, z, fixed, free, lh2, penalty = args
    q[ind, 0] = qid
    q[dep] = _AdinvAid.dot(q[ind])

    return q.ravel() - 10.**(-3)


def slsqp(form, qid0, bounds, gradient, iterations, args):

    """ Finds the optimised loadpath for a FormDiagram with given loads by SLSQP.

    Parameters
    ----------
    form : obj
        FormDiagram.
    qid0 : obj
        Initial starting point qid0.
    bounds : list
        [qmin, qmax] values for each DoF.
    gradient : bool
        Use analytical gradient (True) or approximation (False).
    iterations : int
        Number of iterations.
    args : tuple
        Sequence of additional arguments.

    Returns
    -------
    float
        Optimum load-path value.
    array
        Optimum qids

    """

    q, ind, dep, _AdinvAid, C, Ci, Cit, Cf, pzfree, z, fixed, free, lh2, penalty = args

    if not gradient:

        opt = fmin_slsqp(fint, qid0, args=args, disp=2, bounds=bounds, full_output=1, iter=iterations, f_ieqcons=qpositive)

#    else:
#        keys = list(form.vertices())
#        xyz = array(form.get_vertices_attributes(['x', 'y', 'z'], keys=keys))
#        pz = array(form.get_vertices_attribute('pz', keys=keys))[free]
#        x = xyz[:, 0][:, newaxis]
#        y = xyz[:, 1][:, newaxis]
#        z = xyz[:, 2][:, newaxis]
#        xb = x[fixed]
#        yb = y[fixed]
#        zb = z[fixed]
#        xt = transpose(x)
#        yt = transpose(y)
#        Cb = C[:, fixed]
#        Ci = C[:, free]
#        Ct = C.transpose()
#        Cit = Ci.transpose()
#        Cbt = Cb.transpose()
#        m = C.shape[0]
#        K = zeros((m, len(ind)))
#        uv_i = form.uv_index()
#        c = 0
#        for u, v in uv:
#            K[uv_i[(u, v)], c] = 1
#            c += 1
#        K[dep, :] = dot(-pinv(E[:, dep].toarray()), E[:, ind].toarray())
#        ei = zeros((m, m, 1))
#        Ei = zeros((m, m, m))
#        mr = range(m)
#        ei[mr, mr, 0] = 1
#        Ei[mr, mr, mr] = 1
#        st = (m, 1, 1)
#        K_ = tile(K, st)
#        EiK_ = mm(Ei, K_)
#        xbt_ = tile(transpose(xb), st)
#        ybt_ = tile(transpose(yb), st)
#        zbt_ = tile(transpose(zb), st)
#        pzt_ = tile(transpose(pz), st)
#        eipzt_ = mm(ei, pzt_)
#        Cit_ = tile(Cit.toarray(), st)
#        Cbt_ = tile(Cbt.toarray(), st)
#        Cbtei_ = mm(Cbt_, ei)
#        CtEiK_ = mm(mm(tile(Ct.toarray(), st), Ei), K_)
#        xbtCbteixtCtEiK_ = mm(mm(mm(xbt_, Cbtei_), tile(xt, st)), CtEiK_)
#        ybtCbteiytCtEiK_ = mm(mm(mm(ybt_, Cbtei_), tile(yt, st)), CtEiK_)
#        args = (i_uv, ind, dep, E, form, C, Cb, Ci, Ct, Cit, xt, xb, yt, yb, zb, pz,
#                Cit_, Cbt_, pzt_, eipzt_, EiK_, zbt_, xbtCbteixtCtEiK_, ybtCbteiytCtEiK_)
#        opt = fmin_slsqp(fext, qid0, args=args, disp=2, bounds=bounds, full_output=1, iter=iterations, f_ieqcons=qpositive, fprime=gext)

    qopt = opt[0]
    fopt = opt[1]

    return fopt, qopt


#def fext(qid, *args):
#    """ Calculates the external loadpath for a given qid set.
#
#    Parameters:
#        qid (list): Independent force densities.
#        args (tuple): Sequence of additional arguments.
#
#    Returns:
#        float: Scalar load-path value.
#    """
#    i_uv, ind, dep, E, form, C, Cb, Ci, Ct, Cit, xt, xb, yt, yb, zb, pz = args[:16]
#    q = update_q(form, E, dep, ind, qid)
#    Q = diags(q)
#    Db = Cit.dot(Q).dot(Cb)
#    Di = Cit.dot(Q).dot(Ci)
#    CtQCb = (Ct.dot(Q)).dot(Cb)
#    pztDiinv = mm(transpose(pz), inv(Di).toarray())
#    f = (mm(xt, CtQCb.dot(xb)) + mm(yt, CtQCb.dot(yb)) + mm(pztDiinv, pz) - mm(pztDiinv, Db.dot(zb)))
#    return f[0][0]
#
#
#def gext(qid, *args):
#    """ Calculates the gradient of the external loadpath for a given qid set.
#
#    Parameters:
#        qid (list): Independent force densities.
#        args (tuple): Sequence of additional arguments.
#
#    Returns:
#        array: Load-path gradient at given qid.
#    """
#    i_uv, ind, dep, E, form, C, Cb, Ci, Ct, Cit, xt, xb, yt, yb, zb, pz, \
#        Cit_, Cbt_, pzt_, eipzt_, EiK_, zbt_, xbtCbteixtCtEiK_, ybtCbteiytCtEiK_ = args
#    q = update_q(form, E, dep, ind, qid)
#    Q = diags(q)
#    Db = Cit.dot(Q).dot(Cb)
#    Di = Cit.dot(Q).dot(Ci)
#    st = (C.shape[0], 1, 1)
#    Dbt_ = tile((Db.transpose()).toarray(), st)
#    DiinvCit_ = mm(tile(inv(Di).toarray(), st), Cit_)
#    eipztDiinvCitEiK_ = mm(eipzt_, mm(DiinvCit_, EiK_))
#    g = sum(xbtCbteixtCtEiK_ + ybtCbteiytCtEiK_ - mm(mm(pzt_, DiinvCit_), eipztDiinvCitEiK_) +
#            mm(mm(zbt_, (mm(Dbt_, DiinvCit_) - Cbt_)), eipztDiinvCitEiK_), axis=0)[0]
#    return g


def diff_evo(form, bounds, population, steps, polish, args):

    """ Finds the optimised loadpath for a FormDiagram with given loads, by Differential Evolution.

    Parameters
    ----------
    form : obj
        FormDiagram.
    bounds : list
        [qmin, qmax] values for each DoF.
    population : int
        Number of agents.
    steps : int
        Number of iteration steps.
    polish : bool
        Use L-BFGS-B polish.
    args : tuple
        Sequence of additional arguments.

    Returns
    -------
    float
        Optimum load-path value.
    array
        Optimum qids

    """

    return devo_numpy(fn=fint, bounds=bounds, population=population, generations=steps, polish=polish, args=args)


def diff_ga(form, bounds, population, steps, args):

    """ Finds the optimised loadpath for a FormDiagram with given loads, using a Genetic Algorithm.

    Parameters
    ----------
    form : obj
        FormDiagram.
    bounds : list
        [qmin, qmax] values for each DoF.
    population : int
        Number of agents.
    steps : int
        Number of iteration steps.
    args : tuple
        Sequence of additional arguments.

    Returns
    -------
    float
        Optimum load-path value.
    array
        Optimum qids

    """

    import compas

    num_var = len(bounds)
    num_bin_dig  = [10] * num_var
    output_path = os.path.join(compas.TEMP, 'ga_out/')
    elites = int(0.2 * population)

    if not os.path.exists(output_path):
        os.makedirs(output_path)

    ga_ = ga(fint, 'min', num_var, bounds, num_gen=steps, num_pop=population, num_elite=elites,
             num_bin_dig=num_bin_dig, output_path=output_path, min_fit=0.000001, mutation_probability=0.03,
             fargs=args, print_refresh=10)

    index = ga_.best_individual_index
    qopt = ga_.current_pop['scaled'][index]
    fopt = ga_.current_pop['fit_value'][index]

    return fopt, qopt


#def global_scale(form):
#    """ Applies the optimum global scale for a given form diagram.
#
#    Parameters:
#        form (obj): FormDiagram with applied force densities.
#
#    Returns:
#        float: Updated load path value.
#        list: Updated force densities.
#    """
#    k_i = form.key_index()
#    edges = [(k_i[u], k_i[v]) for u, v in form.edges()]
#    C = connectivity_matrix(edges, 'csr')
#    xy = array(form.xy())
#    lh = normrow(C.dot(xy))
#    q = array(form.q())
#    qt = q.transpose()
#    update_thrustdiagram(form, [])
#    xyz0 = array(form.get_vertices_attributes(['x', 'y', 'z'], keys=list(form.vertices())))
#    z0 = xyz0[:, 2][:, newaxis]
#    w0 = C.dot(z0)
#    rmin = sqrt(dot(qt, lh**2) / (dot(qt, w0**2)))
#    z = z0 * rmin
#    l2 = lh**2 + C.dot(z)**2
#    q /= rmin
#    fopt = dot(q.transpose(), l2)
#    i_k = form.index_key()
#    for i in range(len(z0)):
#        form.vertex[i_k[i]]['z'] = float(z[i])
#    f = q * lh.ravel()
#    uv_i = form.uv_index()
#    for u, v, attr in form.edges(True):
#        i = uv_i[(u, v)]
#        attr['q'] = float(q[i])
#        attr['f'] = float(f[i])
#    return fopt, list(q)


# ==============================================================================
# Debugging
# ==============================================================================

if __name__ == "__main__":

    import compas_ags

    from compas_ags.diagrams import FormDiagram

    from compas.plotters import NetworkPlotter

    from compas.viewers import NetworkViewer

    # Form diagram

    form = FormDiagram.from_json(compas_ags.get('fan.json'))

    # Optimise differential evolution

    fopt, qopt = optimise_loadpath3(form, solver='devo', qmax=10, population=20, steps=1000)

    # Optimise genetic algorithm

    # fopt, qopt = optimise_loadpath3(form, solver='ga', qmax=10, population=20, steps=10000)

    # Optimise function and gradient

    fopt, qopt = optimise_loadpath3(form, solver='slsqp', qid0=qopt, qmax=10, steps=300)

    # Plot

    scale = 5
    lines = []
    for u, v in form.edges():
        qi = form.edge[u][v]['q']
        isind = form.edge[u][v]['is_ind']
        if isind:
            colour = 'ff0000'
        elif qi <= 0.1:
            colour = 'eeeeee'
        else:
            colour = 'ffaaaa' if qi > 0 else '0000ff'
        lines.append({
            'start': form.vertex_coordinates(u),
            'end'  : form.vertex_coordinates(v),
            'color': colour,
            'width': scale * (qi + 0.1),
        })

    plotter = NetworkPlotter(form, figsize=(10, 7), fontsize=8)
    plotter.draw_vertices(facecolor={key: '#aaaaaa' for key in form.fixed()}, radius=0.1)
    plotter.draw_lines(lines)
    plotter.show()

    viewer = NetworkViewer(form)
    viewer.setup()
    viewer.show()
