import random
import compas

from compas_ags.diagrams import FormGraph
from compas_ags.diagrams import FormDiagram
from compas_ags.diagrams import ForceDiagram
from compas_ags.ags import graphstatics

from compas_ags.viewers import Viewer

# ------------------------------------------------------------------------------
# 1. get lines of an orthogonal grid and its boundary conditions
#    make form and force diagrams
# ------------------------------------------------------------------------------

graph = FormGraph.from_obj(compas.get('lines.obj'))

form = FormDiagram.from_graph(graph)
force = ForceDiagram.from_formdiagram(form)

# ------------------------------------------------------------------------------
# 2. assign applied loads and boundary vertices
# ------------------------------------------------------------------------------

# fix boundary vertices
form.vertices_attribute('is_fixed', True, keys=form.leaves())

# get indices of independent edges
ind = graphstatics.form_identify_dof(form)[2]

# apply a random force density between 2 and 20 to independent edges
for u, v in ind:
    form.edge_attributes((u, v), ('is_ind', 'q'), (True, random.choice(range(2, 20))))

# update force densities of form and force diagram
graphstatics.form_update_q_from_qind(form)
graphstatics.force_update_from_form(force, form)

# ------------------------------------------------------------------------------
# 3. display force and form diagrams
# ------------------------------------------------------------------------------

viewer = Viewer(form, force, delay_setup=False, figsize=(12, 7.5))

viewer.draw_form(
    vertexsize=0.15,
    external_on=False)

viewer.draw_force(
    vertexsize=0.15)

viewer.show()
