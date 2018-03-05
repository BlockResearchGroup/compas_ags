
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from compas.datastructures import Network
from compas.datastructures import FaceNetwork
from compas.topology import network_find_faces
from compas.utilities import geometric_key

import rhinoscriptsyntax as rs


__author__    = ['Andrew Liew <liew@arch.ethz.ch>']
__copyright__ = 'Copyright 2018, BLOCK Research Group - ETH Zurich'
__license__   = 'MIT License'
__email__     = 'liew@arch.ethz.ch'


# Networks

guids = rs.ObjectsByLayer('Lines')
suids = rs.ObjectsByLayer('Symmetry')
lines = [[rs.CurveStartPoint(guid), rs.CurveEndPoint(guid)] for guid in guids]
lines.extend([[rs.CurveStartPoint(suid), rs.CurveEndPoint(suid)] for suid in suids if rs.IsCurve(suid)])
network = Network.from_lines(lines)
face_network = FaceNetwork.from_data(network.to_data())
#network_find_faces(face_network, breakpoints=face_network.leaves())
network_find_faces(face_network)
face_network.delete_face(0)

# Pins

network.update_default_vertex_attributes({'is_fixed': False})
gkey_key = network.gkey_key()
for guid in rs.ObjectsByLayer('Pins'):
    gkey = geometric_key(rs.PointCoordinates(guid))
    network.set_vertex_attributes(gkey_key[gkey], {'is_fixed': True})

# Loads

rs.EnableRedraw(False)
rs.DeleteObjects(rs.ObjectsByLayer('Dots'))
rs.CurrentLayer('Dots')

At = 0
for key in network.vertices():
    A = face_network.vertex_area(key=key)
    At += A
    network.vertex[key]['pz'] = A
    rs.AddTextDot('{0:.3f}'.format(A), network.vertex_coordinates(key)) 
print('Total load: {0}'.format(At))

# Symmetry

for suid in rs.ObjectsByLayer('Symmetry'):
    if rs.IsCurve(suid):
        u = gkey_key[geometric_key(rs.CurveStartPoint(suid))]
        v = gkey_key[geometric_key(rs.CurveEndPoint(suid))]
        try:
            network.edge[u][v]['is_symmetry'] = True
        except:
            network.edge[v][u]['is_symmetry'] = True
    elif rs.IsPoint(suid):
        pz = float(rs.ObjectName(suid))
        network.vertex[gkey_key[geometric_key(rs.PointCoordinates(suid))]]['pz'] = pz
    
rs.EnableRedraw(True)
rs.CurrentLayer('Lines')

# Save

network.to_json('H:/data/loadpath/star.json')
