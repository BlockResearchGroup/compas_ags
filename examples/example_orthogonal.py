import random

import compas
import compas_ags

from compas_ags.diagrams import FormGraph
from compas_ags.diagrams import FormDiagram
from compas_ags.diagrams import ForceDiagram
from compas_ags.ags import graphstatics

from compas_ags.viewers import Viewer

graph = FormGraph.from_obj(compas.get('lines.obj'))

form = FormDiagram.from_graph(graph)
force = ForceDiagram.from_formdiagram(form)

form.vertices_attribute('is_fixed', True, keys=form.leaves())

k, m, ind = graphstatics.form_identify_dof(form)

for u, v in ind:
    form.edge_attributes((u, v), ('is_ind', 'q'), (True, random.choice(range(2, 20))))

graphstatics.form_update_q_from_qind(form)
graphstatics.force_update_from_form(force, form)

viewer = Viewer(form, force, delay_setup=False)

viewer.draw_form(
    vertexsize=0.15,
    external_on=False)

viewer.draw_force(
    vertexsize=0.15)

viewer.show()
