import os
import compas
import compas_rhino

compas_rhino.unload_modules('compas_ags')
import compas_ags

from compas.rpc import Proxy

from compas_ags.diagrams import FormGraph
from compas_ags.diagrams import FormDiagram
from compas_ags.diagrams import ForceDiagram
from compas_ags.rhino import Scene


HERE = os.path.dirname(__file__)
DATA = os.path.join(HERE, '../data')
FILE = os.path.join(DATA, 'paper/gs_form_force.obj')

ags = Proxy('compas_ags.ags')

# ags.stop_server()
# ags.start_server()

graph = FormGraph.from_obj(FILE)
form = FormDiagram.from_graph(graph)
force = ForceDiagram.from_formdiagram(form)

x = form.vertices_attribute('x')
left  = list(form.vertices_where({'x': min(x), 'y': 0.0}))[0]
right = list(form.vertices_where({'x': max(x), 'y': 0.0}))[0]

form.vertex_attribute(left, 'is_fixed', True)
form.vertex_attribute(right, 'is_fixed', True)

form.set_edge_force_by_index(0, -30.0)


form.data = ags.form_update_q_from_qind_proxy(form.data)
# ags.force_update_from_form_proxy(force.to_data(), form.to_data())


scene = Scene()

scene.add(form, name='form', layer='AGS::FormDiagram', settings={'show.edgelabels': True})
scene.add(force, name='force', layer='AGS::ForceDiagram', settings={'show.edgelabels': True})

scene.update()
