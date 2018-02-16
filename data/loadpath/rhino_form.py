from compas_ags.diagrams import FormDiagram
from compas_rhino.helpers import NetworkArtist
from compas.utilities import geometric_key
from compas.utilities import XFunc

import rhinoscriptsyntax as rs
import json


# In

fnm = 'H:/data/loadpath/diagonal.json'
form = FormDiagram.from_json(fnm)

artist = NetworkArtist(form, layer='In')
artist.clear_layer()
artist.draw_vertices()
artist.draw_edges()

text = {}
for uv in form.edges():
    text[uv] = '{0:.2f}'.format(form.get_edge_attribute(uv, 'q'))
#artist.draw_edgelabels(text)

form.set_vertices_attributes(form.vertices(), {'z': 0})

rs.LayerVisible('In', False)

# Copy form

#rs.EnableRedraw(False)
#rs.CurrentLayer('Out')
#rs.DeleteObjects(rs.ObjectsByLayer('Out'))
#
#for uv in form.edges():
#    u, v = uv
#    q = form.get_edge_attribute(uv, 'q')
#    sp = form.vertex_coordinates(u)
#    ep = form.vertex_coordinates(v)
#    id = rs.AddLine(sp, ep)
#    rs.ObjectName(id, str(q))
#    
#rs.EnableRedraw(True)

# Analyse

#gkey_key = form.gkey_key()
#for guid in rs.ObjectsByLayer('Out'):
#    q = float(rs.ObjectName(guid))
#    xyz_sp = rs.CurveStartPoint(guid)
#    xyz_ep = rs.CurveEndPoint(guid)
#    gkey_sp = geometric_key(xyz_sp)
#    gkey_ep = geometric_key(xyz_ep)
#    u = gkey_key[gkey_sp]
#    v = gkey_key[gkey_ep]
#    try:
#        form.edge[u][v]['q'] = q
#    except:
#        form.edge[v][u]['q'] = q

# Analyse

#form = XFunc('compas_ags.ags.loadpath3.z_from_form')(form)
#artist = NetworkArtist(form, layer='Analysis')
#artist.clear_layer()
#artist.draw_vertices()
#artist.draw_edges()