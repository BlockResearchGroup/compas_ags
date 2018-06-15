
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from numpy import array
from numpy import argmin
from numpy import dot
from numpy import newaxis
from numpy import vstack
from numpy import zeros
from numpy.linalg import pinv

from scipy.sparse import csr_matrix
from scipy.optimize import fmin_slsqp

from compas_ags.diagrams import FormDiagram

from compas.geometry import add_vectors
from compas.geometry import scale_vector
from compas.geometry import vector_from_points

from compas.numerical import connectivity_matrix
from compas.numerical import devo_numpy
from compas.numerical import equilibrium_matrix
from compas.numerical import nonpivots
from compas.numerical import normrow

from compas.utilities import geometric_key

from multiprocessing import Pool

import sympy


__author__    = ['Andrew Liew <liew@arch.ethz.ch>']
__copyright__ = 'Copyright 2018, BLOCK Research Group - ETH Zurich'
__license__   = 'MIT License'
__email__     = 'liew@arch.ethz.ch'


__all__ = [
]


def ground_form(points):

    """ Makes a ground structure FormDiagram from a set of points.

    Parameters
    ----------
    points : list
        Co-ordinates of each point to connect.

    Returns
    -------
    obj
        Connected edges in a FormDiagram object.

    """

    form = FormDiagram()

    gkey_key = {}
    for x, y, z in points:
        key = form.add_vertex(x=x, y=y, z=z)
        gkey_key[geometric_key([x, y, z])] = key

    for i in form.vertices():
        for j in form.vertices():
            if (i != j) and (not form.has_edge(u=i, v=j, directed=False)):
                sp = form.vertex_coordinates(i)
                ep = form.vertex_coordinates(j)
                vec = vector_from_points(sp, ep)
                unique = True
                for c in range(2, 10):
                    for d in range(1, c):
                        sc = d / c
                        div = add_vectors(sp, scale_vector(vec, sc))
                        if gkey_key.get(geometric_key(div), None):
                            unique = False
                            break
                    if not unique:
                        break
                if unique:
                    form.add_edge(u=i, v=j)

    return form


