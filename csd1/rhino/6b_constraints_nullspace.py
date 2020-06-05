from compas_rhino import unload_modules
unload_modules("compas")

import os
import rhinoscriptsyntax as rs

from compas_ags.diagrams import FormDiagram
from compas_ags.diagrams import ForceDiagram

from compas_ags.rhino import FormArtist
from compas_ags.rhino import ForceArtist

from compas_ags.constraints import ConstraintsCollection
from compas_ags.rhino import rhino_vertex_constraints

from compas.rpc import Proxy
from compas_ags.rhino import display_nullspace_rhino

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
C = ConstraintsCollection(form)

# set vertex constraints
C.constrain_dependent_leaf_edges_lengths()
constraint_dict = rhino_vertex_constraints(form)
C.update_rhino_vertex_constraints(constraint_dict)

cj, cr = C.compute_constraints()
print(cj, cr)


# ==============================================================================
# Null Space
# ==============================================================================
rf = Proxy('compas_ags.ags2.rootfinding')
nullspace = rf.compute_nullspace_xfunc(form.to_data(), force.to_data(), cj, cr)
print('Dimension of null-space is %s' % len(nullspace))

# display null-soace
from compas_ags.rhino import display_nullspace_rhino
i = 1  # input the index of null-space 
display_nullspace_rhino(form, nullspace, i)

