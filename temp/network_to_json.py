from compas.datastructures import Network
from compas.datastructures import FaceNetwork
from compas.topology import network_find_faces

import rhinoscriptsyntax as rs

guids = rs.ObjectsByLayer('Default')
lines = [[rs.CurveStartPoint(guid), rs.CurveEndPoint(guid)] for guid in guids]
network = Network.from_lines(lines)
k_i = network.key_index()

face_network = FaceNetwork.from_data(network.to_data())
network_find_faces(face_network, breakpoints=face_network.leaves())

rs.EnableRedraw(False)
rs.DeleteObjects(rs.ObjectsByLayer('Dots'))

for key in network.vertices():
    xyz = network.vertex_coordinates(key)
    rs.CurrentLayer('Dots')
    A = face_network.vertex_area(key=key)
    network.vertex[key]['pz'] = A
    rs.AddTextDot('{0:.1f}'.format(A), xyz)
    
rs.EnableRedraw(True)
rs.CurrentLayer('Default')

network.to_json('H:/data/fan.json')
