from compas_rhino import unload_modules  
unload_modules("compas")

import os
import rhinoscriptsyntax as rs
import compas_rhino

from compas_ags.diagrams import FormGraph
from compas_ags.diagrams import FormDiagram
from compas_ags.diagrams import ForceDiagram


from compas_ags.rhino import Scene
from compas.rpc import Proxy

graphstatics = Proxy('compas_ags.ags.graphstatics')


HERE = os.path.dirname(__file__)
DATA = os.path.join(HERE, '../data')
FILE = os.path.join(DATA, 'debugging', 'bridge.obj')

#guids = compas_rhino.select_lines(message='Select Form Diagram Lines')
#lines = compas_rhino.get_line_coordinates(guids)
#rs.HideObjects(guids)
#graph = FormGraph.from_lines(lines)

graph = FormGraph.from_obj(FILE)
form = FormDiagram.from_graph(graph)
force = ForceDiagram.from_formdiagram(form)

scene = Scene()
form_id = scene.add(form, name="Form", layer="AGS::FormDiagram")
scene.clear()
form_obj = scene.find(form_id)
scene.update()


# select edges
while True:
    edges = form_obj.select_edges()
    if not edges:
        break
    force_value = rs.GetReal("Force on Edges (kN)", 1.0)
    for (u, v) in edges: 
        form.edge_force((u, v), force_value)
    scene.update()


force_id = scene.add(force, name="Force", layer="AGS::ForceDiagram")
force_obj = scene.find(force_id)

# this should become part of "add"
force_obj.artist.anchor_vertex = 5
force_obj.artist.anchor_point = [100, 0, 0]
force_obj.artist.scale = 5



form.data = graphstatics.form_update_q_from_qind_proxy(form.data)
force.data = graphstatics.force_update_from_form_proxy(force.data, form.data)

print(graphstatics.form_count_dof_proxy(form.data))

scene.clear()
scene.update()
