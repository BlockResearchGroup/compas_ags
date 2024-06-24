import compas_ags
from compas_ags.ags import graphstatics
from compas_ags.diagrams import ForceDiagram
from compas_ags.diagrams import FormDiagram
from compas_ags.diagrams import FormGraph
from compas_ags.viewer import AGSViewer

# ==============================================================================
# Construct the graph of a single panel truss,
# including loads and reaction forces.
# ==============================================================================

graph = FormGraph.from_obj(compas_ags.get("paper/gs_form_force.obj"))

form = FormDiagram.from_graph(graph)
force = ForceDiagram.from_formdiagram(form)

# ==============================================================================
# Fix the left and right supports.
# ==============================================================================

left = next(form.vertices_where({"x": 0.0, "y": 0.0}))
right = next(form.vertices_where({"x": 6.0, "y": 0.0}))
fixed = [left, right]

form.vertices_attribute("is_fixed", True, keys=fixed)

# ==============================================================================
# Set the magnitude of the load.
# ==============================================================================

form.edge_force(1, -10.0)

# ==============================================================================
# Update the force densities in the form diagram.
# ==============================================================================

graphstatics.form_update_q_from_qind(form)

# ==============================================================================
# Update the geometry of the force diagram.
# ==============================================================================

graphstatics.force_update_from_form(force, form)

# ==============================================================================
# Store the original geometries.
# ==============================================================================

# ==============================================================================
# Change the position of the "free" node of the force diagram
# ==============================================================================

force.vertex[4]["x"] -= 8.0

# ==============================================================================
# Update the form diagram accordingly.
# ==============================================================================

graphstatics.form_update_from_force(form, force, kmax=100)

# ==============================================================================
# Indicate the movement of the free node in the force diagram with an arrow.
# ==============================================================================

# ==============================================================================
# Visualize the result.
# ==============================================================================

viewer = AGSViewer()
viewer.add_form(form, scale_forces=0.05)
viewer.add_force(force)
viewer.show()
