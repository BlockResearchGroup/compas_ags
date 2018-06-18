
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from numpy import abs
from numpy import argmin
from numpy import array
from numpy import dot
from numpy import isnan
from numpy import matmul as mm
from numpy import newaxis
from numpy import ones
from numpy import sum
from numpy import sqrt
from numpy import tile
from numpy import zeros

from numpy.linalg import pinv

from scipy.linalg import svd
from scipy.optimize import fmin_slsqp
from scipy.sparse import diags
from scipy.sparse import csr_matrix
from scipy.sparse.linalg import spsolve

from compas_ags.diagrams import FormDiagram
from compas_ags.diagrams import ForceDiagram

from compas.plotters import NetworkPlotter

from compas.numerical import connectivity_matrix
from compas.numerical import devo_numpy
from compas.numerical import equilibrium_matrix
from compas.numerical import ga
from compas.numerical import normrow
from compas.numerical import nonpivots

from compas.utilities import geometric_key

from multiprocessing import Pool

from random import shuffle

import compas_ags
import sympy
import os


__author__    = ['Andrew Liew <liew@arch.ethz.ch>']
__copyright__ = 'Copyright 2018, BLOCK Research Group - ETH Zurich'
__license__   = 'MIT License'
__email__     = 'liew@arch.ethz.ch'


__all__ = [
    # 'compute_loadpath3',
    'optimise_single',
    'optimise_multi',
    'plot_form',
    'randomise_form',
]


# def compute_loadpath3(form, force):
#     k_i   = form.key_index()
#     xyz   = array(form.get_vertices_attributes('xyz'), dtype=float64)
#     edges = [(k_i[u], k_i[v]) for u, v in form.edges()]
#     C     = connectivity_matrix(edges, 'csr')
#     q     = array(form.q(), dtype=float64).reshape((-1, 1))

#     # leaves   = set(form.leaves())
#     # internal = [i for i, u, v in enumerate(form.edges()) if u not in leaves and v not in leaves]

#     l  = normrow(C.dot(xyz))
#     f  = q * l
#     # li = l[internal]
#     # fi = f[internal]
#     # return li.T.dot(fi)[0, 0]

#     return l.T.dot(f)[0, 0]


