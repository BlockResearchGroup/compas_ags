import os

from compas_ags.diagrams import FormGraph
from compas_ags.diagrams import FormDiagram
from compas_ags.diagrams import ForceDiagram
from compas_ags.rhino import Scene

from compas.rpc import Proxy

graphstatics = Proxy('compas_ags.ags.graphstatics')
graphstatics.stop_server()
graphstatics.start_server()

# this file has unloaded, 2-valent nodes
# they will be removed automatically
# and the result renumbered
HERE = os.path.dirname(__file__)
FILE = os.path.join(HERE, '../data/debugging/exercise.obj')

graph = FormGraph.from_obj(FILE)
form = FormDiagram.from_graph(graph)
force = ForceDiagram.from_formdiagram(form)

# fix the supports
form.vertices_attribute('is_fixed', True, [12, 10])

# set the loads
form.edge_force((0, 1), +10.0)
form.edge_force((2, 3), +10.0)
form.edge_force((4, 5), +10.0)
form.edge_force((6, 7), +10.0)
form.edge_force((8, 9), +10.0)

# compute initial form and force diagrams
form.data = graphstatics.form_update_q_from_qind_proxy(form.data)
force.data = graphstatics.force_update_from_form_proxy(force.data, form.data)

form.vertices_attribute('is_fixed', True, [0, 2, 4, 6, 8])

## change the geometry of the force diagram
force.vertex_attribute(13, 'x', force.vertex_attribute(16, 'x'))
force.vertex_attribute(9, 'x', force.vertex_attribute(7, 'x'))
force.vertex_attributes(15, 'xyz', force.vertex_attributes(13, 'xyz'))
force.vertex_attributes(8, 'xyz', force.vertex_attributes(9, 'xyz'))

force.vertex_attribute(14, 'x', force.vertex_attribute(16, 'x'))
force.vertex_attribute(11, 'x', force.vertex_attribute(7, 'x'))
force.vertex_attributes(12, 'xyz', force.vertex_attributes(14, 'xyz'))
force.vertex_attributes(10, 'xyz', force.vertex_attributes(11, 'xyz'))

# # change the depth of the structure
# force.vertices_attribute('x', 20, [6, 7, 8, 9, 10, 11])

# fix some of the nodes in the from diagram
# to constraint the problem to a single solution


# update the form diagram
form.data = graphstatics.form_update_from_force_proxy(form.data, force.data)

# ==============================================================================
# Visualize
# ==============================================================================

scene = Scene()

form_id = scene.add(form, name="Form", layer="AGS::FormDiagram")
force_id = scene.add(force, name="Force", layer="AGS::ForceDiagram")

scene.clear()

form_obj = scene.find(form_id)
force_obj = scene.find(force_id)

# this should become part of "add"
force_obj.artist.anchor_vertex = 0
force_obj.artist.anchor_point = [35, 0, 0]
force_obj.artist.scale = 0.2

form_obj.artist.settings['scale.forces'] = 0.01
force_obj.artist.settings['show.vertexlabels'] = True
scene.update()
