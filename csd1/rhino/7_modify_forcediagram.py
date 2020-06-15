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
forceartist.draw_anchor_vertex()


# ==============================================================================
# Constraints
# ==============================================================================


# set constraints
from compas_ags.constraints import ConstraintsCollection
C = ConstraintsCollection(form)

# set vertex constraints
#from compas_ags.rhino import rhino_vertex_constraints
C.constrain_dependent_leaf_edges_lengths()
 
#constraint_dict = rhino_vertex_constraints(form)
from compas_ags.rhino import rhino_constraint_visualization
constraint_dict = rhino_constraint_visualization(form, scale=0.5)
print(constraint_dict) 
C.update_rhino_vertex_constraints(constraint_dict)


cj, cr = C.compute_constraints()



## compute null-space
#nullspace = rf.compute_nullspace_xfunc(form.to_data(), force.to_data(), cj, cr)
#print('Dimension of null-space is %s' % len(nullspace))

# update force diagram
# TODO: if the move is too far, iterate? / display (Ricardo.. ignore this line)
#from compas_ags.rhino import rhino_vertice_move
#xy, force2 = rhino_vertice_move(force)
from compas_ags.rhino import move_force_vertice
xy, force2 = move_force_vertice(force, forceartist)

# update form diagram
forceartist2 = ForceArtist(force2, layer='ForceDiagram2')
forceartist2.draw_diagram(form)

# update force diagram
formdata2 = rf.compute_form_from_force_newton_xfunc(form.to_data(), force.to_data(), xy, tol=1e5, cj=cj, cr=cr)
form2 = FormDiagram.from_data(formdata2)
formartist2 = FormArtist(form2, layer='FormDiagram2')
formartist2.draw_diagram()

print('success!')