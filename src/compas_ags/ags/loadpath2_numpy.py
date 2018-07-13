
# from __future__ import absolute_import
# from __future__ import division
# from __future__ import print_function

# from numpy import abs
# from numpy import argmin
# from numpy import array
# from numpy import dot
# from numpy import isnan
# from numpy import mean
# from numpy import newaxis
# from numpy import sqrt
# from numpy import vstack
# from numpy import zeros
# from numpy.linalg import pinv

# from scipy.linalg import svd
# from scipy.optimize import fmin_slsqp
# from scipy.sparse import csr_matrix

# from compas_ags.diagrams import FormDiagram

# from compas.geometry import add_vectors
# from compas.geometry import scale_vector
# from compas.geometry import vector_from_points

# from compas.numerical import connectivity_matrix
# from compas.numerical import equilibrium_matrix
# from compas.numerical import nonpivots
# from compas.numerical import normrow

# from compas.utilities import geometric_key

# from multiprocessing import Pool

# from compas_ags.ags.loadpath3_numpy import diff_evo
# from compas_ags.ags.loadpath3_numpy import slsqp

# import sympy


# __author__    = ['Andrew Liew <liew@arch.ethz.ch>']
# __copyright__ = 'Copyright 2018, BLOCK Research Group - ETH Zurich'
# __license__   = 'MIT License'
# __email__     = 'liew@arch.ethz.ch'


# __all__ = [
#     'ground_form',
#     'optimise_single',
# ]


# def ground_form(points):

#     """ Makes a ground structure FormDiagram from a set of points.

#     Parameters
#     ----------
#     points : list
#         Co-ordinates of each point to connect.

#     Returns
#     -------
#     obj
#         Connected edges in a FormDiagram object.

#     """

#     form = FormDiagram()

#     gkey_key = {}
#     for x, y, z in points:
#         key = form.add_vertex(x=x, y=y, z=z)
#         gkey_key[geometric_key([x, y, z])] = key

#     for i in form.vertices():
#         for j in form.vertices():
#             if (i != j) and (not form.has_edge(u=i, v=j, directed=False)):
#                 sp = form.vertex_coordinates(i)
#                 ep = form.vertex_coordinates(j)
#                 vec = vector_from_points(sp, ep)
#                 unique = True
#                 for c in range(2, 10):
#                     for d in range(1, c):
#                         sc = d / c
#                         div = add_vectors(sp, scale_vector(vec, sc))
#                         if gkey_key.get(geometric_key(div), None):
#                             unique = False
#                             break
#                     if not unique:
#                         break
#                 if unique:
#                     form.add_edge(u=i, v=j)

#     return form




#     # Mapping

#     k_i  = form.key_index()
#     i_uv = form.index_uv()
#     uv_i = form.uv_index()

#     # Vertices and edges

#     n     = form.number_of_vertices()
#     m     = form.number_of_edges()
#     fixed = [k_i[key] for key in form.fixed()]
#     edges = [(k_i[u], k_i[v]) for u, v in form.edges()]
#     free  = list(set(range(n)) - set(fixed))

#     # Co-ordinates and loads



#     # C and E matrices

#     C   = connectivity_matrix(edges, 'csr')
#     Ci  = C[:, free]
#     Cit = Ci.transpose()
#     E   = equilibrium_matrix(C, xy, free, 'csr').toarray()
#     uvw = C.dot(xyz)
#     U   = uvw[:, 0]
#     V   = uvw[:, 1]

#     # Independent and dependent branches

#     ind = nonpivots(sympy.Matrix(E).rref()[0].tolist())
#     k   = len(ind)
#     dep = list(set(range(m)) - set(ind))

#     for u, v in form.edges():
#         form.edge[u][v]['is_ind'] = True if uv_i[(u, v)] in ind else False

#     if printout:
#         _, s, _ = svd(E)
#         print('\n')
#         print('Form diagram has {0} independent branches (RREF)'.format(len(ind)))
#         print('Form diagram has {0} independent branches (SVD)'.format(m - len(s)))

#     # Set-up

