from compas.datastructures import Network
from compas.datastructures import FaceNetwork
from compas.topology import network_find_faces

import rhinoscriptsyntax as rs

guids = rs.ObjectsByLayer('Default')
lines = [[rs.CurveStartPoint(guid), rs.CurveEndPoint(guid)] for guid in guids]
network = Network.from_lines(lines)

face_network = FaceNetwork.from_data(network.to_data())
network_find_faces(face_network, breakpoints=face_network.leaves())

rs.EnableRedraw(False)
rs.DeleteObjects(rs.ObjectsByLayer('Dots'))
rs.CurrentLayer('Dots')

for key in face_network.vertices():
    A = face_network.vertex_area(key=key)
    network.vertex[key]['pz'] = A
    rs.AddTextDot('{0:.1f}'.format(A), network.vertex_coordinates(key))
    
rs.EnableRedraw(True)
rs.CurrentLayer('Default')

network.to_json('H:/data/grid_non_orthogonal.json')