import os

from compas_ags.diagrams import FormGraph
from compas_ags.diagrams import FormDiagram
from compas_ags.diagrams import ForceDiagram
from compas_ags.rhino import Scene

from compas.rpc import Proxy

graphstatics = Proxy('compas_ags.ags.graphstatics')
graphstatics.restart_server()

# this file has unloaded, 2-valent nodes
# they will be removed automatically
# and the result renumbered
HERE = os.path.dirname(__file__)
FILE = os.path.join(HERE, '../data/debugging/zero.obj')

graph = FormGraph.from_obj(FILE)
form = FormDiagram.from_graph(graph)
force = ForceDiagram.from_formdiagram(form)
scene = Scene()

# fix the supports
form.vertices_attribute('is_fixed', True, [8, 7])

# set the loads
form.edge_force((0, 1), +10.0)
form.edge_force((2, 3), +10.0)
form.edge_force((4, 5), +10.0)

# compute initial form and force diagrams
form.data = graphstatics.form_update_q_from_qind_proxy(form.data)
force.data = graphstatics.force_update_from_form_proxy(force.data, form.data)

form_id = scene.add(form, name="Form", layer="AGS::FormDiagram")
force_id = scene.add(force, name="Force", layer="AGS::ForceDiagram")

form_obj = scene.find(form_id)
force_obj = scene.find(force_id)

force_obj.artist.anchor_vertex = 0
force_obj.artist.anchor_point = [35, 0, 0]
force_obj.artist.scale = 0.5

form_obj.artist.settings['scale.forces'] = 0.02

scene.clear()
scene.update()

while True:
    vertices = force_obj.select_vertices()
    if not vertices:
        break
    if vertices and force_obj.move_vertices(vertices):
        scene.clear()
        scene.update()

scene.clear()
scene.update()

# fix some of the nodes in the from diagram
# to constraint the problem to a single solution
form.vertices_attribute('is_fixed', True, [0, 2, 5])

# update the form diagram
form.data = graphstatics.form_update_from_force_proxy(form.data, force.data)

scene.update()
