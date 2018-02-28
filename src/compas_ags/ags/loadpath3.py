
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from numpy import abs
from numpy import argmin
from numpy import array
from numpy import dot
from numpy import isnan
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
from scipy.sparse import csr_matrix
from scipy.sparse.linalg import spsolve

from compas_ags.diagrams import FormDiagram

from compas.numerical import connectivity_matrix
from compas.numerical import devo_numpy
from compas.numerical import equilibrium_matrix
from compas.numerical import ga
from compas.numerical import normrow
from compas.numerical import nonpivots

from compas.utilities import geometric_key

from multiprocessing import Pool
from random import shuffle

import sympy


__author__    = ['Andrew Liew <liew@arch.ethz.ch>']
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


def optimise_loadpath3(form, solver='devo', polish='slsqp', gradient=False, qmin=1e-6, qmax=10, population=20,
                       steps=100, printout=True):

    """ Finds the optimised loadpath for a FormDiagram with given loads.

    Parameters
    ----------
    form : obj
        The FormDiagram.
    solver : str
        'devo' or 'ga' solver to use.
    polish : bool
        'slsqp' polish or None.
    gradient : bool
        Use analytical gradient (True) or approximation (False).
    qmin : float
        Minimum qid value.
    qmax : float
        Maximum qid value.
    population : int
        Number of agents for evolution solver.
    steps : int
        Number of iteration steps for evolution solver.
    printout : bool
        Print output to screen.

    Returns
    -------
    float
        Optimum load-path value.
    list
        Optimum qids

    """

    if printout:
        print('\n' + '-' * 50)
        print('Load-path optimisation started')

    # Mapping

    k_i = form.key_index()
    i_k = form.index_key()
    i_uv = form.index_uv()
    uv_i = form.uv_index()

    # Vertices and edges

    n = form.number_of_vertices()
    m = form.number_of_edges()
    fixed = [k_i[key] for key in form.vertices_where({'is_fixed': True})]
    free  = list(set(range(n)) - set(fixed))
    edges = [(k_i[u], k_i[v]) for u, v in form.edges()]

    # Co-ordinates and loads

    xyz = zeros((n, 3))
    pz  = zeros(n)
    for key, vertex in form.vertex.items():
        i = k_i[key]
        xyz[i, :] = form.vertex_coordinates(key)
        pz[i] = vertex.get('pz', 0)
    xy = xyz[:, :2]
    z  = xyz[:, 2]
    pz = pz[free]

    # C and E matrices

    C = connectivity_matrix(edges, 'csr')
    Ci  = C[:, free]
    Cf  = C[:, fixed]
    Cit = Ci.transpose()
    E   = equilibrium_matrix(C, xy, free, 'csr').toarray()

    # Independent and dependent branches

    ind = nonpivots(sympy.Matrix(E).rref()[0].tolist())
    dep = list(set(range(m)) - set(ind))
    for u, v in form.edges():
        if uv_i[(u, v)] in ind:
            form.edge[u][v]['is_ind'] = True
        else:
            form.edge[u][v]['is_ind'] = False
    k = len(ind)
    if printout:
        print('Form diagram has {0} independent branches'.format(len(ind)))

    Adinv = pinv(E[:, dep])
    Aid = E[:, ind]
    _AdinvAid = dot(-Adinv, Aid)
    _AdinvAid = csr_matrix(_AdinvAid)

    # Set-up

    lh = normrow(C.dot(xy))
    lh2 = lh**2
    q = ones((m, 1))
    bounds = [[qmin, qmax]] * k
    args = (q, ind, dep, _AdinvAid, C, Ci, Cit, pz, z, free, lh2)

    if solver == 'devo':
        fopt, qopt = diff_evo(form, bounds, population, steps, printout, args)

    elif solver == 'ga':
        fopt, qopt = diff_ga(form, bounds, population, steps, args)

    if polish == 'slsqp':
        fopt_, qopt_ = slsqp(form, qopt, bounds, gradient, printout, args)

    if fopt_ < fopt:
        fopt = fopt_
        qopt = qopt_

    # Update FormDiagram

    form.attributes['loadpath'] = fopt

    q[ind, 0] = qopt
    q[dep] = _AdinvAid.dot(q[ind])
    Q = diags(q[:, 0])
    z[free] = spsolve(Cit.dot(Q).dot(Ci), pz)

    for i in range(n):
        form.vertex[i_k[i]]['z'] = z[i]

    for c, qi in enumerate(list(q.ravel())):
        u, v = i_uv[c]
        form.edge[u][v]['q'] = qi

    # Print summary

    if printout:
        print('fopt: {0:.3g}'.format(fopt))
        print('All branches compressive: {0}'.format(all(q.ravel() >= 0)))
        print('Maximum qid: {0:.3g}'.format(max(qopt)))
        print('-' * 50 + '\n')

    return fopt, qopt


