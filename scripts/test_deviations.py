import compas_ags

from compas.rpc import Proxy

from compas_ags.diagrams import FormGraph
from compas_ags.diagrams import FormDiagram
from compas_ags.diagrams import ForceDiagram

from compas.geometry import angle_vectors_xy
from compas.geometry import subtract_vectors

from compas_ags.rhino import Scene

import compas_rhino

p = Proxy()
p.start_server()
p.stop_server()

graphstatics = Proxy('compas_ags.ags.graphstatics')

FILE = compas_ags.get('debugging/zero.obj')
FILE = '/Users/mricardo/compas_dev/compas_ags/data/debugging/zero.obj'

graph = FormGraph.from_obj(FILE)
form = FormDiagram.from_graph(graph)
force = ForceDiagram.from_formdiagram(form)

form.edge_force((0, 1), +1.0)
form.edge_force((2, 3), +1.0)
form.edge_force((4, 5), +1.0)

form.data = graphstatics.form_update_q_from_qind_proxy(form.data)
force.data = graphstatics.force_update_from_form_proxy(force.data, form.data)

# Pick one key and move
move_key = 2
delta = + 0.1
moving_point = force.vertex_coordinates(move_key)
force.vertex_attribute(move_key, 'x', moving_point[0] + delta)
force.vertex_attribute(move_key, 'y', moving_point[1] + delta)

# Create Scene

from compas_ags.utilities import check_deviations
if not check_deviations(form, force):
    compas_rhino.display_message('Error: Diagrams are not in equilibrium!')

scene = Scene()

form_id = scene.add(form, name="Form", layer="AGS::FormDiagram")
force_id = scene.add(force, name="Force", layer="AGS::ForceDiagram")

form_obj = scene.find(form_id)
force_obj = scene.find(force_id)

force_obj.artist.anchor_vertex = 5
force_obj.artist.anchor_point = [35, 0, 0]
force_obj.artist.scale = 5.0

scene.update()

# if not checked:
#     from compas_plotters import MeshPlotter
#     plotter = MeshPlotter(form)
#     plotter.draw_edges(text={edge: form.edge_attribute(edge, 'a') for edge in form.edges()})
#     plotter.show()

#     plotter = MeshPlotter(force)
#     plotter.draw_edges(text={edge: form.edge_attribute(force.dual_edge(edge), 'a') for edge in force.edges()})
#     plotter.draw_vertices(text={key: key for key in force.vertices()})
#     plotter.show()


