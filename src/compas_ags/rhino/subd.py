from __future__ import absolute_import
from __future__ import division
from __future__ import print_function


import compas.geometry as cg
from compas.geometry import cross_vectors
from compas.utilities import pairwise
from compas.datastructures.mesh._mesh import Mesh

__all__ = ['subdivide_force_tri', 
            'get_cycle_direction',
            ]

def mesh_fast_copy(other):
    from copy import deepcopy
    subd = SubdMesh()
    # subd.attributes = deepcopy(other.attributes)
    # subd.default_vertex_attributes = deepcopy(other.default_vertex_attributes)
    # subd.default_face_attributes = deepcopy(other.default_face_attributes)
    # subd.default_edge_attributes = deepcopy(other.default_edge_attributes)
    subd.vertex = deepcopy(other.vertex)
    subd.face = deepcopy(other.face)
    # subd.edgedata = deepcopy(other.edgedata)
    # subd.facedata = deepcopy(other.facedata)
    subd.halfedge = deepcopy(other.halfedge)
    subd._max_int_key = other._max_int_key
    subd._max_int_fkey = other._max_int_fkey
    return subd


class SubdMesh(Mesh):
    
    _add_vertex = Mesh.add_vertex
    _add_face = Mesh.add_face
    _insert_vertex = Mesh.insert_vertex

    def add_vertex(self, x, y, z):
        key = self._max_int_key = self._max_int_key + 1

        if key not in self.vertex:
            self.vertex[key] = {}
            self.halfedge[key] = {}

        self.vertex[key] = dict(x=x, y=y, z=z)

        return key

    def add_face(self, vertices):
        fkey = self._max_int_fkey = self._max_int_fkey + 1

        self.face[fkey] = vertices
        self.facedata[fkey] = {}

        for u, v in pairwise(vertices + vertices[:1]):
            self.halfedge[u][v] = fkey
            if u not in self.halfedge[v]:
                self.halfedge[v][u] = None

        return fkey

    def insert_vertex(self, fkey):
        x, y, z = self.face_center(fkey)
        w = self.add_vertex(x=x, y=y, z=z)
        for u, v in self.face_halfedges(fkey):
            self.add_face([u, v, w])
        del self.face[fkey]
        return w



def subdivide_force_tri(form, force):
    """ 
    Subdivide a ForceDiagram using simple insertion of vertices.
    Support / fixed vertices in the FormDiagram are faces that should not be subdivided in the ForceDiagram

    Parameters
    ----------
    form : compas_ags.diagrams.FormDiagram
    forcd : compas_ags.diagrams.ForcdDiagram
    
    Return
    ------
    fkeys_to_del: list
        The face keys that are deleted.

    """

    # find fkeys that should not be subdivided
    form_fixed_vertices = [vkey for vkey in form.vertices() if form.vertex_attribute(vkey, 'is_fixed') is True]
    # update ForceDiagram face attribute to save the origianl fkey
    force.update_default_face_attributes({'ori_fkey': None})
    
    # copy the origianl ForceDiagram
    cls = type(force)
    subd = mesh_fast_copy(force)

    fkeys_to_del = []
    for fkey in subd.faces():
        force.face_attribute(fkey, 'ori_fkey', fkey) 
        # use duality, fkey of force diagram is vkey of form diagram
        # to subdivide only internal faces
        if fkey not in form_fixed_vertices:
            force.insert_vertex(fkey)

            fkeys_to_del.append(fkey)
    #         x, y, z = subd.face_centroid(fkey)
    #         f_cen_key = force.add_vertex(x=x, y=y, z=z)
    #         for u, v in subd.face_halfedges(fkey):
    #             force.add_face([u, v, f_cen_key], ori_fkey=fkey)
    
    # # delete the original faces
    # for fkey_to_del in fkeys_to_del:
    #     force.delete_face(fkey_to_del)
    
    print(list(force.edges()), 'edges')
    return fkeys_to_del



def get_cycle_direction(form, vkeys):
    # vkeys should be in cycle, for example face_vertices
    # this function is used to check the cycle direction

    assert len(vkeys) >= 3 # make sure there are at least 3 vertices in the face
    p1 = form.vertex_coordinates(vkeys[0])
    p2 = form.vertex_coordinates(vkeys[1])
    p3 = form.vertex_coordinates(vkeys[2])
    
    v1 = [a - b for a, b in zip(p1, p2)]
    v2 = [a - b for a, b in zip(p3, p2)]
    
    return cross_vectors(v1, v2)