def optimise_single(form, solver='devo', polish='slsqp', qmin=1e-6, qmax=10, population=300,
                    generations=500, printout=10, plot=False, frange=None):

    """ Finds the optimised load-path for a FormDiagram.

    Parameters
    ----------
    form : obj
        The FormDiagram.
    solver : str
        'devo' evolutionary solver.
    polish : str
        'slsqp' polish or None.
    qmin : float
        Minimum qid value.
    qmax : float
        Maximum qid value.
    population : int
        Number of agents for evolution solver.
    generations : int
        Number of iteration steps for the evolution solver.
    printout : int
        Frequency of print output to screen.
    plot : bool
        Plot progress of evolution.
    frange : list
        Minimum and maximum f value to plot.

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
    i_uv = form.index_uv()
    uv_i = form.uv_index()

    # Vertices and edges

    n     = form.number_of_vertices()
    m     = form.number_of_edges()
    fixed = [k_i[key] for key in form.fixed()]
    free  = list(set(range(n)) - set(fixed))
    edges = [(k_i[u], k_i[v]) for u, v in form.edges()]
    # sym   = [uv_i[uv] for uv in form.edges_where({'is_symmetry': True})]

    # Co-ordinates and loads

    px  = zeros((n, 1))
    py  = zeros((n, 1))
    xyz = zeros((n, 3))
    for key, vertex in form.vertex.items():
        i = k_i[key]
        xyz[i, :] = form.vertex_coordinates(key)
        px[i] = vertex.get('px', 0)
        py[i] = vertex.get('py', 0)
    xy = xyz[:, :2]

    # Matrices

    C = connectivity_matrix(edges, 'csr')
    E = equilibrium_matrix(C, xy, free, 'csr').toarray()
    q = array(form.q())[:, newaxis]

    # Independent and dependent branches

    ind = nonpivots(sympy.Matrix(E).rref()[0].tolist())
    k   = len(ind)
    dep = list(set(range(m)) - set(ind))

    for u, v in form.edges():
        form.edge[u][v]['is_ind'] = True if uv_i[(u, v)] in ind else False

    if printout:
        print('Form diagram has {0} independent branches'.format(k))
    print(m, k)


    # Set-up

    Edinv = -csr_matrix(pinv(E[:, dep]))
    Ei = E[:, ind]
    p = vstack([px[free], py[free]])
    lh2 = normrow(C.dot(xy))**2
    args = (q, ind, dep, Edinv, Ei, p, lh2)

    # Solve

    bounds = [[qmin, qmax]] * k

    if solver == 'devo':
        fopt, qopt = diff_evo(form, bounds, population, generations, printout, plot, frange, args)

    if polish == 'slsqp':
        fopt, qopt = slsqp(form, qopt, bounds, printout, args)

    q[ind, 0] = qopt
    q[dep] = -Edinv.dot(p - Ei.dot(q[ind]))

    if printout:
        print('\n' + '-' * 50)
        print('fopt: {0:.3f}'.format(fopt))
        print('qid: {0:.3f} : {1:.3f}'.format(min(qopt), max(qopt)))
        print('q: {0:.3f} : {1:.3f}'.format(float(min(q)), float(max(q))))
        print('-' * 50 + '\n')

    # Update FormDiagram

    form.attributes['loadpath'] = fopt

    for c, qi in enumerate(list(q.ravel())):
        u, v = i_uv[c]
        form.edge[u][v]['q'] = qi

    return fopt, qopt


def fint(qid, *args):
    q, ind, dep, Edinv, Ei, p, lh2 = args
    q[ind, 0] = qid
    q[dep] = -Edinv.dot(p - Ei.dot(q[ind]))
    f = dot(abs(q).transpose(), lh2)
    return f


def diff_evo(form, bounds, population, generations, printout, plot, frange, args):
    return devo_numpy(fn=fint, bounds=bounds, population=population, generations=generations, printout=printout,
                      plot=plot, frange=frange, args=args)


def slsqp(form, qid0, bounds, printout, args):
    pout = 2 if printout else 0
    opt = fmin_slsqp(fint, qid0, args=args, disp=pout, bounds=bounds, full_output=1, iter=300)
    return opt[1], opt[0]


def _worker(data):
    i, form, save_figs = data
    fopt, qopt = optimise_single(form, solver='devo', polish='slsqp', qmin=-5, qmax=5, population=300,
                                 generations=500, printout=0)
    print('Trial: {0} - Optimum: {1:.1f}'.format(i, fopt))

    if save_figs:
        plotter = plot_form(form, radius=0, fix_width=True)
        plotter.save('{0}trial_{1}-fopt_{2:.6f}.png'.format(save_figs, i, fopt))
        del plotter

    return (fopt, form)


def optimise_multi(form, trials=10, save_figs=''):
    data = [(i, randomise_form(form), save_figs) for i in range(trials)]
    result = Pool().map(_worker, data)
    fopts, forms = zip(*result)
    best = argmin(fopts)
    fopt = fopts[best]
    print('Best: {0} - fopt {1:.1f}'.format(best, fopt))

    return fopts, forms, best


# ==============================================================================
# Debugging
# ==============================================================================

if __name__ == "__main__":

    # from compas_ags.ags import plot_form

    # form = FormDiagram()
    # form.add_vertex(key=0, x=0, y=1, z=0, is_fixed=True)
    # form.add_vertex(key=1, x=1, y=1, z=0, is_fixed=False, py=-1)
    # form.add_vertex(key=2, x=0, y=0, z=0, is_fixed=True)
    # form.add_vertex(key=3, x=1, y=0, z=0, is_fixed=False)
    # form.add_edge(u=0, v=1)
    # form.add_edge(u=1, v=3)
    # form.add_edge(u=2, v=3)
    # form.add_edge(u=1, v=2)
    # form.add_edge(u=0, v=3)

    # fopt, qopt = optimise_single(form, solver='devo', polish='slsqp', qmin=-5, qmax=5, population=100,
    #                              generations=500, plot=True, frange=[None, None], printout=10)

    # plot_form(form).show()

    # ==============================================================================

    from compas_ags.ags import plot_form
    from compas_ags.ags import randomise_form

    m = 10
    n = 2
    points = [[i, j, 0] for i in range(m) for j in range(n)]

    form = ground_form(points)
    form = randomise_form(form)
    left = list(form.vertices_where(conditions={'x': 0}))
    top = list(form.vertices_where(conditions={'x': m - 1, 'y': n - 1}))
    form.set_vertices_attributes(left, is_fixed=True)
    form.set_vertices_attributes(top, py=-1)

    # fopt, qopt = optimise_single(form, solver='devo', polish='slsqp', qmin=-5, qmax=5, population=100,
    #                              generations=500, plot=0, frange=[None, None], printout=10)

    fopts, forms, best = optimise_multi(form, trials=36, save_figs='/home/al/temp/figs/')
    # form = forms[best]

    # plot_form(form, max_width=20, simple=True, radius=0.05).show()