def optimise_single(form, solver='devo', polish='slsqp', gradient=False, qmin=1e-6, qmax=5, population=300,
                    generations=500, printout=10, plot=False, frange=None, indset=None, tension=False):

    """ Finds the optimised load-path for a FormDiagram.

    Parameters
    ----------
    form : obj
        The FormDiagram.
    solver : str
        Differential Evolution 'devo' or Genetic Algorithm 'ga' evolutionary solver to use.
    polish : str
        'slsqp' polish or None.
    gradient : bool
        Use analytical gradient (True) or approximation (False).
    qmin : float
        Minimum qid value.
    qmax : float
        Maximum qid value.
    population : int
        Number of agents for evolution solver.
    generations : int
        Number of generations for the evolution solver.
    printout : int
        Frequency of print output to the terminal.
    plot : bool
        Plot progress of the evolution.
    frange : list
        Minimum and maximum function value to plot.
    indset : str
        Key of the independent set to use.
    tension : bool
        Allow tension edge force densities (experimental).

    Notes
    -----
    - SLSQP polish does not yet respect lower and upper bound constraints.

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

    k_i  = form.key_index()
    i_k  = form.index_key()
    i_uv = form.index_uv()
    uv_i = form.uv_index()

    # Vertices and edges

    n     = form.number_of_vertices()
    m     = form.number_of_edges()
    fixed = [k_i[key] for key in form.fixed()]
    edges = [(k_i[u], k_i[v]) for u, v in form.edges()]
    sym   = [uv_i[uv] for uv in form.edges_where({'is_symmetry': True})]
    rol   = [k_i[key] for key in form.vertices_where({'is_roller': True})]
    free  = list(set(range(n)) - set(fixed) - set(rol))

    # Constraints

    lb_ind = []
    ub_ind = []
    lb = []
    ub = []
    for key, vertex in form.vertex.items():
        if vertex.get('lb', None):
            lb_ind.append(k_i[key])
            lb.append(vertex['lb'])
        if vertex.get('ub', None):
            ub_ind.append(k_i[key])
            ub.append(vertex['ub'])
    lb = array(lb)
    ub = array(ub)

    # Co-ordinates and loads

    xyz = zeros((n, 3))
    pz  = zeros(n)
    for key, vertex in form.vertex.items():
        i = k_i[key]
        xyz[i, :] = form.vertex_coordinates(key)
        pz[i] = vertex.get('pz', 0)
    xy = xyz[:, :2]
    z  = zeros(n)
    pz = pz[free]

    # C and E matrices

    C   = connectivity_matrix(edges, 'csr')
    Ci  = C[:, free]
    Cit = Ci.transpose()
    E   = equilibrium_matrix(C, xy, free, 'csr').toarray()
    uvw = C.dot(xyz)
    U   = uvw[:, 0]
    V   = uvw[:, 1]

    # Independent and dependent branches

    if indset:
        ind = []
        inds = indset.split('-')
        for u, v in form.edges():
            if geometric_key(form.edge_midpoint(u, v)[:2] + [0]) in inds:
                ind.append(uv_i[(u, v)])
    else:
        ind = nonpivots(sympy.Matrix(E).rref()[0].tolist())
    k   = len(ind)
    dep = list(set(range(m)) - set(ind))

    for u, v in form.edges():
        form.edge[u][v]['is_ind'] = True if uv_i[(u, v)] in ind else False

    if printout:
        _, s, _ = svd(E)
        print('Form diagram has {0} independent branches (RREF)'.format(len(ind)))
        print('Form diagram has {0} independent branches (SVD)'.format(m - len(s)))

    # Set-up

    EdinvEi = csr_matrix(dot(-pinv(E[:, dep]), E[:, ind]))
    lh2 = normrow(C.dot(xy))**2
    q = array(form.q())[:, newaxis]
    bounds = [[qmin, qmax]] * k
    args = (q, ind, dep, EdinvEi, C, Ci, Cit, pz, z, free, lh2, sym, U, V, lb, ub, lb_ind, ub_ind, tension)

    # Solve

    if solver == 'devo':
        fopt, qopt = diff_evo(form, bounds, population, generations, printout, plot, frange, args)

    elif solver == 'ga':
        fopt, qopt = diff_ga(form, bounds, population, generations, args)

    q = zlq_from_qid(qopt, args)[2]

    if polish == 'slsqp':
        fopt_, qopt_ = slsqp(form, qopt, bounds, gradient, printout, args)
        q_ = zlq_from_qid(qopt_, args)[2]
        if fopt_ < fopt:
            if (min(q_) > -0.001 and not tension) or tension:
                fopt, qopt, q = fopt_, qopt_, q_

    z, _, q, checked = zlq_from_qid(qopt, args)

    if printout:
        print('\n' + '-' * 50)
        print('qid: {0:.3f} : {1:.3f}'.format(min(qopt), max(qopt)))
        print('q: {0:.3f} : {1:.3f}'.format(float(min(q)), float(max(q))))
        print('Horizontal equillibrium: {0}'.format(checked))
        print('-' * 50 + '\n')

    # Unique key

    gkeys = []
    for i in ind:
        u, v = i_uv[i]
        gkeys.append(geometric_key(form.edge_midpoint(u, v)[:2] + [0]))
    form.attributes['indset'] = '-'.join(sorted(gkeys))

    # Update FormDiagram

    form.attributes['loadpath'] = fopt

    for i in range(n):
        form.vertex[i_k[i]]['z'] = z[i]

    for c, qi in enumerate(list(q.ravel())):
        u, v = i_uv[c]
        form.edge[u][v]['q'] = qi

    return fopt, qopt


def zlq_from_qid(qid, args):

    """ Calculates the new z co-ordinates, lengths and force densities from a qid set.

    Parameters
    ----------
    qid : list
        Independent force densities.
    args : tuple
        Sequence of additional arguments.

    Returns
    -------
    array
        Updated z.
    array
        Updated squared edge lengths.
    array
        Updated force densities.
    bool
        Check for horizontal equillibrium.

    """

    q, ind, dep, EdinvEi, C, Ci, Cit, pz, z, free, lh2, sym, U, V = args[:-5]
    q[ind, 0] = qid
    q[dep] = EdinvEi.dot(q[ind])

    Rx = Cit.dot(U * q.ravel())
    Ry = Cit.dot(V * q.ravel())
    R  = max(sqrt(Rx**2 + Ry**2))
    if R < 0.001:
        checked = True
    else:
        checked = False

    q[sym] *= 0

    z[free] = spsolve(Cit.dot(diags(q[:, 0])).dot(Ci), pz)
    l2 = lh2 + C.dot(z[:, newaxis])**2

    return z, l2, q, checked


def fint(qid, *args):

    """ Calculates the internal load-path for a given qid set (with penalties).

    Parameters
    ----------
    qid : list
        Independent force densities.
    args : tuple
        Sequence of additional arguments.

    Returns
    -------
    float
        Scalar load-path value.

    """

    lb, ub, lb_ind, ub_ind, tension = args[-5:]

    z, l2, q, checked = zlq_from_qid(qid, args)
    f = dot(abs(q.transpose()), l2)

    if isnan(f) or not checked:
        return 10**10

    else:
        if not tension:
            f += sum((q[q < 0] - 5)**4)

        if lb_ind:
            z_lb    = z[lb_ind]
            log_lb  = z_lb < lb
            diff_lb = z_lb[log_lb] - lb[log_lb]
            pen_lb  = sum(abs(diff_lb) + 5)**4
            f += pen_lb

        if ub_ind:
            z_ub    = z[ub_ind]
            log_ub  = z_ub > ub
            diff_ub = z_ub[log_ub] - ub[log_ub]
            pen_ub  = sum(abs(diff_ub) + 5)**4
            f += pen_ub

        return f


def fint_(qid, *args):

    """ Calculates the internal load-path for a given qid set (without penalties).

    Parameters
    ----------
    qid : list
        Independent force densities.
    args : tuple
        Sequence of additional arguments.

    Returns
    -------
    float
        Scalar load-path value.

    """

    z, l2, q, checked = zlq_from_qid(qid, args)
    f = dot(abs(q.transpose()), l2)

    if isnan(f) or not checked:
        return 10**10
    return f


def qpos(qid, *args):

    """ Function for non-negativity constraint of force densities q.

    Parameters
    ----------
    qid : list
        Independent force densities.
    args : tuple
        Sequence of additional arguments.

    Returns
    -------
    array
        q values to be >= 0.

    """

    q, ind, dep, EdinvEi, C, Ci, Cit, pz, z, free, lh2, sym, U, V = args[:-5]
    q[ind, 0] = qid
    q[dep] = EdinvEi.dot(q[ind])
    q[sym] *= 0
    return q.ravel() - 10**(-5)


def slsqp(form, qid0, bounds, gradient, printout, args):

    """ Finds the optimised load-path for a FormDiagram by SLSQP.

    Parameters
    ----------
    form : obj
        FormDiagram.
    qid0 : obj
        Initial starting point.
    bounds : list
        [qmin, qmax] values for each qid.
    gradient : bool
        Use analytical gradient (True) or approximation (False).
    printout : bool
        Print output to terminal.
    args : tuple
        Sequence of additional arguments for fn.

    Returns
    -------
    float
        Optimum load-path value.
    array
        Optimum qids

    """

    pout = 2 if printout else 0
    ieq = None if args[-1] else qpos

    if not gradient:
        opt = fmin_slsqp(fint_, qid0, args=args, disp=pout, bounds=bounds, full_output=1, iter=300, f_ieqcons=ieq)

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

    return opt[1], opt[0]


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


def diff_evo(form, bounds, population, generations, printout, plot, frange, args):

    """ Finds the optimised load-path for a FormDiagram by Differential Evolution.

    Parameters
    ----------
    form : obj
        FormDiagram.
    bounds : list
        [qmin, qmax] values for each qid.
    population : int
        Number of agents for evolution solver.
    generations : int
        Number of generations for the evolution solver.
    printout : int
        Frequency of print output to the terminal.
    plot : bool
        Plot progress of the evolution.
    frange : list
        Minimum and maximum function value to plot.
    args : tuple
        Sequence of additional arguments for fn.

    Returns
    -------
    float
        Optimum load-path value.
    array
        Optimum qids

    """

    return devo_numpy(fn=fint, bounds=bounds, population=population, generations=generations, printout=printout,
                      plot=plot, frange=frange, args=args)


def diff_ga(form, bounds, population, generations, args):

    """ Finds the optimised load-path for a FormDiagram by Genetic Algorithm.

    Parameters
    ----------
    form : obj
        FormDiagram.
    bounds : list
        [qmin, qmax] values for each qid.
    population : int
        Number of agents for evolution solver.
    generations : int
        Number of generations for the evolution solver.
    args : tuple
        Sequence of additional arguments for fn.

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

    ga_ = ga(fint, 'min', k, bounds, num_gen=generations, num_pop=population, num_elite=elites, num_bin_dig=nbins,
             mutation_probability=0.03, fargs=args, print_refresh=10)

    index = ga_.best_individual_index
    qopt  = ga_.current_pop['scaled'][index]
    fopt  = ga_.current_pop['fit_value'][index]

    return fopt, qopt


