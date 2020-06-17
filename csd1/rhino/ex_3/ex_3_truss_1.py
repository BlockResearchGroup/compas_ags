import os
import rhinoscriptsyntax as rs

from compas_rhino import unload_modules  
unload_modules("compas")

import compas_rhino

from compas_ags.rhino import select_forcediagram_location
from compas_ags.rhino import diagram_fix_vertice
from compas_ags.rhino import set_edge_loads
from compas_ags.rhino import ForceArtist
from compas_ags.rhino import FormArtist
from compas_ags.diagrams import ForceDiagram
from compas_ags.diagrams import FormDiagram
from compas_ags.diagrams import FormGraph

from compas.rpc import Proxy
graphstatics = Proxy('compas_ags.ags.graphstatics')


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

# Hide input lines
rs.HideObjects(structure_guids)
rs.HideObjects(reaction_guids)
rs.HideObjects(loads_guids)

graph = FormGraph.from_lines(lines)
form = FormDiagram.from_graph(graph)
force = ForceDiagram.from_formdiagram(form)

formartist = FormArtist(form, layer='FormDiagram')
formartist.draw_diagram()


# ==============================================================================
# Set loads and constrains
# ==============================================================================
set_edge_loads(form)
fixed = diagram_fix_vertice(form)
select_forcediagram_location(force)


# ==============================================================================
# Update diagrams
# ==============================================================================
form_data = graphstatics.form_update_q_from_qind_rhino(form.to_data())
force_data = graphstatics.force_update_from_form_rhino(force.to_data(), form_data)

form = FormDiagram.from_data(form_data)
force = ForceDiagram.from_data(force_data)


# ==============================================================================
# Visualize result
# ==============================================================================
# if the formdiagram is updated, how to update the formartist?
formartist = FormArtist(form, layer='FormDiagram')
formartist.draw_diagram()
formartist.draw_independent_edge()
formartist.draw_fixed_vertice()
formartist.draw_leaves()
formartist.draw_forces(scale=0.05)


forceartist = ForceArtist(force, form=form, layer='ForceDiagram')
forceartist.draw_diagram()
forceartist.draw_independent_edges()
forceartist.draw_edge_force()
forceartist.draw_anchor_vertex()

# ==============================================================================
# Save data
# ==============================================================================
HERE = os.path.dirname(__file__)
DATA = os.path.join(HERE, 'data')
form_file = os.path.join(DATA, 'ex_3_form.json')
form.to_json(form_file)
force_file = os.path.join(DATA, 'ex_3_force.json')
force.to_json(force_file)
