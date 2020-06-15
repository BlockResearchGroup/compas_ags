from compas.rpc import Proxy
from compas_ags.rhino import move_force_vertice
from compas_ags.rhino import ForceArtist
from compas_ags.rhino import FormArtist
from compas_ags.diagrams import ForceDiagram
from compas_ags.diagrams import FormDiagram
import compas_rhino
import rhinoscriptsyntax as rs
import os
from compas_rhino import unload_modules
unload_modules("compas")


rf = Proxy('compas_ags.ags2.rootfinding')

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
forceartist = ForceArtist(force, layer='ForceDiagram')

formartist.draw_diagram()
formartist.draw_independent_edge()
formartist.draw_fixed_vertice()

forceartist.draw_diagram(form=form)
forceartist.draw_independent_edges(form)
forceartist.draw_edge_force()
forceartist.draw_anchor_vertex()


# ==============================================================================
# Modify Forcediagram
# ==============================================================================
# set constraints
from compas_ags.constraints import ConstraintsCollection
C = ConstraintsCollection(form)

# set vertex constraints
#from compas_ags.rhino import rhino_vertex_constraints
C.constrain_dependent_leaf_edges_lengths()

from compas_ags.rhino import rhino_constraint_visualization
constraint_dict = rhino_constraint_visualization(form, scale=1)
C.update_rhino_vertex_constraints(constraint_dict)


cj, cr = C.compute_constraints()

# compute null-space
nullspace = rf.compute_nullspace_xfunc(form.to_data(), force.to_data(), cj, cr)
print('Dimension of null-space is %s' % len(nullspace))


from compas_ags.rhino import move_force_vertice
xy, force = move_force_vertice(force, forceartist)

forceartist.draw_diagram(form=form)
forceartist.draw_independent_edges(form)


# ==============================================================================
# Update Formdiagram
# ==============================================================================
formdata = rf.compute_form_from_force_newton_xfunc(form.to_data(), force.to_data(), xy, tol=1e5, cj=cj, cr=cr)
form = FormDiagram.from_data(formdata)
formartist = FormArtist(form, layer='FormDiagram')
formartist.draw_diagram()




# ==============================================================================
# Save data
# ==============================================================================
#form.to_json(form_file)
#force.to_json(force_file)
