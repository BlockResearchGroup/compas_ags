from compas_rhino import unload_modules
unload_modules("compas")

import rhinoscriptsyntax as rs
from compas_ags.diagrams import FormGraph
from compas_ags.diagrams import FormDiagram
from compas_ags.diagrams import ForceDiagram
from compas_ags.rhino import FormArtist
from compas_ags.rhino import ForceArtist
from compas.utilities import geometric_key
import compas_rhino
from compas_rhino.artists import MeshArtist
import math



from compas.rpc import Proxy
graphstatics = Proxy('compas_ags.ags.graphstatics')

# Select lines in rhino
guids = compas_rhino.select_lines(message='Form Diagram lines')
lines = compas_rhino.get_line_coordinates(guids)
graph = FormGraph.from_lines(lines)
print(lines)

# create form and force
form = FormDiagram.from_graph(graph)
force = ForceDiagram.from_formdiagram(form)

# set independent edge and force
from compas_ags.rhino import select_loaded_edges
index, uv = select_loaded_edges(form)
force_value = rs.GetReal("Force on Edges", 1.0)

form.set_edge_force_by_index(index, force_value)


# set the fixed branch and anchor of force diagram
#fixed = 
#form.set_fixed([0,1])


from compas_ags.rhino import select_forcediagram_location
select_forcediagram_location(force)

# update diagrams
form_data = graphstatics.form_update_q_from_qind_rhino(form.to_data())
force_data = graphstatics.force_update_from_form_rhino(force.to_data(), form_data)
form = FormDiagram.from_data(form_data)
force = ForceDiagram.from_data(force_data)


# display

formartist = FormArtist(form, layer='FormDiagram')
forceartist = ForceArtist(force, layer='ForceDiagram')

#formartist.clear()
#formartist.draw_mesh()
#formartist.draw_faces()
#formartist.draw_vertices()
#formartist.draw_edges()
#formartist.draw_vertexlabels()
#formartist.draw_edgelabels()
#formartist.draw_facelabels()
#
#forceartist.clear()
#forceartist.draw_mesh()
#forceartist.draw_faces()
#forceartist.draw_vertices()
#forceartist.draw_edges()
#forceartist.draw_vertexlabels()
#forceartist.draw_edgelabels()


## draw dual form faces and force vertices ------------------------------------
#from compas_ags.rhino import draw_dual_form_faces_force_vertices
#draw_dual_form_faces_force_vertices(form, force, formartist, forceartist)


## draw dual force faces and form non-leaf vertices ---------------------------
#from compas_ags.rhino import draw_dual_form_vertices_force_faces
#draw_dual_form_vertices_force_faces(form, force, formartist, forceartist)


# draw dual force faces and form non-leaf vertices ----------------------------
from compas_ags.rhino import draw_dual_edges
draw_dual_edges(form, force, formartist, forceartist)

# show the force in an edge ---------------------------------------------------
forceartist.draw_edge_force()

# draw independent edges ------------------------------------------------------
formartist.draw_independent_edge()
forceartist.draw_independent_edges(form)


# select constraints in the form diagram
formartist.draw_vertices()
formartist.draw_vertexlabels()
forceartist.draw_vertices()



# =============================================================================


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
nullspace = rf.compute_nullspace_xfunc(form.to_data(), force.to_data(), cj, cr)
print('Dimension of null-space is %s' % len(nullspace))

## display null-soace
#from compas_ags.rhino import display_nullspace_rhino
#i = 0  
#display_nullspace_rhino(form, nullspace, i)
# =----------------------------------------------------------------------------


# update force diagram
from compas_ags.rhino import rhino_vertice_move
xy, force2 = rhino_vertice_move(force)
print(xy, 'xy')

# TODO: if the move is too far, iterate? / display

forceartist2 = ForceArtist(force2, layer='ForceDiagram2')
forceartist2.draw_vertices()
forceartist2.draw_edges()
forceartist2.draw_edge_force()
forceartist2.draw_independent_edges(form)

formdata2 = rf.compute_form_from_force_newton_xfunc(form.to_data(), force.to_data(), xy, tol=1e5, cj=cj, cr=cr)
print(formdata2)
form2 = FormDiagram.from_data(formdata2)

formartist2 = FormArtist(form2, layer='FormArtist2')
formartist2.draw_vertices()
formartist2.draw_edges()

print('Done')
