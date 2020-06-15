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


# ==============================================================================
# Visualize result
# ==============================================================================
formartist = FormArtist(form, layer='FormDiagram')
formartist.draw_diagram()


forceartist = ForceArtist(force, layer='ForceDiagram')
forceartist.draw_diagram(form=form)