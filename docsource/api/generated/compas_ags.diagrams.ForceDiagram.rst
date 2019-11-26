.. rst-class:: detail

ForceDiagram
================================

.. currentmodule:: compas_ags.diagrams

.. .. inheritance-diagram:: ForceDiagram

.. autoclass:: ForceDiagram

   
   
   .. rubric:: Methods

   .. autosummary::
      :toctree:

   
      ~ForceDiagram.__init__
      ~ForceDiagram.add_edge
      ~ForceDiagram.add_face
      ~ForceDiagram.add_vertex
      ~ForceDiagram.anchor
      ~ForceDiagram.clear
      ~ForceDiagram.clear_edgedict
      ~ForceDiagram.clear_facedict
      ~ForceDiagram.clear_halfedgedict
      ~ForceDiagram.clear_vertexdict
      ~ForceDiagram.copy
      ~ForceDiagram.delete_edge
      ~ForceDiagram.delete_face
      ~ForceDiagram.delete_vertex
      ~ForceDiagram.dump
      ~ForceDiagram.dumps
      ~ForceDiagram.edge_connected_edges
      ~ForceDiagram.edge_coordinates
      ~ForceDiagram.edge_direction
      ~ForceDiagram.edge_faces
      ~ForceDiagram.edge_label_name
      ~ForceDiagram.edge_length
      ~ForceDiagram.edge_midpoint
      ~ForceDiagram.edge_name
      ~ForceDiagram.edge_point
      ~ForceDiagram.edge_vector
      ~ForceDiagram.edges
      ~ForceDiagram.edges_on_boundary
      ~ForceDiagram.edges_where
      ~ForceDiagram.edges_where_predicate
      ~ForceDiagram.face_adjacency
      ~ForceDiagram.face_adjacency_edge
      ~ForceDiagram.face_area
      ~ForceDiagram.face_center
      ~ForceDiagram.face_centroid
      ~ForceDiagram.face_coordinates
      ~ForceDiagram.face_corners
      ~ForceDiagram.face_edges
      ~ForceDiagram.face_halfedges
      ~ForceDiagram.face_label_name
      ~ForceDiagram.face_name
      ~ForceDiagram.face_neighborhood
      ~ForceDiagram.face_neighbors
      ~ForceDiagram.face_normal
      ~ForceDiagram.face_vertex_ancestor
      ~ForceDiagram.face_vertex_descendant
      ~ForceDiagram.face_vertex_neighbors
      ~ForceDiagram.face_vertices
      ~ForceDiagram.faces
      ~ForceDiagram.faces_on_boundary
      ~ForceDiagram.fixed
      ~ForceDiagram.from_data
      ~ForceDiagram.from_formdiagram
      ~ForceDiagram.from_json
      ~ForceDiagram.from_lines
      ~ForceDiagram.from_obj
      ~ForceDiagram.from_vertices_and_edges
      ~ForceDiagram.from_vertices_and_faces
      ~ForceDiagram.get_any_edge
      ~ForceDiagram.get_any_face
      ~ForceDiagram.get_any_face_vertex
      ~ForceDiagram.get_any_vertex
      ~ForceDiagram.get_any_vertices
      ~ForceDiagram.get_edge_attribute
      ~ForceDiagram.get_edge_attributes
      ~ForceDiagram.get_edges_attribute
      ~ForceDiagram.get_edges_attributes
      ~ForceDiagram.get_face_attribute
      ~ForceDiagram.get_face_attributes
      ~ForceDiagram.get_face_attributes_all
      ~ForceDiagram.get_faces_attribute
      ~ForceDiagram.get_faces_attributes
      ~ForceDiagram.get_faces_attributes_all
      ~ForceDiagram.get_vertex_attribute
      ~ForceDiagram.get_vertex_attributes
      ~ForceDiagram.get_vertices_attribute
      ~ForceDiagram.get_vertices_attributes
      ~ForceDiagram.gkey_key
      ~ForceDiagram.halfedges
      ~ForceDiagram.has_edge
      ~ForceDiagram.has_vertex
      ~ForceDiagram.index_key
      ~ForceDiagram.index_uv
      ~ForceDiagram.indexed_face_vertices
      ~ForceDiagram.is_edge_naked
      ~ForceDiagram.is_vertex_connected
      ~ForceDiagram.is_vertex_leaf
      ~ForceDiagram.key_gkey
      ~ForceDiagram.key_index
      ~ForceDiagram.leaves
      ~ForceDiagram.load
      ~ForceDiagram.loads
      ~ForceDiagram.number_of_edges
      ~ForceDiagram.number_of_faces
      ~ForceDiagram.number_of_vertices
      ~ForceDiagram.ordered_edges
      ~ForceDiagram.plot
      ~ForceDiagram.set_edge_attribute
      ~ForceDiagram.set_edge_attributes
      ~ForceDiagram.set_edges_attribute
      ~ForceDiagram.set_edges_attributes
      ~ForceDiagram.set_face_attribute
      ~ForceDiagram.set_face_attributes
      ~ForceDiagram.set_faces_attribute
      ~ForceDiagram.set_faces_attributes
      ~ForceDiagram.set_fixed
      ~ForceDiagram.set_vertex_attribute
      ~ForceDiagram.set_vertex_attributes
      ~ForceDiagram.set_vertices_attribute
      ~ForceDiagram.set_vertices_attributes
      ~ForceDiagram.split_edge
      ~ForceDiagram.summary
      ~ForceDiagram.to_data
      ~ForceDiagram.to_json
      ~ForceDiagram.to_lines
      ~ForceDiagram.to_obj
      ~ForceDiagram.to_points
      ~ForceDiagram.to_vertices_and_edges
      ~ForceDiagram.update
      ~ForceDiagram.update_default_edge_attributes
      ~ForceDiagram.update_default_face_attributes
      ~ForceDiagram.update_default_vertex_attributes
      ~ForceDiagram.uv_index
      ~ForceDiagram.vertex_area
      ~ForceDiagram.vertex_connected_edges
      ~ForceDiagram.vertex_coordinates
      ~ForceDiagram.vertex_degree
      ~ForceDiagram.vertex_degree_in
      ~ForceDiagram.vertex_degree_out
      ~ForceDiagram.vertex_faces
      ~ForceDiagram.vertex_label_name
      ~ForceDiagram.vertex_laplacian
      ~ForceDiagram.vertex_max_degree
      ~ForceDiagram.vertex_min_degree
      ~ForceDiagram.vertex_name
      ~ForceDiagram.vertex_neighborhood
      ~ForceDiagram.vertex_neighborhood_centroid
      ~ForceDiagram.vertex_neighbors
      ~ForceDiagram.vertex_neighbors_in
      ~ForceDiagram.vertex_neighbors_out
      ~ForceDiagram.vertex_normal
      ~ForceDiagram.vertices
      ~ForceDiagram.vertices_on_boundary
      ~ForceDiagram.vertices_where
      ~ForceDiagram.vertices_where_predicate
      ~ForceDiagram.wireframe
      ~ForceDiagram.xy
   
   

   
   
   .. rubric:: Attributes

   .. autosummary::
   
      ~ForceDiagram.adjacency
      ~ForceDiagram.data
      ~ForceDiagram.name
   
   