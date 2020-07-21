from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

# from ast import literal_eval

# import compas

# from compas.files import OBJ

# from compas.utilities import pairwise
# from compas.utilities import window

# from compas.geometry import normalize_vector
# from compas.geometry import centroid_points
# from compas.geometry import centroid_polygon
# from compas.geometry import cross_vectors
# from compas.geometry import length_vector
# from compas.geometry import subtract_vectors
# from compas.geometry import normal_polygon
# from compas.geometry import area_polygon

from compas.datastructures import Mesh


__all__ = ['Diagram']


class Diagram(Mesh):
    """Basic mesh-based data structure for diagrams in AGS.
    """

    def __init__(self):
        super(Diagram, self).__init__()
        self.dual = None

    # --------------------------------------------------------------------------
    # additional accessors
    # --------------------------------------------------------------------------

    def indexed_face_vertices(self):
        k_i = self.key_index()
        return [[k_i[key] for key in self.face_vertices(fkey)] for fkey in self.faces()]

    # --------------------------------------------------------------------------
    # vertex topology
    # --------------------------------------------------------------------------

    # --------------------------------------------------------------------------
    # edge topology
    # --------------------------------------------------------------------------

    # def edge_faces(self, u, v):
    #     return [self.halfedge[u][v], self.halfedge[v][u]]

    # def is_edge_naked(self, u, v):
    #     return self.halfedge[u][v] is None or self.halfedge[v][u] is None

    # --------------------------------------------------------------------------
    # face topology
    # --------------------------------------------------------------------------

    # def face_adjacency(self):
    #     # this function does not actually use any of the topological information
    #     # provided by the halfedges
    #     # it is used for unifying face cycles
    #     # so the premise is that halfedge data is not valid/reliable
    #     from scipy.spatial import cKDTree

    #     fkey_index = {fkey: index for index, fkey in self.faces_enum()}
    #     index_fkey = dict(self.faces_enum())
    #     points = [self.face_centroid(fkey) for fkey in self.faces()]

    #     tree = cKDTree(points)

    #     _, closest = tree.query(points, k=10, n_jobs=-1)

    #     adjacency = {}
    #     for fkey in self.face:
    #         nbrs  = []
    #         index = fkey_index[fkey]
    #         nnbrs = closest[index]
    #         found = set()
    #         for u, v in iter(self.face[fkey].items()):
    #             for index in nnbrs:
    #                 nbr = index_fkey[index]
    #                 if nbr == fkey:
    #                     continue
    #                 if nbr in found:
    #                     continue
    #                 if v in self.face[nbr] and u == self.face[nbr][v]:
    #                     nbrs.append(nbr)
    #                     found.add(nbr)
    #                     break
    #                 if u in self.face[nbr] and v == self.face[nbr][u]:
    #                     nbrs.append(nbr)
    #                     found.add(nbr)
    #                     break
    #         adjacency[fkey] = nbrs
    #     return adjacency

    # # def face_tree(self, root, algo=network_bfs):
    # #     return algo(self.face_adjacency(), root)

    # def face_adjacency_edge(self, f1, f2):
    #     for u, v in self.face_halfedges(f1):
    #         if self.halfedge[v][u] == f2:
    #             if v in self.edge[u]:
    #                 return u, v
    #             return v, u

    # --------------------------------------------------------------------------
    # vertex geometry
    # --------------------------------------------------------------------------

    # --------------------------------------------------------------------------
    # face geometry
    # --------------------------------------------------------------------------

    # --------------------------------------------------------------------------
    # boundary
    # --------------------------------------------------------------------------

    # def vertices_on_boundary(self, ordered=False):
    #     """Return the vertices on the boundary.

    #     Warning
    #     -------
    #     If the vertices are requested in order, and the mesh has multiple borders,
    #     currently only the vertices of one of the borders will be returned.

    #     Parameters
    #     ----------
    #     ordered : bool, optional
    #         If ``True``, Return the vertices in the same order as they are found on the boundary.
    #         Default is ``False``.

    #     Returns
    #     -------
    #     list
    #         The vertices of the boundary.

    #     Examples
    #     --------
    #     >>>

    #     """
    #     vertices = set()
    #     for key, nbrs in iter(self.halfedge.items()):
    #         for nbr, face in iter(nbrs.items()):
    #             if face is None:
    #                 vertices.add(key)
    #                 vertices.add(nbr)

    #     vertices = list(vertices)

    #     if not ordered:
    #         return vertices

    #     key = vertices[0]
    #     vertices = []
    #     start = key

    #     while 1:
    #         for nbr, fkey in iter(self.halfedge[key].items()):
    #             if fkey is None:
    #                 vertices.append(nbr)
    #                 key = nbr
    #                 break

    #         if key == start:
    #             break

    #     return vertices

    # def faces_on_boundary(self):
    #     """Return the faces on the boundary."""
    #     boundary = []
    #     for fkey in self.faces():
    #         vertices = self.face_vertices(fkey)
    #         for u, v in pairwise(vertices + vertices[0:1]):
    #             if not self.has_edge(u, v, directed=False):
    #                 boundary.append(fkey)
    #                 break
    #     return boundary

    # def edges_on_boundary(self):
    #     edges = []
    #     for fkey in self.faces_on_boundary():
    #         vertices = self.face_vertices(fkey)
    #         for u, v in pairwise(vertices + vertices[0:1]):
    #             if self.has_edge(u, v):
    #                 edges.append((u, v))
    #             elif self.has_edge(v, u):
    #                 edges.append((v, u))
    #     return edges


# ==============================================================================
# Main
# ==============================================================================

if __name__ == '__main__':
    pass
