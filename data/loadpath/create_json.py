
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


# Form

guids = rs.ObjectsByLayer('Lines') + rs.ObjectsByLayer('Symmetry')
lines = [[rs.CurveStartPoint(i), rs.CurveEndPoint(i)] for i in guids if rs.IsCurve(i)]

form = FormDiagram.from_lines(lines)
form.update_default_vertex_attributes({'is_roller': False})
form.update_default_edge_attributes({'is_symmetry': False})
form.attributes['loadpath'] = 0
form.attributes['indset'] = ''

gkey_key = form.gkey_key()

# FaceNetwork

face_network = FaceNetwork.from_data(form.to_data())
#network_find_faces(face_network, breakpoints=face_network.leaves())
network_find_faces(face_network)
face_network.delete_face(0)

# Pins

for i in rs.ObjectsByLayer('Pins'):
    gkey = geometric_key(rs.PointCoordinates(i))
    form.set_vertex_attributes(gkey_key[gkey], {'is_fixed': True})
    
# Rollers

for i in rs.ObjectsByLayer('Rollers'):
    gkey = geometric_key(rs.PointCoordinates(i))
    form.set_vertex_attributes(gkey_key[gkey], {'is_roller': True})

# Loads

for key in form.vertices():
    form.vertex[key]['pz'] = face_network.vertex_area(key=key)
    
# Constraints

for i in rs.ObjectsByLayer('Lower'):
    gkey = geometric_key(rs.PointCoordinates(i))
    form.set_vertex_attributes(gkey_key[gkey], {'lb': float(rs.ObjectName(i))})
    
for i in rs.ObjectsByLayer('Upper'):
    gkey = geometric_key(rs.PointCoordinates(i))
    form.set_vertex_attributes(gkey_key[gkey], {'ub': float(rs.ObjectName(i))})
    
# Symmetry

for i in rs.ObjectsByLayer('Symmetry'):
    if rs.IsCurve(i):
        u = gkey_key[geometric_key(rs.CurveStartPoint(i))]
        v = gkey_key[geometric_key(rs.CurveEndPoint(i))]
        form.set_edge_attribute((u, v), name='is_symmetry', value=True, directed=False)
    elif rs.IsPoint(i):
        key = gkey_key[geometric_key(rs.PointCoordinates(i))]
        form.vertex[key]['pz'] = float(rs.ObjectName(i))

# TextDots

rs.EnableRedraw(False)
rs.DeleteObjects(rs.ObjectsByLayer('Dots'))
rs.CurrentLayer('Dots')

pzt = 0
for key in form.vertices():
    pz = form.vertex[key].get('pz', 0)
    pzt += pz
    if pz:
        rs.AddTextDot('{0:.2f}'.format(pz), form.vertex_coordinates(key))
print('Total load: {0}'.format(pzt))

rs.EnableRedraw(True)
rs.CurrentLayer('Lines')
rs.LayerVisible('Dots', False)

# Save

form.to_json('F:/compas_ags/data/loadpath/diagonal.json')
