from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

import os

from compas.rpc import Proxy

from compas_ags.diagrams import FormGraph
from compas_ags.diagrams import FormDiagram
from compas_ags.diagrams import ForceDiagram

from compas_ags.rhino import FormObject
from compas_ags.rhino import ForceObject

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

form_object = FormObject(form, name="Form", layer="AGS::FormDiagram")
force_object = ForceObject(force, name="Force", layer="AGS::ForceDiagram")

form_object.clear_layer()
force_object.clear_layer()

form_object.anchor = 9

force_object.anchor = 5
force_object.location = [35, 0, 0]
force_object.scale = 5.0

form_object.draw()
force_object.draw()

vertices = form_object.select_vertices()
if vertices and form_object.move_vertices(vertices):
    form_object.draw()

vertices = force_object.select_vertices()
if vertices and force_object.move_vertices(vertices):
    force_object.draw()
