import json
import compas_ags

from compas_ags.diagrams import FormGraph
from compas_ags.diagrams import FormDiagram
from compas_ags.diagrams import ForceDiagram
from compas_ags.ags import graphstatics
from compas_ags.viewers import Viewer

# this file has unloaded, 2-valent nodes
# they will be removed automatically
# and the result renumbered
FILE = compas_ags.get('forms/howe_modified.ags')

with open(FILE, 'r') as f:
    data = json.load(f)

    form = FormDiagram.from_data(data['data']['form'])
    force = ForceDiagram.from_data(data['data']['force'])
    form.dual = force
    force.dual = form

graphstatics.form_update_from_force(form, force, kmax=100)

# ==============================================================================
# Visualize
# ==============================================================================

viewer = Viewer(form, force, delay_setup=False, figsize=(12, 7.5))

viewer.draw_form(
    vertexsize=0.15,
    vertexcolor={key: '#000000' for key in form.vertices_where({'is_fixed': True})},
    vertexlabel={key: key for key in form.vertices()})

viewer.draw_force(
    vertexsize=0.15,
    vertexlabel={key: key for key in force.vertices()})

viewer.show()
