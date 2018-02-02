from compas.datastructures import Network

import rhinoscriptsyntax as rs

guids = rs.ObjectsByLayer('Default')
lines = [[rs.CurveStartPoint(guid), rs.CurveEndPoint(guid)] for guid in guids]
network = Network.from_lines(lines)

network.to_json('C:/Users/al/Documents/GitHub/compas_ags/data/grid_cross.json')