# def update_form_from_force_sub_tri(form, force, vkey):
#     """ 
#     update the FormDiagram after subdiving a ForceDiagram using simple insertion of vertices.

#     Parameters
#     ----------
#     form : compas_ags.diagrams.FormDiagram
#     force : compas_ags.diagrams.ForcdDiagram
#     vkey: fkey of the ForceDiagram / vkey of the FormDiagram which is subdivided
    
#     Return
#     ------

#     """

#     # find edges connected to the vertex in FormDiagram
#     neighbor_vertices = form.vertex_neighbors(vkey, ordered=True)
#     # xy coordinate of the vkey in FormDiagram
#     v_xy = form.vertex_coordinates(vkey)
#     new_vkeys = []
    
#     # edge dictionary to store the original edge uv and the new vkey
#     edges_dict = {}
#     for n_vkey in neighbor_vertices: 
#         n_xy = form.vertex_coordinates(n_vkey) # xy coordinate of the neighbour
#         vec = cg.subtract_vectors(n_xy, v_xy) # vector of the edge
#         vec = cg.scale_vector(vec, sca)
#         # target point xy coordinate
#         x, y, z = [a + b for a, b in zip(v_xy, vec)] 
#         # add new vertex
#         tar_vkey = form.add_vertex(x=x, y=y, z=z, is_fixed=False)
#         new_vkeys.append(tar_vkey)
        
#         # store the original uv and new vkey
#         edges_dict[(vkey, n_vkey)] = tar_vkey
#     print(edges_dict)
    
#     # find faces connected to the vertex
#     neighbor_faces = form.vertex_faces(vkey, ordered=True)  # TO CHECK: VERTEX_FACES ARE ALWAYS IN THE CLOCKWISE DIRECTION?
#     vkey_dict[vkey] = {}
#     for n_fkey in neighbor_faces:
#         print(n_fkey, 'neighbour_face_key')
#         vkey_dict[vkey][n_fkey] = []
#         for (u, v) in form.face_halfedges(n_fkey):
#             print(u, v, 'these are uvs')
#             if (u, v) in edges_dict.keys():
#                 print(edges_dict[(u, v)])
#                 vkey_dict[vkey][n_fkey].append(edges_dict[(u, v)])
#             elif (v, u) in edges_dict.keys():
#                 print(edges_dict[(v, u)])
#                 vkey_dict[vkey][n_fkey].append(edges_dict[(v, u)])
#         print(vkey_dict[vkey][n_fkey], 'vkey_dict')
    
#         u1, v1 = form.face_halfedges(n_fkey)[0]
#         u2, v2 = form.face_halfedges(n_fkey)[-1]
#         if (u1, v1) in edges_dict.keys() or (v1, u1) in edges_dict.keys():
#             if (u2, v2) in edges_dict.keys() or (v2, u2) in edges_dict.keys():
#                 print(vkey_dict[vkey][n_fkey], 'SWITCH')
#                 vkey_dict[vkey][n_fkey] = vkey_dict[vkey][n_fkey][::-1]
#                 print(vkey_dict[vkey][n_fkey], 'SWITCH')
        
# #     print(vkey, new_vkeys, 'these are the new keys')
#     form.add_face(new_vkeys[::-1]) 

# # face_dict stores fkey whose face_vertices are modified and its new face vertices
# face_dict = {}
# for fkey in form.faces():
#     f_vkeys = form.face_vertices(fkey)
#     count = 0
#     for i, vkey in enumerate(form.face_vertices(fkey)):
#         if vkey in vkey_dict.keys():
#             print(f_vkeys)
#             f_vkeys.pop(i)
#             print(f_vkeys)
#             f_vkeys.insert(i, vkey_dict[vkey][fkey][0])
#             print(f_vkeys)
#             f_vkeys.insert(i + 1, vkey_dict[vkey][fkey][1])
#             count += 1
#     if count != 0:
#         face_dict[fkey] = f_vkeys
        
# # delete the old faces and add new faces    
# for fkey in face_dict.keys():
#     form.face[fkey] = face_dict[fkey]


# new_nodes = []
# count = 0
# vkey_index = {}
# for i in range(form.number_of_vertices()):
#     vkey = form.key_index()[i]
#     if vkey not in force_del_fkeys:
#         vkey_index[vkey] = i - count
#         new_nodes.append(form.vertex_coordinates(vkey))
#     else:
#         count += 1

# new_faces = [form.face_vertices(fkey) for fkey in form.faces()]
# for i, f in enumerate(new_faces):
#     new_faces[i] = [vkey_index[v] for v in f]