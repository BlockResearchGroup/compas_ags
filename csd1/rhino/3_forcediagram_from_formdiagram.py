from compas_rhino import unload_modules
unload_modules("compas")

import os
import rhinoscriptsyntax as rs

from compas_ags.diagrams import FormDiagram
from compas_ags.diagrams import ForceDiagram

from compas_ags.rhino import FormArtist
from compas_ags.rhino import ForceArtist
from compas_ags.rhino import select_forcediagram_location

from compas.rpc import Proxy
graphstatics = Proxy('compas_ags.ags.graphstatics')


# ==============================================================================
# Load Formdiagram
# ==============================================================================

HERE = os.path.dirname(__file__)
DATA = os.path.join(HERE, 'data')
form_file = os.path.join(DATA, 'form.json')

form = FormDiagram.from_json(form_file)
force = ForceDiagram.from_formdiagram(form) # dual-mesh of form

select_forcediagram_location(force)

# update diagrams
form_data = graphstatics.form_update_q_from_qind_rhino(form.to_data())
force_data = graphstatics.force_update_from_form_rhino(force.to_data(), form_data)
form = FormDiagram.from_data(form_data)
force = ForceDiagram.from_data(force_data)


# ==============================================================================
# Visualize result
# ==============================================================================
formartist = FormArtist(form, layer='FormDiagram')
formartist.draw_diagram()
formartist.draw_fixed_vertice()
formartist.draw_independent_edge()

forceartist = ForceArtist(force, layer='ForceDiagram')
forceartist.draw_diagram(form=form)
forceartist.draw_independent_edges(form)

# ==============================================================================
# Export result
# ==============================================================================
form.to_json(form_file)

force_file = os.path.join(DATA, 'force.json')
force.to_json(force_file)