def randomise_form(form):

    """ Randomises the FormDiagram by shuffling the edges.

    Parameters
    ----------
    form : obj
        Original FormDiagram.

    Returns
    -------
    obj
        New shuffled FormDiagram.

    """

    edges = [form.edge_coordinates(u, v) for u, v in form.edges()]
    shuffle(edges)
    form_ = FormDiagram.from_lines(edges)
    form_.update_default_edge_attributes({'is_symmetry': False})
    gkey_key = form_.gkey_key()

    sym = [geometric_key(form.edge_midpoint(u, v)) for u, v in form.edges_where({'is_symmetry': True})]
    for u, v in form_.edges():
        if geometric_key(form_.edge_midpoint(u, v)) in sym:
            form_.edge[u][v]['is_symmetry'] = True

    for key, vertex in form.vertex.items():
        gkey = geometric_key(form.vertex_coordinates(key))
        form_.vertex[gkey_key[gkey]] = vertex

    return form_


def _worker(data):

    try:
        i, form, save_figs, qmin, qmax, population, generations, simple = data
        fopt, qopt = optimise_single(form, qmin=qmin, qmax=qmax, population=population, generations=generations,
                                     printout=0, tension=0)
        print('Trial: {0} - Optimum: {1:.1f}'.format(i, fopt))

        if save_figs:
            plotter = plot_form(form, radius=0, fix_width=True, simple=simple)
            plotter.save('{0}trial_{1}-fopt_{2:.6f}.png'.format(save_figs, i, fopt))
            del plotter
        return (fopt, form)

    except:
        print('Trial: {0} - FAILED'.format(i))
        return (10**10, None)


