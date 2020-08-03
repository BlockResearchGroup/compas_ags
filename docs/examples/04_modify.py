import compas_ags

from compas_ags.diagrams import FormGraph
from compas_ags.diagrams import FormDiagram
from compas_ags.diagrams import ForceDiagram
from compas_ags.ags import graphstatics

from compas_ags.viewers import Viewer

FILE = compas_ags.get('examples/truss2.obj')

graph = FormGraph.from_obj(FILE)
form = FormDiagram.from_graph(graph)
force = ForceDiagram.from_formdiagram(form)

fixed = [17, 18, 6, 0, 14, 12, 9, 4, 2]

form.vertices_attribute('is_fixed', True, fixed)

# set the loads
form.edge_force((18, 23), +1.0)
form.edge_force((6, 24), +1.0)
form.edge_force((0, 25), +1.0)
form.edge_force((14, 22), +1.0)
form.edge_force((12, 15), +1.0)
form.edge_force((9, 13), +1.0)
form.edge_force((4, 10), +1.0)

# compute initial form and force diagrams
graphstatics.form_update_q_from_qind(form)
graphstatics.force_update_from_form(force, form)

# change the geometry of the force diagram
x = force.vertex_attribute(15, 'x')
force.vertices_attribute('x', x, [10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22])

force.vertex_attributes(16, 'xy', force.vertex_attributes(17, 'xy'))
force.vertex_attributes(20, 'xy', force.vertex_attributes(21, 'xy'))
force.vertex_attributes(13, 'xy', force.vertex_attributes(14, 'xy'))

force.vertex_attributes(22, 'xy', force.vertex_attributes(19, 'xy'))
force.vertex_attributes(18, 'xy', force.vertex_attributes(12, 'xy'))
force.vertex_attributes(10, 'xy', force.vertex_attributes(11, 'xy'))

# update the form diagram
graphstatics.form_update_from_force(form, force)

# ==============================================================================
# Visualize
# ==============================================================================

viewer = Viewer(form, force, delay_setup=False, figsize=(12, 7.5))

viewer.draw_form(
    vertexsize=0.10,
    vertexcolor={key: '#000000' for key in fixed},
    forcescale=2.0,
    faces_on=False,
    facelabel={key: str(key) for key in form.faces()})

viewer.draw_force(
    vertexsize=0.10,
    # vertexlabel={key: key for key in force.vertices()}
)

viewer.show()
