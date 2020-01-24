.. rst-class:: detail

FormDiagram
===============================

.. currentmodule:: compas_ags.diagrams

.. .. inheritance-diagram:: FormDiagram

.. autoclass:: FormDiagram

   
   
   .. rubric:: Methods

   .. autosummary::
      :toctree:

   
      ~FormDiagram.__init__
      ~FormDiagram.add_face
      ~FormDiagram.add_vertex
      ~FormDiagram.area
      ~FormDiagram.bounding_box
      ~FormDiagram.bounding_box_xy
      ~FormDiagram.breakpoints
      ~FormDiagram.centroid
      ~FormDiagram.clear
      ~FormDiagram.collapse_edge
      ~FormDiagram.connected_components
      ~FormDiagram.constrained
      ~FormDiagram.constraints
      ~FormDiagram.copy
      ~FormDiagram.cull_vertices
      ~FormDiagram.delete_face
      ~FormDiagram.delete_vertex
      ~FormDiagram.dual
      ~FormDiagram.edge_attribute
      ~FormDiagram.edge_attributes
      ~FormDiagram.edge_coordinates
      ~FormDiagram.edge_direction
      ~FormDiagram.edge_faces
      ~FormDiagram.edge_label_name
      ~FormDiagram.edge_length
      ~FormDiagram.edge_midpoint
      ~FormDiagram.edge_name
      ~FormDiagram.edge_point
      ~FormDiagram.edge_vector
      ~FormDiagram.edges
      ~FormDiagram.edges_attribute
      ~FormDiagram.edges_attributes
      ~FormDiagram.edges_on_boundary
      ~FormDiagram.edges_where
      ~FormDiagram.edges_where_predicate
      ~FormDiagram.euler
      ~FormDiagram.face_adjacency
      ~FormDiagram.face_adjacency_edge
      ~FormDiagram.face_adjacency_halfedge
      ~FormDiagram.face_adjacency_vertices
      ~FormDiagram.face_area
      ~FormDiagram.face_aspect_ratio
      ~FormDiagram.face_attribute
      ~FormDiagram.face_attributes
      ~FormDiagram.face_center
      ~FormDiagram.face_centroid
      ~FormDiagram.face_coordinates
      ~FormDiagram.face_corners
      ~FormDiagram.face_curvature
      ~FormDiagram.face_degree
      ~FormDiagram.face_flatness
      ~FormDiagram.face_halfedges
      ~FormDiagram.face_label_name
      ~FormDiagram.face_max_degree
      ~FormDiagram.face_min_degree
      ~FormDiagram.face_name
      ~FormDiagram.face_neighborhood
      ~FormDiagram.face_neighbors
      ~FormDiagram.face_normal
      ~FormDiagram.face_skewness
      ~FormDiagram.face_vertex_ancestor
      ~FormDiagram.face_vertex_descendant
      ~FormDiagram.face_vertices
      ~FormDiagram.faces
      ~FormDiagram.faces_attribute
      ~FormDiagram.faces_attributes
      ~FormDiagram.faces_on_boundary
      ~FormDiagram.faces_where
      ~FormDiagram.faces_where_predicate
      ~FormDiagram.fixed
      ~FormDiagram.flip_cycles
      ~FormDiagram.from_data
      ~FormDiagram.from_graph
      ~FormDiagram.from_json
      ~FormDiagram.from_lines
      ~FormDiagram.from_obj
      ~FormDiagram.from_off
      ~FormDiagram.from_pickle
      ~FormDiagram.from_ply
      ~FormDiagram.from_points
      ~FormDiagram.from_polygons
      ~FormDiagram.from_polyhedron
      ~FormDiagram.from_polylines
      ~FormDiagram.from_shape
      ~FormDiagram.from_stl
      ~FormDiagram.from_vertices_and_faces
      ~FormDiagram.genus
      ~FormDiagram.get_any_edge
      ~FormDiagram.get_any_face
      ~FormDiagram.get_any_face_vertex
      ~FormDiagram.get_any_vertex
      ~FormDiagram.get_any_vertices
      ~FormDiagram.gkey_key
      ~FormDiagram.halfedge_face
      ~FormDiagram.identify_constraints
      ~FormDiagram.identify_fixed
      ~FormDiagram.ind
      ~FormDiagram.index_key
      ~FormDiagram.index_uv
      ~FormDiagram.indexed_face_vertices
      ~FormDiagram.insert_vertex
      ~FormDiagram.is_connected
      ~FormDiagram.is_edge_on_boundary
      ~FormDiagram.is_empty
      ~FormDiagram.is_face_on_boundary
      ~FormDiagram.is_halfedge
      ~FormDiagram.is_manifold
      ~FormDiagram.is_orientable
      ~FormDiagram.is_quadmesh
      ~FormDiagram.is_regular
      ~FormDiagram.is_trimesh
      ~FormDiagram.is_valid
      ~FormDiagram.is_vertex_connected
      ~FormDiagram.is_vertex_on_boundary
      ~FormDiagram.key_gkey
      ~FormDiagram.key_index
      ~FormDiagram.leaves
      ~FormDiagram.normal
      ~FormDiagram.number_of_edges
      ~FormDiagram.number_of_faces
      ~FormDiagram.number_of_vertices
      ~FormDiagram.q
      ~FormDiagram.set_edge_force
      ~FormDiagram.set_edge_force_by_index
      ~FormDiagram.set_edge_forcedensity
      ~FormDiagram.set_fixed
      ~FormDiagram.smooth_area
      ~FormDiagram.smooth_centroid
      ~FormDiagram.split_edge
      ~FormDiagram.summary
      ~FormDiagram.to_data
      ~FormDiagram.to_json
      ~FormDiagram.to_lines
      ~FormDiagram.to_obj
      ~FormDiagram.to_off
      ~FormDiagram.to_pickle
      ~FormDiagram.to_ply
      ~FormDiagram.to_points
      ~FormDiagram.to_polygons
      ~FormDiagram.to_polylines
      ~FormDiagram.to_quadmesh
      ~FormDiagram.to_stl
      ~FormDiagram.to_trimesh
      ~FormDiagram.to_vertices_and_faces
      ~FormDiagram.transform
      ~FormDiagram.transformed
      ~FormDiagram.unify_cycles
      ~FormDiagram.unset_edge_attribute
      ~FormDiagram.unset_face_attribute
      ~FormDiagram.unset_vertex_attribute
      ~FormDiagram.update_default_edge_attributes
      ~FormDiagram.update_default_face_attributes
      ~FormDiagram.update_default_vertex_attributes
      ~FormDiagram.uv_index
      ~FormDiagram.vertex_area
      ~FormDiagram.vertex_attribute
      ~FormDiagram.vertex_attributes
      ~FormDiagram.vertex_coordinates
      ~FormDiagram.vertex_curvature
      ~FormDiagram.vertex_degree
      ~FormDiagram.vertex_faces
      ~FormDiagram.vertex_label_name
      ~FormDiagram.vertex_laplacian
      ~FormDiagram.vertex_max_degree
      ~FormDiagram.vertex_min_degree
      ~FormDiagram.vertex_name
      ~FormDiagram.vertex_neighborhood
      ~FormDiagram.vertex_neighborhood_centroid
      ~FormDiagram.vertex_neighbors
      ~FormDiagram.vertex_normal
      ~FormDiagram.vertices
      ~FormDiagram.vertices_attribute
      ~FormDiagram.vertices_attributes
      ~FormDiagram.vertices_on_boundaries
      ~FormDiagram.vertices_on_boundary
      ~FormDiagram.vertices_where
      ~FormDiagram.vertices_where_predicate
      ~FormDiagram.xy
   
   

   
   
   .. rubric:: Attributes

   .. autosummary::
   
      ~FormDiagram.adjacency
      ~FormDiagram.data
      ~FormDiagram.name
   
   