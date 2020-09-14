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

from compas_ags.utilities import calculate_drawingscale

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

scale = calculate_drawingscale(form, force)
print(scale)

print(force_object.location)

form_object.clear_layer()
force_object.clear_layer()

# force_object.location = [35, 0, 0]
force_object.scale = scale

form_xyz = list(form_object.vertex_xyz.values())
force_xyz = list(force_object.vertex_xyz.values())

form_xmax = max([xyz[0] for xyz in form_xyz])
form_xmin = min([xyz[0] for xyz in form_xyz])

form_ymin = min([xyz[1] for xyz in form_xyz])

force_xmin = min([xyz[0] for xyz in force_xyz])
force_ymin = min([xyz[1] for xyz in force_xyz])

#anchor_x, anchor_y = force_object.location[0], force_object.location[1]
#danchor_x = anchor_x - force_xmin
#danchor_y = anchor_y - force_ymin

spacing = 0.5 * (form_xmax - form_xmin)

force_object.location[0] += form_xmax + spacing - force_xmin
force_object.location[1] += form_ymin - force_ymin

#dx = form_xmax + spacing - force_xmin
#force_object.location[0] += dx

print(force_object.location)

form_object.draw()
force_object.draw()

# vertices = form_object.select_vertices()
# if vertices and form_object.move_vertices(vertices):
#     form_object.draw()

# vertices = force_object.select_vertices()
# if vertices and force_object.move_vertices(vertices):
#     force_object.draw()

#if force_object.scale_from_3_points(message="Select the base node of the Force Diagram for the scaling operation"):
#    force_object.draw()
