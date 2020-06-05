from compas_rhino import unload_modules
unload_modules("compas")

import os
import rhinoscriptsyntax as rs

from compas_ags.diagrams import FormDiagram
from compas_ags.diagrams import ForceDiagram

from compas_ags.rhino import FormArtist
from compas_ags.rhino import ForceArtist
from compas_ags.rhino import draw_dual_form_vertices_force_faces

# ==============================================================================
# Load Diagrams
# ==============================================================================

HERE = os.path.dirname(__file__)
DATA = os.path.join(HERE, 'data')
form_file = os.path.join(DATA, 'form.json')
force_file = os.path.join(DATA, 'force.json')

form = FormDiagram.from_json(form_file)
force = ForceDiagram.from_json(force_file)


# ==============================================================================
# Visualize result
# ==============================================================================

formartist = FormArtist(form, layer='FormDiagram')
forceartist = ForceArtist(force, layer='ForceDiagram')

draw_dual_form_vertices_force_faces(form, force, formartist, forceartist)


