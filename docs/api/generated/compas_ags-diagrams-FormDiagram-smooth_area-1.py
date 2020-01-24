import compas

from compas.datastructures import Mesh
from compas.datastructures import mesh_smooth_area
from compas_plotters import MeshPlotter

mesh = Mesh.from_obj(compas.get('faces.obj'))
fixed = [key for key in mesh.vertices() if mesh.vertex_degree(key) == 2]

mesh_smooth_area(mesh, fixed=fixed)

plotter = MeshPlotter(mesh)

plotter.draw_vertices(facecolor={key: '#ff0000' for key in fixed})
plotter.draw_faces()
plotter.draw_edges()

plotter.show()