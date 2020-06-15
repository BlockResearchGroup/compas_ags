from compas_rhino import unload_modules
unload_modules("compas")

import rhinoscriptsyntax as rs

import compas_rhino

from compas_ags.diagrams import FormGraph
from compas_ags.diagrams import FormDiagram
from compas_ags.rhino import FormArtist

# ==============================================================================
# Input
# ==============================================================================
# Select lines in rhino
guids = compas_rhino.select_lines(message='Select Form Diagram Lines')
lines = compas_rhino.get_line_coordinates(guids)
# Hide input lines
rs.HideObjects(guids)

graph = FormGraph.from_lines(lines)
print(graph.is_2d())
form = FormDiagram.from_graph(graph)


# ==============================================================================
# Visualize result
# ==============================================================================
formartist = FormArtist(form, layer='FormDiagram')

formartist.draw_diagram()

#formartist.draw_mesh( )
#formartist.draw_faces()
#formartist.draw_facelabels()