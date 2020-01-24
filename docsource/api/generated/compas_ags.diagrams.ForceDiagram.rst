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
      ~ForceDiagram.add_face
      ~ForceDiagram.add_vertex
      ~ForceDiagram.anchor
      ~ForceDiagram.area
      ~ForceDiagram.bounding_box
      ~ForceDiagram.bounding_box_xy
      ~ForceDiagram.centroid
      ~ForceDiagram.clear
      ~ForceDiagram.collapse_edge
      ~ForceDiagram.compute_constraints
      ~ForceDiagram.connected_components
      ~ForceDiagram.copy
      ~ForceDiagram.cull_vertices
      ~ForceDiagram.delete_face
      ~ForceDiagram.delete_vertex
      ~ForceDiagram.dual
      ~ForceDiagram.edge_attribute
      ~ForceDiagram.edge_attributes
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
      ~ForceDiagram.edges_attribute
      ~ForceDiagram.edges_attributes
      ~ForceDiagram.edges_on_boundary
      ~ForceDiagram.edges_where
      ~ForceDiagram.edges_where_predicate
      ~ForceDiagram.euler
      ~ForceDiagram.external_edges
      ~ForceDiagram.external_vertices
      ~ForceDiagram.face_adjacency
      ~ForceDiagram.face_adjacency_halfedge
      ~ForceDiagram.face_adjacency_vertices
      ~ForceDiagram.face_area
      ~ForceDiagram.face_aspect_ratio
      ~ForceDiagram.face_attribute
      ~ForceDiagram.face_attributes
      ~ForceDiagram.face_center
      ~ForceDiagram.face_centroid
      ~ForceDiagram.face_coordinates
      ~ForceDiagram.face_corners
      ~ForceDiagram.face_curvature
      ~ForceDiagram.face_degree
      ~ForceDiagram.face_flatness
      ~ForceDiagram.face_halfedges
      ~ForceDiagram.face_label_name
      ~ForceDiagram.face_max_degree
      ~ForceDiagram.face_min_degree
      ~ForceDiagram.face_name
      ~ForceDiagram.face_neighborhood
      ~ForceDiagram.face_neighbors
      ~ForceDiagram.face_normal
      ~ForceDiagram.face_skewness
      ~ForceDiagram.face_vertex_ancestor
      ~ForceDiagram.face_vertex_descendant
      ~ForceDiagram.face_vertices
      ~ForceDiagram.faces
      ~ForceDiagram.faces_attribute
      ~ForceDiagram.faces_attributes
      ~ForceDiagram.faces_on_boundary
      ~ForceDiagram.faces_where
      ~ForceDiagram.faces_where_predicate
      ~ForceDiagram.fixed
      ~ForceDiagram.flip_cycles
      ~ForceDiagram.from_data
      ~ForceDiagram.from_formdiagram
      ~ForceDiagram.from_json
      ~ForceDiagram.from_lines
      ~ForceDiagram.from_obj
      ~ForceDiagram.from_off
      ~ForceDiagram.from_pickle
      ~ForceDiagram.from_ply
      ~ForceDiagram.from_points
      ~ForceDiagram.from_polygons
      ~ForceDiagram.from_polyhedron
      ~ForceDiagram.from_polylines
      ~ForceDiagram.from_shape
      ~ForceDiagram.from_stl
      ~ForceDiagram.from_vertices_and_faces
      ~ForceDiagram.genus
      ~ForceDiagram.get_any_edge
      ~ForceDiagram.get_any_face
      ~ForceDiagram.get_any_face_vertex
      ~ForceDiagram.get_any_vertex
      ~ForceDiagram.get_any_vertices
      ~ForceDiagram.gkey_key
      ~ForceDiagram.halfedge_face
      ~ForceDiagram.index_key
      ~ForceDiagram.index_uv
      ~ForceDiagram.indexed_face_vertices
      ~ForceDiagram.insert_vertex
      ~ForceDiagram.is_connected
      ~ForceDiagram.is_edge_on_boundary
      ~ForceDiagram.is_empty
      ~ForceDiagram.is_face_on_boundary
      ~ForceDiagram.is_halfedge
      ~ForceDiagram.is_manifold
      ~ForceDiagram.is_orientable
      ~ForceDiagram.is_quadmesh
      ~ForceDiagram.is_regular
      ~ForceDiagram.is_trimesh
      ~ForceDiagram.is_valid
      ~ForceDiagram.is_vertex_connected
      ~ForceDiagram.is_vertex_on_boundary
      ~ForceDiagram.key_gkey
      ~ForceDiagram.key_index
      ~ForceDiagram.normal
      ~ForceDiagram.number_of_edges
      ~ForceDiagram.number_of_faces
      ~ForceDiagram.number_of_vertices
      ~ForceDiagram.ordered_edges
      ~ForceDiagram.set_anchor
      ~ForceDiagram.set_fixed
      ~ForceDiagram.smooth_area
      ~ForceDiagram.smooth_centroid
      ~ForceDiagram.split_edge
      ~ForceDiagram.summary
      ~ForceDiagram.to_data
      ~ForceDiagram.to_json
      ~ForceDiagram.to_lines
      ~ForceDiagram.to_obj
      ~ForceDiagram.to_off
      ~ForceDiagram.to_pickle
      ~ForceDiagram.to_ply
      ~ForceDiagram.to_points
      ~ForceDiagram.to_polygons
      ~ForceDiagram.to_polylines
      ~ForceDiagram.to_quadmesh
      ~ForceDiagram.to_stl
      ~ForceDiagram.to_trimesh
      ~ForceDiagram.to_vertices_and_faces
      ~ForceDiagram.transform
      ~ForceDiagram.transformed
      ~ForceDiagram.unify_cycles
      ~ForceDiagram.unset_edge_attribute
      ~ForceDiagram.unset_face_attribute
      ~ForceDiagram.unset_vertex_attribute
      ~ForceDiagram.update
      ~ForceDiagram.update_default_edge_attributes
      ~ForceDiagram.update_default_face_attributes
      ~ForceDiagram.update_default_vertex_attributes
      ~ForceDiagram.uv_index
      ~ForceDiagram.vertex_area
      ~ForceDiagram.vertex_attribute
      ~ForceDiagram.vertex_attributes
      ~ForceDiagram.vertex_coordinates
      ~ForceDiagram.vertex_curvature
      ~ForceDiagram.vertex_degree
      ~ForceDiagram.vertex_faces
      ~ForceDiagram.vertex_label_name
      ~ForceDiagram.vertex_laplacian
      ~ForceDiagram.vertex_max_degree
      ~ForceDiagram.vertex_min_degree
      ~ForceDiagram.vertex_name
      ~ForceDiagram.vertex_neighborhood
      ~ForceDiagram.vertex_neighborhood_centroid
      ~ForceDiagram.vertex_neighbors
      ~ForceDiagram.vertex_normal
      ~ForceDiagram.vertices
      ~ForceDiagram.vertices_attribute
      ~ForceDiagram.vertices_attributes
      ~ForceDiagram.vertices_on_boundaries
      ~ForceDiagram.vertices_on_boundary
      ~ForceDiagram.vertices_where
      ~ForceDiagram.vertices_where_predicate
      ~ForceDiagram.xy
   
   

   
   
   .. rubric:: Attributes

   .. autosummary::
   
      ~ForceDiagram.adjacency
      ~ForceDiagram.data
      ~ForceDiagram.name
   
   