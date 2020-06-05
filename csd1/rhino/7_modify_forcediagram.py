from compas_rhino import unload_modules
unload_modules("compas")

import os
import rhinoscriptsyntax as rs

from compas_ags.diagrams import FormDiagram
from compas_ags.diagrams import ForceDiagram

from compas_ags.rhino import FormArtist
from compas_ags.rhino import ForceArtist

from compas.rpc import Proxy
rf = Proxy('compas_ags.ags2.rootfinding')


# ==============================================================================
# Load Diagrams
# ==============================================================================

HERE = os.path.dirname(__file__)
DATA = os.path.join(HERE, 'data')
form_file = os.path.join(DATA, 'form.json')
force_file = os.path.join(DATA, 'force.json')

form = FormDiagram.from_json(form_file)
force = ForceDiagram.from_json(force_file)

formartist = FormArtist(form, layer='FormDiagram')
forceartist = ForceArtist(force, layer='ForceDiagram')
formartist.draw_diagram()
forceartist.draw_diagram(form=form)

# ==============================================================================
# Constraints
# ==============================================================================


# set constraints
from compas_ags.constraints import ConstraintsCollection
C = ConstraintsCollection(form)

# set vertex constraints
from compas_ags.rhino import rhino_vertex_constraints
C.constrain_dependent_leaf_edges_lengths()
constraint_dict = rhino_vertex_constraints(form)
print(constraint_dict)
C.update_rhino_vertex_constraints(constraint_dict)

print(len(C.constraints))

cj, cr = C.compute_constraints()
print(cj, cr)

# update force diagram
# TODO: if the move is too far, iterate? / display (Ricardo.. ignore this line)
from compas_ags.rhino import rhino_vertice_move
xy, force2 = rhino_vertice_move(force)

forceartist2 = ForceArtist(force2, layer='ForceDiagram2')
forceartist2.draw_diagram(form)

# -----------------HERE IS THE PROBLEM!!!!!!------------------------------------
formdata2 = rf.compute_form_from_force_newton_xfunc(form.to_data(), force.to_data(), xy, tol=1e5, cj=cj, cr=cr)
form2 = FormDiagram.from_data(formdata2)
# -----------------HERE IS THE PROBLEM!!!!!!------------------------------------


formartist2 = FormArtist(form2, layer='FormArtist2')
formartist2.draw_diagram()
