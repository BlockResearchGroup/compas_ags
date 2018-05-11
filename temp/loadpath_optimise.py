'''compas.algorithms.ags_forcediagram_optimise_loadpath: 

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see http://www.gnu.org/licenses/.
'''

import os
import sys
import json
import cStringIO
import cProfile
import pstats
import traceback

from numpy import float64, seterr
from numpy import array, zeros, divide

from scipy.linalg import cho_solve, cho_factor
from scipy.optimize import minimize

sys.path.append(os.getenv('PYLIB'))
from compas.toolbox.vector import dot
from compas.datastructures.digraph import DiGraph
from compas.toolbox.linalg import connectivity_matrix
from compas.toolbox.linalg import normrow

__author__     = 'Tom Van Mele'
__copyright__  = 'Copyright 2014, BLOCK Research Group - ETH Zurich'
__license__    = 'GNU - General Public License'
__version__    = '0.0.1'
__email__      = 'vanmelet@ethz.ch'
__status__     = 'Development'
__date__       = '27.03.2014'
__contact__    = ['ETH Zurich',
                  'Institute for Technology in Architecture',
                  'BLOCK Research Group',
                  'Stefano-Franscini-Platz 5', 
                  'HIL H 47', 
                  '8093 Zurich', 
                  'Switzerland']


seterr(all='ignore')

################################################################################
################################################################################
################################################################################
################################################################################
################################################################################

