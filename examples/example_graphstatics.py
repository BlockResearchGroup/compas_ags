import compas
import compas_ags

from compas_ags.diagrams import FormGraph
from compas_ags.diagrams import FormDiagram
from compas_ags.diagrams import ForceDiagram
from compas_ags.ags import graphstatics

from compas_ags.viewers import Viewer


# ------------------------------------------------------------------------------
#   1. get lines of a plane triangle frame in equilibrium, its applied loads and reaction forces
#      make form and force diagrams
# ------------------------------------------------------------------------------
graph = FormGraph.from_obj(compas_ags.get('paper/gs_form_force.obj'))

form = FormDiagram.from_graph(graph)
force = ForceDiagram.from_formdiagram(form)


# ------------------------------------------------------------------------------
#   2. set applied load
# ------------------------------------------------------------------------------
# choose an independent edge and set the magnitude of the applied load
# the system is statically determinate, thus choosing one edge is enough
form.set_edge_force_by_index(0, -30.0)

# update force densities of form and force diagrams
graphstatics.form_update_q_from_qind(form)
graphstatics.force_update_from_form(force, form)


# ------------------------------------------------------------------------------
#   3. display force and form diagrams
# ------------------------------------------------------------------------------
viewer = Viewer(form, force, delay_setup=False, figsize=(9, 6))

left  = list(form.vertices_where({'x': 0.0, 'y': 0.0}))[0]
right = list(form.vertices_where({'x': 6.0, 'y': 0.0}))[0]

viewer.draw_form(
    vertexsize=0.15,
    vertexcolor={key: '#000000' for key in (left, right)},
    vertexlabel={key: key for key in form.vertices()},
    edgelabel={uv: index for index, uv in enumerate(form.edges())})

viewer.draw_force(
    vertexsize=0.15,
    vertexlabel={key: key for key in force.vertices()})

viewer.show()
