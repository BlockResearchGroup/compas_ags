import rhinoscriptsyntax as rs
from compas_ags.diagrams import FormGraph
from compas_ags.diagrams import FormDiagram
from compas_ags.diagrams import ForceDiagram
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
guids = compas_rhino.select_lines(message='Loaded Edges')
lines = compas_rhino.get_line_coordinates(guids)
force_value = rs.GetReal("Force on Edges", 1.0)
force_point = rs.GetPoint("Set Force Diagram Location")

gkey_key = form.gkey_key()
uv_i = form.uv_index()
print(uv_i)
print(gkey_key)
for p1,p2 in lines:
    u = gkey_key[geometric_key(p1)]
    v = gkey_key[geometric_key(p2)]
    print(u,v)
    try:
        index = uv_i[(u, v)]
        uv = (u, v)
    except:
        index = uv_i[(v, u)]
        vu = (v, u)
    print(index)
    form.set_edge_force_by_index(index, force_value)

# set the fixed branch and anchor of force diagram
form.set_fixed([0,1])
force.set_anchor([0])
force.vertex_attribute(0, 'x', force_point[0])  # can ask for user to input a location
force.vertex_attribute(0, 'y', force_point[1])
    
# update diagrams
form_data = graphstatics.form_update_q_from_qind_rhino(form.to_data())
force_data = graphstatics.force_update_from_form_rhino(force.to_data(), form_data)
form = FormDiagram.from_data(form_data)
force = ForceDiagram.from_data(force_data)


formartist = MeshArtist(form, layer='FormDiagram')
formartist.clear()
formartist.draw_mesh()
formartist.draw_faces()
formartist.draw_vertices()
formartist.draw_edges()
formartist.draw_vertexlabels()
formartist.draw_edgelabels()
formartist.draw_facelabels()


forceartist = MeshArtist(force, layer='ForceDiagram')
forceartist.clear()
forceartist.draw_mesh()
forceartist.draw_faces()
forceartist.draw_vertices()
forceartist.draw_edges()
forceartist.draw_vertexlabels()
forceartist.draw_edgelabels()
forceartist.draw_facelabels()

print('Done')