if __name__ == '__main__':
    
    out_dict = {
        'data': {},
        'error': None,
        'iterations': None,
        'profile': None,
    }
    
    in_path = sys.argv[1]
    out_path = sys.argv[2]
    
    with open(in_path, 'rb') as f:
        in_dict = json.load(f)

    try:
        profile = cProfile.Profile()
        profile.enable()
        #-----------------------------------------------------------------------
        #-----------------------------------------------------------------------
        #-----------------------------------------------------------------------
        #-----------------------------------------------------------------------
        #-----------------------------------------------------------------------
        #-----------------------------------------------------------------------
        #-----------------------------------------------------------------------
        config      = in_dict.get('config', {})
        params      = config.get('params', [])
        constraints = config.get('constraints', None)
        bounds      = config.get('bounds', None)
        #-----------------------------------------------------------------------
        vertex              = in_dict['vertex']
        edge                = in_dict['edge']
        halfedge            = in_dict['halfedge']
        reciprocal_vertex   = in_dict['reciprocal.vertex']
        reciprocal_edge     = in_dict['reciprocal.edge']
        reciprocal_halfedge = in_dict['reciprocal.halfedge']
        #-----------------------------------------------------------------------
        graph = DiGraph(vertex, edge, halfedge)
        dual  = DiGraph(reciprocal_vertex, reciprocal_edge, reciprocal_halfedge)
        #-----------------------------------------------------------------------
        key_to_index  = graph.key_to_index
        index_to_key  = graph.index_to_key
        leaves        = graph.get_leaves()
        fixed         = [key_to_index[key] for key, attr in graph.node.iteritems() if attr['is_fixed'] or key in leaves]
        free          = [key_to_index[key] for key, attr in graph.node.iteritems() if not attr['is_fixed']]
        cxcy          = dict((key, (attr['cx'], attr['cy'])) for key, attr in graph.iternodes(True))
        edges         = graph.get_uv(key_to_index)
        edge_to_index = graph.uv_to_index
        m             = graph.m
        n             = graph.n
        #-----------------------------------------------------------------------
        halfedge_to_index = {}
        for (u, v), index in edge_to_index.iteritems():
            halfedge_to_index[(u, v)] = index
            halfedge_to_index[(v, u)] = index
        interior_edges = [edge_to_index[(u, v)] for u, v in graph.iteredges() if u not in leaves and v not in leaves]
        #-----------------------------------------------------------------------
        xyz  = graph.get_node_data('xyz', key_to_index)
        xyz  = array(xyz, dtype=float64)
        xyz0 = xyz.copy()
        C    = connectivity_matrix(edges, 'csr')
        q    = graph.get_edge_data('q', edge_to_index)
        q    = array(q, dtype=float64).reshape((-1, 1))
        #-----------------------------------------------------------------------
        dual_n            = dual.n
        dual_key_to_index = dual.key_to_index
        dual_index_to_key = dual.index_to_key
        dual_free         = [dual_key_to_index[key] for key in params]
        dual_fixed        = list(set(range(dual_n)) - set(dual_free))
        dual_edges        = dual.get_uv(dual_key_to_index)
        dual_order        = [edge_to_index[tuple(attr['primal'])] for u, v, attr in dual.iteredges(True)]
        dual_order        = [(i, j) for i, j in enumerate(dual_order)]
        dual_order        = [i for i, j in sorted(dual_order, key=lambda ij: ij[1])]
        #-----------------------------------------------------------------------
        xyzd  = dual.get_node_data('xyz', dual_key_to_index)
        xyzd  = array(xyzd, dtype=float64)
        xyzd0 = xyzd.copy()
        Cd    = connectivity_matrix(dual_edges, 'csr')
        Cd    = Cd[dual_order,:]
        uvwd  = Cd.dot(xyzd)
        ld    = normrow(uvwd) 
        #-----------------------------------------------------------------------
        #-----------------------------------------------------------------------
        #-----------------------------------------------------------------------
        keys     = graph.node.keys()
        shape_0  = sum([len(graph.halfedge[key]) for key in keys if key_to_index[key] in free])
        shape_0 += sum([2 for key in keys if key_to_index[key] in fixed])
        shape_0 += 2 * len(cxcy)
        shape_1  = 2 * n
        #-----------------------------------------------------------------------
        line_of_action = {}
        for leaf in leaves:
            nbrs       = graph.halfedge[leaf].keys()
            node       = nbrs[0]
            index      = key_to_index[leaf]
            node_index = key_to_index[node]
            p2 = [graph.node[leaf][_] for _ in 'xyz']
            p1 = [graph.node[node][_] for _ in 'xyz']
            a  = p2[1] - p1[1]
            b  = p2[0] - p1[0]
            c  = p2[1] * p1[0] - p2[0] * p1[1]
            line_of_action[(node, leaf)] = a, b, c
        #-----------------------------------------------------------------------
        A = zeros((shape_0, shape_1))
        row = 0
        for index in free:
            key = index_to_key[index]
            nbrs = graph.halfedge[key]
            for nbr in nbrs:
                edge_index = halfedge_to_index[(key, nbr)]
                A[row, 2 * index]     = + uvwd[edge_index, 1]
                A[row, 2 * index + 1] = - uvwd[edge_index, 0]
                row += 1
        for index in fixed:
            A[row,     2 * index]     = 1
            A[row + 1, 2 * index + 1] = 1
            row += 2
        for key in cxcy:
            cx, cy = cxcy[key]
            index  = key_to_index[key]
            A[row,     2 * index]     = 1 if cx == 1.0 else 0
            A[row + 1, 2 * index + 1] = 1 if cy == 1.0 else 0
            row += 2
        #-----------------------------------------------------------------------
        b = zeros((shape_0, 1))
        row = 0
        for index in free:
            key  = index_to_key[index]
            nbrs = graph.halfedge[key]
            for nbr in nbrs:
                nbr_index  = key_to_index[nbr]
                edge_index = halfedge_to_index[(key, nbr)]
                dx = uvwd[edge_index, 0]
                dy = uvwd[edge_index, 1]
                x2 = xyz[nbr_index, 0]
                y2 = xyz[nbr_index, 1]
                b[row, 0] = y2 * (x2 - dx) - x2 * (y2 - dy)
                row += 1
        for index in fixed:
            b[row,     0] = xyz[index, 0]
            b[row + 1, 0] = xyz[index, 1]
            row += 2
        for key in cxcy:
            cx, cy = cxcy[key]
            index  = key_to_index[key]
            b[row,     0] = xyz[index, 0] if cx == 1.0 else 0
            b[row + 1, 0] = xyz[index, 1] if cy == 1.0 else 0
            row += 2
        #-----------------------------------------------------------------------
        #-----------------------------------------------------------------------
        #-----------------------------------------------------------------------
        #-----------------------------------------------------------------------
        def objfun(xydi):
            xyzd[dual_free, 0:2] = xydi.reshape((-1, 2), order='C')
            if links:
                for master, slave in links:
                    xyzd[dual_key_to_index[slave], 0] = xyzd[dual_key_to_index[master], 0]
            uvwd = Cd.dot(xyzd)
            ld = normrow(uvwd)
            #-------------------------------------------------------------------
            row = 0
            for index in free:
                key = index_to_key[index]
                nbrs = graph.halfedge[key]
                for nbr in nbrs:
                    edge_index = halfedge_to_index[(key, nbr)]
                    A[row, 2 * index]     = + uvwd[edge_index, 1]
                    A[row, 2 * index + 1] = - uvwd[edge_index, 0]
                    row += 1
            At         = A.transpose()
            AtA        = At.dot(A)
            AtA_factor = cho_factor(AtA)
            for _ in range(100):
                row = 0
                for index in free:
                    key  = index_to_key[index]
                    nbrs = graph.halfedge[key]
                    for nbr in nbrs:
                        nbr_index  = key_to_index[nbr]
                        edge_index = halfedge_to_index[(key, nbr)]
                        dx = uvwd[edge_index, 0]
                        dy = uvwd[edge_index, 1]
                        x2 = xyz[nbr_index, 0]
                        y2 = xyz[nbr_index, 1]
                        b[row, 0] = y2 * (x2 - dx) - x2 * (y2 - dy)
                        row += 1
                xy = cho_solve(AtA_factor, At.dot(b))
                xy = xy.reshape((-1, 2), order='C')
                xyz[free, 0:2] = xy[free]
                for key in cxcy:
                    cx, cy = cxcy[key]
                    index  = key_to_index[key]
                    if cx == 1.0:
                        xyz[index, 0] = xyz0[index, 0]
                    if cy == 1.0:
                        xyz[index, 1] = xyz0[index, 1]
            for key in leaves:
                index         = key_to_index[key]
                nbrs          = graph.halfedge[key].keys()
                nbr           = nbrs[0]
                nbr_index     = key_to_index[nbr]
                dy, dx, _     = line_of_action[(nbr, key)]
                xyz[index, 0] = xyz[nbr_index, 0] + dx
                xyz[index, 1] = xyz[nbr_index, 1] + dy
            #-------------------------------------------------------------------
            uvw  = C.dot(xyz)
            l    = normrow(uvw)
            ldl  = ld * l
            fval = sum(ldl[interior_edges])[0]
            print fval
            return fval
        #-----------------------------------------------------------------------
        #-----------------------------------------------------------------------
        #-----------------------------------------------------------------------
        links  = []
        if constraints:
            for key in constraints:
                for constraint_type, constraint_data in constraints[key]:
                    if 'link' == constraint_type:
                        slave  = key
                        master = constraint_data
                        links.append((master, slave))
        temp = None
        if bounds:
            temp = [0] * (2*len(dual_free))
            for i in xrange(len(dual_free)):
                index = dual_free[i]
                key   = dual_index_to_key[index]
                if key not in bounds:
                    temp[2*i]     = (None, None)
                    temp[2*i + 1] = (None, None)
                else:
                    x_bound, y_bound, z_bound = bounds[key]
                    temp[2*i]     = x_bound
                    temp[2*i + 1] = y_bound
        #-----------------------------------------------------------------------
        method = 'L-BFGS-B'
        x0 = xyzd0[dual_free, 0:2].reshape((-1, 1), order='C')
        res = minimize(objfun, 
                       x0, 
                       method=method, 
                       bounds=temp,
                       tol=1e-12, 
                       options={'maxiter': 500})
        print '------------------------------'
        print 'scipy.optimize.minimize => {0}'.format(method)
        print '------------------------------'
        print 'Solution: {0}'.format(res.x)
        print 'Success: {0}'.format(res.success)
        print 'Cause of termination: {0}'.format(res.message)
        #-----------------------------------------------------------------------
        uvwd  = Cd.dot(xyzd)
        ld    = normrow(uvwd)
        uvw   = C.dot(xyz)
        l     = normrow(uvw)
        q     = divide(ld, l)
        q     = divide(ld, l)
        signs = array([-1 if dot(uvwd[i], uvw[i]) < 0 else +1 for i in xrange(m)]).reshape((-1, 1))
        q     = signs * q
        f     = q * l
        #-----------------------------------------------------------------------
        #-----------------------------------------------------------------------
        #-----------------------------------------------------------------------
        for key, attr in graph.node.iteritems():
            index = key_to_index[key]
            attr['x'] = xyz[index, 0]
            attr['y'] = xyz[index, 1]
        for u, v, attr in graph.iteredges(True):
            index = edge_to_index[(u, v)]
            attr['q'] = q[index, 0]
            attr['f'] = f[index, 0]
            attr['l'] = l[index, 0]
        for key, attr in dual.node.iteritems():
            index = dual_key_to_index[key]
            attr['x'] = xyzd[index, 0]
            attr['y'] = xyzd[index, 1]
        #-----------------------------------------------------------------------
        #-----------------------------------------------------------------------
        #-----------------------------------------------------------------------
        #-----------------------------------------------------------------------
        #-----------------------------------------------------------------------
        #-----------------------------------------------------------------------
        profile.disable()
        stream = cStringIO.StringIO()
        stats = pstats.Stats(profile, stream=stream)
        stats.strip_dirs()
        stats.sort_stats(1)
        stats.print_stats(20)
        out_dict['profile'] = stream.getvalue()
        out_dict['data']['vertex']            = graph.node
        out_dict['data']['edge']              = graph.edge
        out_dict['data']['reciprocal.vertex'] = dual.node
        out_dict['data']['reciprocal.edge']   = dual.edge
    except:
        out_dict['data']       = None
        out_dict['error']      = traceback.format_exc()
        out_dict['iterations'] = None
        out_dict['profile']    = None
    
    with open(out_path, 'wb+') as f:
        json.dump(out_dict, f)