def z_from_form(form):

    # Mapping

    i_k = form.index_key()
    k_i = form.key_index()

    # Vertices and edges

    n = form.number_of_vertices()
    fixed = [k_i[key] for key in form.vertices_where({'is_fixed': True})]
    free  = list(set(range(n)) - set(fixed))
    edges = [(k_i[u], k_i[v]) for u, v in form.edges()]

    # Connectivity and equillibrium matrices

    C = connectivity_matrix(edges, 'csr')
    Ci  = C[:, free]
    Cit = Ci.transpose()

    # Co-ordinates and loads

    pz = zeros(n)
    xyz = zeros((n, 3))
    for key, vertex in form.vertex.items():
        i = k_i[key]
        xyz[i, :] = form.vertex_coordinates(key)
        pz[i] = vertex.get('pz')
    z = xyz[:, 2]
    pzfree = pz[free]
    q = array(form.q())

    # Update z

    Q = diags(q)
    z[free] = spsolve(Cit.dot(Q).dot(Ci), pzfree)
    for i in range(n):
        form.vertex[i_k[i]]['z'] = z[i]

    return form


def fint(qid, *args):

    """ Calculates the internal loadpath for a given qid set (with penalty).

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

    q, ind, dep, _AdinvAid, C, Ci, Cit, pz, z, free, lh2 = args
    q[ind, 0] = qid
    q[dep] = _AdinvAid.dot(q[ind])
    Q = diags(q[:, 0])
    z[free] = spsolve(Cit.dot(Q).dot(Ci), pz)
    l2 = lh2 + C.dot(z[:, newaxis])**2
    f = dot(abs(q.transpose()), l2)
    f_ = f + sum((q[q < 0] - 1.)**2)

    if isnan(f_):
        return 10**20
    return f_


def fint_(qid, *args):

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

    q, ind, dep, _AdinvAid, C, Ci, Cit, pz, z, free, lh2 = args
    q[ind, 0] = qid
    q[dep] = _AdinvAid.dot(q[ind])
    Q = diags(q[:, 0])
    z[free] = spsolve(Cit.dot(Q).dot(Ci), pz)
    l2 = lh2 + C.dot(z[:, newaxis])**2
    f = dot(abs(q.transpose()), l2)

    return f


def qpos(qid, *args):

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

    q, ind, dep, _AdinvAid, C, Ci, Cit, pz, z, free, lh2 = args
    q[ind, 0] = qid
    q[dep] = _AdinvAid.dot(q[ind])

    return q.ravel() - 10.**(-3)


def slsqp(form, qid0, bounds, gradient, printout, args):

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
    printout : bool
        Print output to screen.
    args : tuple
        Sequence of additional arguments.

    Returns
    -------
    float
        Optimum load-path value.
    array
        Optimum qids

    """

    q, ind, dep, _AdinvAid, C, Ci, Cit, pz, z, free, lh2 = args
    pout = 2 if printout else 0

    if not gradient:
        opt = fmin_slsqp(fint_, qid0, args=args, disp=pout, bounds=bounds, full_output=1, iter=300, f_ieqcons=qpos)

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


