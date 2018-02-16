from compas.datastructures import Network
from compas.datastructures import FaceNetwork
from compas.topology import network_find_faces
from compas.utilities import geometric_key

import rhinoscriptsyntax as rs

# Clear

rs.EnableRedraw(False)
rs.DeleteObjects(rs.ObjectsByLayer('Dots'))

# Networks

guids = rs.ObjectsByLayer('Lines')
lines = [[rs.CurveStartPoint(guid), rs.CurveEndPoint(guid)] for guid in guids]
network = Network.from_lines(lines)
face_network = FaceNetwork.from_data(network.to_data())
network_find_faces(face_network, breakpoints=face_network.leaves())

# Pins

network.update_default_vertex_attributes({'is_fixed': False})
gkey_key = network.gkey_key()
for guid in rs.ObjectsByLayer('Pins'):
    gkey = geometric_key(rs.PointCoordinates(guid))
    network.set_vertex_attributes(gkey_key[gkey], {'is_fixed': True})

# Loads

rs.CurrentLayer('Dots')
for key in network.vertices():
    xyz = network.vertex_coordinates(key)
    A = face_network.vertex_area(key=key)
    A = 1.
    network.vertex[key]['pz'] = A
    rs.AddTextDot('{0:.1f}'.format(A), xyz) 

# Return

rs.EnableRedraw(True)
rs.CurrentLayer('Lines')

# Save

network.to_json('H:/data/loadpath/diagonal.json')
