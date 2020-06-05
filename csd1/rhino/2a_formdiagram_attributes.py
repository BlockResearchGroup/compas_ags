from compas_rhino import unload_modules
unload_modules("compas")

import rhinoscriptsyntax as rs

import compas_rhino

from compas_ags.diagrams import FormGraph
from compas_ags.diagrams import FormDiagram
from compas_ags.rhino import FormArtist
from compas_ags.rhino import select_loaded_edges
from compas_ags.rhino import diagram_fix_vertice

# ==============================================================================
# Input
# ==============================================================================
# Select lines in rhino
guids = compas_rhino.select_lines(message='Select Form Diagram Lines')
lines = compas_rhino.get_line_coordinates(guids)

graph = FormGraph.from_lines(lines)
form = FormDiagram.from_graph(graph)

# ==============================================================================
# Attributes
# ==============================================================================
# Hide input lines
rs.HideObjects(guids)

# draw the form diagram
formartist = FormArtist(form, layer='FormDiagram')
formartist.draw_diagram()

# set independent edge and force
index, uv = select_loaded_edges(form)
force_value = rs.GetReal("Force on Edges", 1.0)
form.set_edge_force_by_index(index, force_value)


# set the fixed vertices of form diagram
fixed = diagram_fix_vertice(form)
print(fixed)

# ==============================================================================
# Visualize result
# ==============================================================================
formartist.draw_fixed_vertice()
formartist.draw_leaves()
formartist.draw_independent_edge()