def diff_evo(form, bounds, population, steps, printout, args):

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
    printout : bool
        Print output to screen.
    args : tuple
        Sequence of additional arguments.

    Returns
    -------
    float
        Optimum load-path value.
    array
        Optimum qids

    """

    return devo_numpy(fn=fint, bounds=bounds, population=population, generations=steps, printout=printout, args=args)


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

    k = len(bounds)
    nbins  = [10] * k
    elites = int(0.2 * population)

    ga_ = ga(fint, 'min', k, bounds, num_gen=steps, num_pop=population, num_elite=elites,
             num_bin_dig=nbins, mutation_probability=0.03, fargs=args, print_refresh=10)

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


def randomise_form(form):

    edges = [(form.vertex_coordinates(i), form.vertex_coordinates(j)) for i, j in form.edges()]
    shuffle(edges)
    form_ = FormDiagram.from_lines(edges)
    gkey_key = form_.gkey_key()
    for key, vertex in form.vertex.items():
        gkey = geometric_key(form.vertex_coordinates(key))
        form_.vertex[gkey_key[gkey]] = vertex

    return form_


def worker(sequence):

    i, form = sequence
    fopt, qopt = optimise_loadpath3(form, solver='devo', polish='slsqp', qmax=7, population=50, steps=100000, printout=0)
    print('Trial: {0} - Optimum: {1:.1f}'.format(i, fopt))

    return (fopt, form)


def optimise_multi(form, trials=10):

    unique_keys = []
    forms = []
    for i in range(trials):
        print('Combination: {0}'.format(i))
        form_ = randomise_form(form)
        key = unique_key(form_)
        if key not in unique_keys:
            unique_keys.append(key)
            forms.append(form_)
    trials = len(forms)
    print('Trials: {0}'.format(trials))

    pool = Pool()
    sequence = zip(list(range(trials)), forms)
    result = pool.map(worker, sequence)
    fopts = [i for i, _ in result]
    best = argmin(fopts)
    fopt = fopts[best]
    form = result[best][1]
    form.attributes['loadpath'] = fopt
    print('Best: {0} - fopt {1:.1f}'.format(best, fopt))

    return form


def unique_key(form):

    k_i = form.key_index()
    i_uv = form.index_uv()

    n = form.number_of_vertices()
    fixed = [k_i[key] for key in form.vertices_where({'is_fixed': True})]
    free  = list(set(range(n)) - set(fixed))
    edges = [(k_i[u], k_i[v]) for u, v in form.edges()]

    xyz = zeros((n, 3))
    for key, vertex in form.vertex.items():
        i = k_i[key]
        xyz[i, :] = form.vertex_coordinates(key)
    xy = xyz[:, :2]

    C = connectivity_matrix(edges, 'csr')
    E   = equilibrium_matrix(C, xy, free, 'csr').toarray()
    ind = nonpivots(sympy.Matrix(E).rref()[0].tolist())

    gkeys = []
    for i in ind:
        u, v = i_uv[i]
        gkey = geometric_key(form.edge_midpoint(u, v))
        gkeys.append(gkey)

    unique_key = '-'.join(sorted(gkeys))

    return unique_key


# ==============================================================================
# Debugging
# ==============================================================================

if __name__ == "__main__":

    # fnm = '/al/compas_ags/data/loadpath/fan.json'
    fnm = '/cluster/home/liewa/compas_ags/data/loadpath/fan.json'
    form = FormDiagram.from_json(fnm)

    # fopt, qopt = optimise_loadpath3(form, solver='devo', polish='slsqp', qmax=5, population=20, steps=100)
    form = optimise_multi(form, trials=250)

    form.to_json(fnm)

    # from compas.plotters import NetworkPlotter

    # lines = []
    # qmax = max(form.q())
    # for u, v in form.edges():
    #     qi = form.edge[u][v].get('q', 1)
    #     if form.edge[u][v]['is_ind']:
    #         colour = 'ff0000'
    #     elif qi <= 0.001:
    #         colour = 'eeeeee'
    #     else:
    #         colour = 'ff8784' if qi > 0 else '0000ff'
    #     lines.append({
    #         'start': form.vertex_coordinates(u),
    #         'end'  : form.vertex_coordinates(v),
    #         'color': colour,
    #         'width': (qi / qmax + 0.2) * 10,
    #     })

    # plotter = NetworkPlotter(form, figsize=(10, 7), fontsize=8)
    # plotter.draw_vertices(facecolor={key: '#aaaaaa' for key in form.fixed()}, radius=0.1)
    # plotter.draw_lines(lines)
    # plotter.show()

    # from compas.viewers import NetworkViewer

    # viewer = NetworkViewer(form)
    # viewer.setup()
    # viewer.show()