def optimise_multi(form, trials=10, save_figs='', qmin=0.001, qmax=5, population=300, generations=500, simple=False):

    """ Finds the optimised load-path for multiple randomised FormDiagrams.

    Parameters
    ----------
    form : obj
        Original FormDiagram.
    trials : int
        Number of trials to perform.
    save_figs : str
        Directory to save FormDiagram plots.
    qmin : float
        Minimum qid value.
    qmax : float
        Maximum qid value.
    population : int
        Number of agents for evolution solver.
    generations : int
        Number of generations for the evolution solver.
    simple : bool
        Simple plotting for figures.
    Returns
    -------
    list
        Optimum load-path for each trial.
    list
        Each final FormDiagram.
    int
        Index of the optimum.

    """

    data = [(i, randomise_form(form), save_figs, qmin, qmax, population, generations, simple)
            for i in range(trials)]
    fopts, forms = zip(*Pool().map(_worker, data))
    best = argmin(fopts)
    print('Best: {0} - fopt {1:.1f}'.format(best, fopts[best]))

    return fopts, forms, best


def plot_form(form, radius=0.1, fix_width=False, max_width=10, simple=True):

    """ Extended load-path plotting for a FormDiagram

    Parameters
    ----------
    form : obj
        FormDiagram to plot.
    radius : float
        Radius of vertex markers.
    fix_width : bool
        Fix the width of edges to be constant.
    max_width : float
        Maximum width of the edges.
    simple : bool
        Simple red and blue colour plotting.

    Returns
    -------
    obj
        Plotter object.

    """

    qmax = max(abs(array(form.q())))
    lines = []

    for u, v in form.edges():
        edge = form.edge[u][v]
        qi = edge.get('q', 0)

        if simple:

            if qi > 0:
                colour = ['ff', '00', '00']
            elif qi < 0:
                colour = ['00', '00', 'ff']
            else:
                colour = ['aa', 'aa', 'aa']

        else:

            colour = ['00', '00', '00']
            if qi > 0:  # red if compression
                colour[0] = 'ff'
            if edge.get('is_symmetry'):  # green if symmetry
                colour[1] = 'cc'
            if edge.get('is_ind'):  # blue if independent
                colour[2] = 'ff'

        if fix_width:
            width = max_width
        else:
            width = (qi / qmax) * max_width

        lines.append({
            'start': form.vertex_coordinates(u),
            'end'  : form.vertex_coordinates(v),
            'color': ''.join(colour),
            'width': width,
        })

    plotter = NetworkPlotter(form, figsize=(10, 10))
    if radius:
        plotter.draw_vertices(facecolor={i: '#aaaaaa' for i in form.vertices_where({'is_fixed': True})}, radius=radius)
    plotter.draw_lines(lines)

    return plotter


# ==============================================================================
# Debugging
# ==============================================================================

if __name__ == "__main__":

    # Load FormDiagram

    file = os.path.join(compas_ags.DATA, 'loadpath/arches_flat.json')
    form = FormDiagram.from_json(file)
    form.set_vertices_attributes(form.vertices(), {'lb': 0, 'ub': 20})

    # Single run

    form = randomise_form(form)
    fopt, qopt = optimise_single(form, qmax=5, population=300, generations=500, plot=0, frange=[100, 500], printout=10)

    # Multiple runs

    # fopts, forms, best = optimise_multi(form, trials=30, save_figs='', qmax=5, population=300, generations=200)
    # form = forms[best]

    # Plot

    plot_form(form, radius=0.1, simple=False).show()

    # Save

    # form.to_json(file)
