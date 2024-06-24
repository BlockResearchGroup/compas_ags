import compas_ags
from compas_ags.ags import graphstatics
from compas_ags.diagrams import ForceDiagram
from compas_ags.diagrams import FormDiagram
from compas_ags.diagrams import FormGraph
from compas_ags.viewer import AGSViewer

# ------------------------------------------------------------------------------
# 1. get lines of a plane triangle frame in equilibrium, its applied loads and reaction forces
#    make form and force diagrams
# ------------------------------------------------------------------------------

graph = FormGraph.from_obj(compas_ags.get("paper/gs_form_force.obj"))

form = FormDiagram.from_graph(graph)
force = ForceDiagram.from_formdiagram(form)

# ------------------------------------------------------------------------------
# 2. set applied load
# ------------------------------------------------------------------------------

# choose an independent edge and set the magnitude of the applied load
# the system is statically determinate, thus choosing one edge is enough
form.edge_force(0, -3.0)

# update force densities of form and force diagrams
graphstatics.form_update_q_from_qind(form)
graphstatics.force_update_from_form(force, form)

# ------------------------------------------------------------------------------
# 3. display force and form diagrams
# ------------------------------------------------------------------------------

viewer = AGSViewer()
viewer.add_form(form)
viewer.add_force(force)
viewer.show()
