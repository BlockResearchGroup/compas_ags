from compas_rhino import unload_modules
unload_modules("compas")

import os
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
# Get lines from layers in rhino
structure_guids = compas_rhino.get_lines(layer='structure')
structure_lines = compas_rhino.get_line_coordinates(structure_guids)

reaction_guids = compas_rhino.get_lines(layer='reaction')
reaction_lines = compas_rhino.get_line_coordinates(reaction_guids)

loads_guids = compas_rhino.get_lines(layer='loads')
loads_lines = compas_rhino.get_line_coordinates(loads_guids)

lines = structure_lines + reaction_lines + loads_lines
graph = FormGraph.from_lines(lines)
form = FormDiagram.from_graph(graph)

# ==============================================================================
# Attributes
# ==============================================================================
# Hide input lines
rs.HideObjects(structure_guids)
rs.HideObjects(reaction_guids)
rs.HideObjects(loads_guids)

# draw the form diagram
formartist = FormArtist(form, layer='FormDiagram')
formartist.draw_diagram()

# set independent edge and force
index, uv = select_loaded_edges(form)
force_value = rs.GetReal("Force on Edges", 1.0)
form.set_edge_force_by_index(index, force_value)


# set the fixed vertices of form diagram
fixed = diagram_fix_vertice(form)


# ==============================================================================
# Visualize result
# ==============================================================================
formartist.draw_fixed_vertice()
formartist.draw_leaves()
formartist.draw_independent_edge()


# ==============================================================================
# Export result
# ==============================================================================
HERE = os.path.dirname(__file__)
DATA = os.path.join(HERE, 'data')
form_file = os.path.join(DATA, 'form.json')

form.to_json(form_file)