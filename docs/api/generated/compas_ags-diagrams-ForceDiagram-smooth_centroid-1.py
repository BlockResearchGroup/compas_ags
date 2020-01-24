import compas

from compas.datastructures import Mesh
from compas.datastructures import mesh_smooth_centroid
from compas_plotters import MeshPlotter

mesh = Mesh.from_obj(compas.get('faces.obj'))
fixed = list(mesh.vertices_where({'vertex_degree': 2}))

mesh_smooth_centroid(mesh, fixed=fixed)

plotter = MeshPlotter(mesh)

plotter.draw_vertices(facecolor={key: '#ff0000' for key in fixed})
plotter.draw_faces()
plotter.draw_edges()

plotter.show()