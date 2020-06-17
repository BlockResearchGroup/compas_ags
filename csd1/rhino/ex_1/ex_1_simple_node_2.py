
import os
import rhinoscriptsyntax as rs

from compas_rhino import unload_modules
unload_modules("compas")

import compas_rhino

from compas_ags.rhino import move_form_vertice
from compas_ags.rhino import ForceArtist
from compas_ags.rhino import FormArtist
from compas_ags.diagrams import ForceDiagram
from compas_ags.diagrams import FormDiagram


from compas.rpc import Proxy
graphstatics = Proxy('compas_ags.ags.graphstatics')


# ==============================================================================
# Load Diagrams
# ==============================================================================
HERE = os.path.dirname(__file__)
DATA = os.path.join(HERE, 'data')
form_file = os.path.join(DATA, 'ex_1_form.json')
force_file = os.path.join(DATA, 'ex_1_force.json')

form = FormDiagram.from_json(form_file)
force = ForceDiagram.from_json(force_file)

formartist = FormArtist(form, layer='FormDiagram')
forceartist = ForceArtist(force, form=form, layer='ForceDiagram')

formartist.draw_diagram()
formartist.draw_independent_edge()
formartist.draw_fixed_vertice()

forceartist.draw_diagram()
forceartist.draw_independent_edges()
forceartist.draw_edge_force()
forceartist.draw_anchor_vertex()


# ==============================================================================
# Modify Formdiagram
# ==============================================================================
move_form_vertice(form, formartist)

formartist.draw_diagram()
formartist.draw_independent_edge()


# ==============================================================================
# Update Forcediagram
# ==============================================================================
form_data = graphstatics.form_update_q_from_qind_rhino(form.to_data())
force_data = graphstatics.force_update_from_form_rhino(force.to_data(), form_data)
form = FormDiagram.from_data(form_data)
force = ForceDiagram.from_data(force_data)

# when update force diagram, force artist doesn't update automatically? 
# construct a new force artist
forceartist = ForceArtist(force, form=form, layer='ForceDiagram')
forceartist.draw_diagram()
forceartist.draw_independent_edges()
forceartist.draw_edge_force()


# ==============================================================================
# Save data
# ==============================================================================
form.to_json(form_file)
force.to_json(force_file)
