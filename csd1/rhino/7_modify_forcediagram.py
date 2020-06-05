from compas_rhino import unload_modules
unload_modules("compas")

import os
import rhinoscriptsyntax as rs

from compas_ags.diagrams import FormDiagram
from compas_ags.diagrams import ForceDiagram

from compas_ags.rhino import FormArtist
from compas_ags.rhino import ForceArtist


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

# null-space ------------------------------------------------------------------
# compute null-space
rf = Proxy('compas_ags.ags2.rootfinding')
#nullspace = rf.compute_nullspace_xfunc(form.to_data(), force.to_data(), cj, cr)
#print('Dimension of null-space is %s' % len(nullspace))

# display null-soace
#from compas_ags.rhino import display_nullspace_rhino
#i = 0  
#display_nullspace_rhino(form, nullspace, i)
# =----------------------------------------------------------------------------

