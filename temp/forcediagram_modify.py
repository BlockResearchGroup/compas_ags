'''compas.algorithms.ags_forcediagram_modify: 

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
from numpy import array, divide, zeros

from scipy.linalg import cho_factor, cho_solve

sys.path.append(os.getenv('PYLIB'))
from compas.toolbox.vector import dot, acute_angles
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
        config = in_dict.get('config', {})
        #-----------------------------------------------------------------------
        vertex              = in_dict['vertex']
        edge                = in_dict['edge']
        face                = in_dict['face']
        halfedge            = in_dict['halfedge']
        reciprocal_vertex   = in_dict['reciprocal.vertex']
        reciprocal_edge     = in_dict['reciprocal.edge']
        reciprocal_halfedge = in_dict['reciprocal.halfedge']
        #-----------------------------------------------------------------------
        graph = DiGraph(vertex, edge, halfedge, face)
        dual = DiGraph(reciprocal_vertex, reciprocal_edge, reciprocal_halfedge)
        #-----------------------------------------------------------------------
        key_to_index  = graph.key_to_index
        index_to_key  = graph.index_to_key
        leaves        = graph.get_leaves()
        fixed         = [key_to_index[key] for key, attr in graph.node.iteritems() if attr['is_fixed'] or key in leaves]
        free          = [key_to_index[key] for key, attr in graph.node.iteritems() if not attr['is_fixed']]
        constraints   = dict((key, (attr['cx'], attr['cy'])) for key, attr in graph.iternodes(True))
        edges         = graph.get_uv(key_to_index)
        edge_to_index = graph.uv_to_index
        m             = graph.m
        n             = graph.n
        #-----------------------------------------------------------------------
        halfedge_to_index = {}
        for (u, v), index in edge_to_index.iteritems():
            halfedge_to_index[(u, v)] = index
            halfedge_to_index[(v, u)] = index
        exterior_edges = [(u, v) for u, v in graph.iteredges() if u in leaves or v in leaves]
        #-----------------------------------------------------------------------
        xyz  = graph.get_node_data('xyz', key_to_index)
        xyz  = array(xyz, dtype=float64).reshape((-1, 1), order='F')
        xyz0 = xyz.copy()
        C    = connectivity_matrix(edges, 'csr')
        q    = graph.get_edge_data('q', edge_to_index)
        q    = array(q, dtype=float64).reshape((-1, 1))
        #-----------------------------------------------------------------------
        dual_key_to_index = dual.key_to_index
        dual_index_to_key = dual.index_to_key
        dual_fixed        = [dual_key_to_index[key] for key, attr in dual.node.iteritems() if graph.face[attr['primal']]['is_exterior']]
        dual_free         = list(set(range(dual.n)) - set(dual_fixed))
        dual_edges        = dual.get_uv(dual_key_to_index)
        dual_order        = [edge_to_index[tuple(attr['primal'])] for u, v, attr in dual.iteredges(True)]
        dual_order        = [(i, j) for i, j in enumerate(dual_order)]
        dual_order        = [i for i, j in sorted(dual_order, key=lambda ij: ij[1])]
        #-----------------------------------------------------------------------
        xyzd = dual.get_node_data('xyz', dual_key_to_index)
        xyzd = array(xyzd, dtype=float64).reshape((-1, 1), order='F')
        Cd   = connectivity_matrix(dual_edges, 'csr')
        Cd   = Cd[dual_order,:]
        uvwd = Cd.dot(xyzd.reshape((-1, 3), order='F'))
        ld   = normrow(uvwd)
        #-----------------------------------------------------------------------
        #-----------------------------------------------------------------------
        #-----------------------------------------------------------------------
        keys     = graph.node.keys()
        shape_0  = sum([len(graph.halfedge[key]) for key in keys if key_to_index[key] in free])
        shape_0 += sum([2 for key in keys if key_to_index[key] in fixed])
        shape_0 += 2 * len(constraints)
        shape_1  = 2 * n
        #-----------------------------------------------------------------------
        line_of_action = {}
        for leaf in leaves:
            nbrs = graph.halfedge[leaf].keys()
            node = nbrs[0]
            p2   = [graph.node[leaf][_] for _ in 'xyz']
            p1   = [graph.node[node][_] for _ in 'xyz']
            a    = p2[1] - p1[1]
            b    = p2[0] - p1[0]
            c    = p2[1] * p1[0] - p2[0] * p1[1]
            line_of_action[(node, leaf)] = a, b, c
        #-----------------------------------------------------------------------
        A = zeros((shape_0, shape_1))
        row = 0
        for index in free:
            key = index_to_key[index]
            nbrs = graph.halfedge[key]
            for nbr in nbrs:
                edge_index = halfedge_to_index[(key, nbr)]
                A[row, index]     = +uvwd[edge_index, 1]
                A[row, index + n] = -uvwd[edge_index, 0]
                row += 1
        for index in fixed:
            A[row,     index]     = 1
            A[row + 1, index + n] = 1
            row += 2
        for key in constraints:
            cx, cy = constraints[key]
            index  = key_to_index[key]
            A[row,     index]     = 1 if cx == 1.0 else 0
            A[row + 1, index + n] = 1 if cy == 1.0 else 0
            row += 2
        At         = A.transpose()
        AtA        = At.dot(A)
        AtA_factor = cho_factor(AtA)
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
                x2 = xyz[nbr_index,     0]
                y2 = xyz[nbr_index + n, 0]
                b[row, 0] = y2 * (x2 - dx) - x2 * (y2 - dy)
                row += 1
        for index in fixed:
            b[row,     0] = xyz[index,     0]
            b[row + 1, 0] = xyz[index + n, 0]
            row += 2
        for key in constraints:
            cx, cy = constraints[key]
            index  = key_to_index[key]
            b[row,     0] = xyz[index, 0]     if cx == 1.0 else 0
            b[row + 1, 0] = xyz[index + n, 0] if cy == 1.0 else 0
            row += 2
        #-----------------------------------------------------------------------
        free_x = free
        free_y = [index + n for index in free_x]
        for k in range(500):
            row = 0
            for index in free:
                key  = index_to_key[index]
                nbrs = graph.halfedge[key]
                for nbr in nbrs:
                    nbr_index  = key_to_index[nbr]
                    edge_index = halfedge_to_index[(key, nbr)]
                    dx = uvwd[edge_index, 0]
                    dy = uvwd[edge_index, 1]
                    x2 = xyz[nbr_index,     0]
                    y2 = xyz[nbr_index + n, 0]
                    b[row, 0] = y2 * (x2 - dx) - x2 * (y2 - dy)
                    row += 1
            xy = cho_solve(AtA_factor, At.dot(b))
            xyz[free_x] = xy[free_x]
            xyz[free_y] = xy[free_y]
            # re-impose the constraints
            for key in constraints:
                cx, cy = constraints[key]
                index  = key_to_index[key]
                if cx == 1.0:
                    xyz[index, 0] = xyz0[index, 0]
                if cy == 1.0:
                    xyz[index + n, 0] = xyz0[index + n, 0]
        #-----------------------------------------------------------------------
        for key in leaves:
            index             = key_to_index[key]
            nbrs              = graph.halfedge[key].keys()
            nbr               = nbrs[0]
            nbr_index         = key_to_index[nbr]
            dy, dx, _         = line_of_action[(nbr, key)]
            xyz[index, 0]     = xyz[nbr_index, 0] + dx
            xyz[index + n, 0] = xyz[nbr_index + n, 0] + dy
        #-----------------------------------------------------------------------
        uvw   = C.dot(xyz.reshape((-1, 3), order='F'))
        signs = [-1 if dot(uvwd[i], uvw[i]) < 0 else +1 for i in xrange(m)]
        #-----------------------------------------------------------------------
        vectors    = [(signs[i] * uvwd[i], uvw[i]) for i in xrange(m)]
        angles     = acute_angles(vectors)
        angles_max = max(angles)
        imax       = angles.index(angles_max)
        if angles_max > 1e-6:
            pass
#             print angles_max
#             print imax
#             print vectors[imax]
#             print angles
#             R = zeros((n, 3))
#             for k in range(100):
#                 for index in free:
#                     key           = index_to_key[index]
#                     dual_face_key = graph.node[key]['dual']
#                     nbrs = list(graph.halfedge[key])
#                     p1   = xyz[key_to_index[key]]
#                     p1_  = xyz[key_to_index[key]]
#                     for nbr in nbrs:
#                         if nbr in graph.edge[key]:
#                             u, v = key, nbr
#                             dual_v, dual_u = graph.edge[u][v]['dual']
#                         else:
#                             u, v = nbr, key
#                             dual_u, dual_v = graph.edge[u][v]['dual']
#                         p0   = xyz[key_to_index[nbr]]
#                         p2   = xyzd[dual_key_to_index[dual_u]]
#                         p3   = xyzd[dual_key_to_index[dual_v]]
#                         vec0 = p1 - p0
#                         if key in leaves or nbr in leaves:
#                             l = 1
#                         else:
#                             l = length(vec0)
#                         if l < 1e-3:
#                             continue
#                         vec1 = p3 - p2
#                         if length(vec1) < 1e-3:
#                             continue
#                         vec0_ = array(unit(vec1))
#                         vec0_ = l * vec0_
#                         if dot(vec0, vec0_) < 0:
#                             vec0_ = -1.0 * vec0_
#                         p1_ = 0.5 * (p0 + vec0_ + p1_)
#                     R[index] = p1_ - p1
#                 xyz[free] = xyz[free] + R[free]
        #-----------------------------------------------------------------------
        uvw = C.dot(xyz.reshape((-1, 3), order='F'))
        l   = normrow(uvw)
        q   = divide(ld, l)
        s   = array([-1 if dot(uvwd[i], uvw[i]) < 0 else +1 for i in xrange(m)]).reshape((-1, 1))
        q   = s * q
        f   = q * l
        #-----------------------------------------------------------------------
        #-----------------------------------------------------------------------
        #-----------------------------------------------------------------------
        for key, attr in graph.node.iteritems():
            index = key_to_index[key]
            attr['x'] = xyz[index, 0]
            attr['y'] = xyz[index + n, 0]
        for u, v, attr in graph.iteredges(True):
            index = edge_to_index[(u, v)]
            attr['q'] = q[index, 0]
            attr['f'] = f[index, 0]
            attr['l'] = l[index, 0]
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
        out_dict['profile']        = stream.getvalue()
        out_dict['data']['vertex'] = graph.node
        out_dict['data']['edge']   = graph.edge
    except:
        out_dict['data']       = None
        out_dict['error']      = traceback.format_exc()
        out_dict['iterations'] = None
        out_dict['profile']    = None
    
    with open(out_path, 'wb+') as f:
        json.dump(out_dict, f)
