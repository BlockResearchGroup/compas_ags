
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from compas_ags.diagrams import FormDiagram
from compas.datastructures import FaceNetwork
from compas.topology import network_find_faces
from compas.utilities import geometric_key

import rhinoscriptsyntax as rs


__author__    = ['Andrew Liew <liew@arch.ethz.ch>']
__copyright__ = 'Copyright 2018, BLOCK Research Group - ETH Zurich'
__license__   = 'MIT License'
__email__     = 'liew@arch.ethz.ch'


# Network

guids = rs.ObjectsByLayer('Lines')
suids = rs.ObjectsByLayer('Symmetry')
lines = [[rs.CurveStartPoint(i), rs.CurveEndPoint(i)] for i in guids]
symmetry = [[rs.CurveStartPoint(i), rs.CurveEndPoint(i)] for i in suids if rs.IsCurve(i)]
network = FormDiagram.from_lines(lines + symmetry)
gkey_key = network.gkey_key()
network.update_default_edge_attributes({'is_symmetry': False})
network.attributes['loadpath'] = 0

# FaceNetwork

face_network = FaceNetwork.from_data(network.to_data())
#network_find_faces(face_network, breakpoints=face_network.leaves())
network_find_faces(face_network)
face_network.delete_face(0)

# Pins

network.update_default_vertex_attributes({'p': 0})
for guid in rs.ObjectsByLayer('Pins'):
    gkey = geometric_key(rs.PointCoordinates(guid))
    network.set_vertex_attributes(gkey_key[gkey], {'is_fixed': True})

# Loads

for key in network.vertices():
    network.vertex[key]['pz'] = face_network.vertex_area(key=key)
    
# Symmetry

for i in rs.ObjectsByLayer('Symmetry'):
    if rs.IsCurve(i):
        u = gkey_key[geometric_key(rs.CurveStartPoint(i))]
        v = gkey_key[geometric_key(rs.CurveEndPoint(i))]
        try:
            network.edge[u][v]['is_symmetry'] = True
        except:
            network.edge[v][u]['is_symmetry'] = True
    elif rs.IsPoint(i):
        pz = float(rs.ObjectName(i))
        key = gkey_key[geometric_key(rs.PointCoordinates(i))]
        network.vertex[key]['pz'] = pz

# TextDots

rs.EnableRedraw(False)
rs.DeleteObjects(rs.ObjectsByLayer('Dots'))
rs.CurrentLayer('Dots')

pzt = 0
for key in network.vertices():
    pz = network.vertex[key].get('pz', None)
    if pz:
        pzt += pz
        rs.AddTextDot('{0:.3f}'.format(pz), network.vertex_coordinates(key))
print('Total load: {0}'.format(pzt))

rs.EnableRedraw(True)
rs.CurrentLayer('Lines')
rs.LayerVisible('Dots', False)

# Save

network.to_json('F:/compas_ags/data/loadpath/plus.json')
