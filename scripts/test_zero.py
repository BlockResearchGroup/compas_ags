import compas_ags

from compas_ags.diagrams import FormGraph
from compas_ags.diagrams import FormDiagram
from compas_ags.diagrams import ForceDiagram
from compas_ags.ags import graphstatics

from compas_ags.viewers import Viewer

FILE = compas_ags.get('debugging/zero.obj')

graph = FormGraph.from_obj(FILE)
form = FormDiagram.from_graph(graph)
force = ForceDiagram.from_formdiagram(form)

form.vertices_attribute('is_fixed', True, [8, 7])
form.vertices_attribute('is_fixed', True, [0, 2, 5])

form.edge_force((0, 1), +10.0)
form.edge_force((2, 3), +10.0)
form.edge_force((4, 5), +10.0)

graphstatics.form_update_q_from_qind(form)
graphstatics.force_update_from_form(force, form)

force.vertex_attribute(6, 'x', force.vertex_attribute(8, 'x'))
force.vertex_attribute(9, 'x', force.vertex_attribute(10, 'x'))

force.vertex_attributes(7, 'xyz', force.vertex_attributes(6, 'xyz'))
force.vertex_attributes(11, 'xyz', force.vertex_attributes(9, 'xyz'))

graphstatics.form_update_from_force(form, force)

viewer = Viewer(form, force, delay_setup=False, figsize=(12, 7.5))

viewer.draw_form(
    vertexsize=0.15,
    vertexcolor={key: '#000000' for key in (8, 7)},
    vertexlabel={key: key for key in form.vertices()},
    edgelabel={uv: index for index, uv in enumerate(form.edges())})

viewer.draw_force(
    vertexsize=0.15,
    vertexlabel={key: key for key in force.vertices()})

viewer.show()
