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
FILE = os.path.join(DATA, 'paper', 'gs_form_force.obj')

# ==============================================================================
# Init
# ==============================================================================

graph = FormGraph.from_obj(FILE)

form = FormDiagram.from_graph(graph)
force = ForceDiagram.from_formdiagram(form)

# ==============================================================================
# Boundary conditions
# ==============================================================================

left = next(form.vertices_where({'x': 0.0, 'y': 0.0}))
right = next(form.vertices_where({'x': 6.0, 'y': 0.0}))

form.vertices_attribute('is_fixed', True, keys=[left, right])

form.edge_force(1, -10.0)

# ==============================================================================
# Equilibrium
# ==============================================================================

form.data = graphstatics.form_update_q_from_qind_proxy(form.data)
force.data = graphstatics.force_update_from_form_proxy(force.data, form.data)

# ==============================================================================
# Visualize
# ==============================================================================

scene = Scene()

form_id = scene.add(form, name="Form", layer="AGS::FormDiagram")
force_id = scene.add(force, name="Force", layer="AGS::ForceDiagram")

scene.clear_layers()

form_obj = scene.find(form_id)
force_obj = scene.find(force_id)

# this should become part of "add"
force_obj.anchor = 3
force_obj.location = [15, 0, 0]
force_obj.scale = 0.3

scene.update()

# ==============================================================================
# Update
# ==============================================================================

while True:
    vertices = force_obj.select_vertices()
    if not vertices:
        break
    if force_obj.move_vertices(vertices):
        # update form diagram
        form.data = graphstatics.form_update_from_force_proxy(form.data, force.data, kmax=100)
        # update the scene
        scene.update()
