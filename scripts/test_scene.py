from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

import os

from compas.rpc import Proxy

from compas_ags.diagrams import FormGraph
from compas_ags.diagrams import FormDiagram
from compas_ags.diagrams import ForceDiagram

from compas_ags.rhino import Scene

graphstatics = Proxy('compas_ags.ags.graphstatics')

HERE = os.path.dirname(__file__)
DATA = os.path.join(HERE, '../data')
FILE = os.path.join(DATA, 'debugging', 'truss.obj')

graph = FormGraph.from_obj(FILE)

form = FormDiagram.from_graph(graph)
force = ForceDiagram.from_formdiagram(form)

form.edge_force((0, 1), -1.0)
form.edge_force((2, 3), -1.0)
form.edge_force((4, 5), -1.0)

form.data = graphstatics.form_update_q_from_qind_proxy(form.data)
force.data = graphstatics.force_update_from_form_proxy(force.data, form.data)

# ==============================================================================
# Visualize and Interact
# ==============================================================================

scene = Scene()

form_id = scene.add(form, name="Form", layer="AGS::FormDiagram")
force_id = scene.add(force, name="Force", layer="AGS::ForceDiagram")

form_obj = scene.find(form_id)
force_obj = scene.find(force_id)

# this should become part of "add"
force_obj.artist.anchor_vertex = 5
force_obj.artist.anchor_point = [35, 0, 0]
force_obj.artist.scale = 5.0

scene.update()

vertices = form_obj.select_vertices()
if form_obj.move_vertices(vertices):
    scene.update()