#     lh2    = normrow(C.dot(xy))**2
#     Edinv  = -csr_matrix(pinv(E[:, dep]))
#     q      = array(form.q())[:, newaxis]
#     Ei     = E[:, ind]
#     p      = vstack([px[free], py[free]])
#     bounds = [[qmin, qmax]] * k
#     args   = (q, ind, dep, Edinv, Ei, p, lh2, Cit, U, V, px, py, free, True)

#     # Solve

#     if solver == 'devo':
#         fopt, qopt = diff_evo(fint, form, bounds, population, generations, printout, plot, frange, args)

#     # if polish == 'slsqp':
#     #     fopt_, qopt_ = slsqp(fint_, form, qopt, bounds, False, printout, None, qequal, args)
#     #     q_ = 1 * q
#     #     q_[ind, 0] = qopt_
#     #     q_[dep] = -Edinv.dot(p - Ei.dot(q_[ind]))
#     #     if fopt_ < fopt:
#     #         fopt, qopt, q = fopt_, qopt_, q_

#     q[ind, 0] = qopt
#     q[dep] = -Edinv.dot(p - Ei.dot(q[ind]))

#     R = residual(q, px, py, free, Cit, U, V)
#     if R < 0.001:
#         checked = True
#     else:
#         checked = False

#     if printout:
#         print('\n' + '-' * 50)
#         print('qid: {0:.3f} : {1:.3f}'.format(min(qopt), max(qopt)))
#         print('q: {0:.3f} : {1:.3f}'.format(float(min(q)), float(max(q))))
#         print('Horizontal equillibrium: {0}'.format(checked))
#         print('-' * 50 + '\n')

#     # Unique key

#     gkeys = []
#     for i in ind:
#         u, v = i_uv[i]
#         gkeys.append(geometric_key(form.edge_midpoint(u, v)[:2] + [0]))
#     form.attributes['indset'] = '-'.join(sorted(gkeys))

#     # Update FormDiagram

#     form.attributes['loadpath'] = fopt

#     for c, qi in enumerate(list(q.ravel())):
#         u, v = i_uv[c]
#         form.edge[u][v]['q'] = qi

#     return fopt, qopt


# def qequal(qid, *args):

#     q, ind, dep, Edinv, Ei, p, lh2, Cit, U, V, px, py, free, _ = args
#     q[ind, 0] = qid
#     q[dep] = -Edinv.dot(p - Ei.dot(q[ind]))

#     R = residual(q, px, py, free, Cit, U, V)
#     return [R]





# def fint(qid, *args):

#     q, ind, dep, Edinv, Ei, p, lh2, Cit, U, V, px, py, free, _ = args
#     q[ind, 0] = qid
#     q[dep] = -Edinv.dot(p - Ei.dot(q[ind]))

#     R = residual(q, px, py, free, Cit, U, V)
#     # f = dot(abs(q.transpose()), lh2)
#     # if R > 0.001:
#     #     f += (5 + R)**4

#     # if isnan(f):
#     #     return 10**10
#     return R


# def fint_(qid, *args):

#     q, ind, dep, Edinv, Ei, p, lh2, Cit, U, V, px, py, free, _ = args
#     q[ind, 0] = qid
#     q[dep] = -Edinv.dot(p - Ei.dot(q[ind]))

#     f = dot(abs(q.transpose()), lh2)

#     if isnan(f):
#         return 10**10
#     return f



# # ==============================================================================
# # Main
# # ==============================================================================

# if __name__ == "__main__":

#     from compas_ags.ags import plot_form
#     from compas_ags.ags import randomise_form

#     m = 4
#     n = 4
#     points = [[i, j, 0] for i in range(m) for j in range(n)]

#     form = ground_form(points)
#     form = randomise_form(form)

#     pins = list(form.vertices_where(conditions={'x': 0}))
#     load = list(form.vertices_where(conditions={'x': m - 1, 'y': n - 1}))
#     form.set_vertices_attributes(pins, is_fixed=True)
#     form.set_vertices_attributes(load, py=-1)

#     # fopt, qopt = optimise_single(form, qmin=-5, qmax=5, population=300, generations=500, printout=10)

#     fopts, forms, best = optimise_multi(form, trials=4, save_figs='/home/al/temp/figs/')
#     form = forms[best]

#     # plot_form(form, max_width=10, radius=0.05, simple=False).show()
