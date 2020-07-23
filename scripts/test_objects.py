from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

import os

from compas.rpc import Proxy

from compas_ags.diagrams import FormGraph
from compas_ags.diagrams import FormDiagram
from compas_ags.diagrams import ForceDiagram

from compas_ags.rhino import FormObject

graphstatics = Proxy('compas_ags.ags.graphstatics')

HERE = os.path.dirname(__file__)
DATA = os.path.join(HERE, '../data')
FILE = os.path.join(DATA, 'debugging', 'truss.obj')

graph = FormGraph.from_obj(FILE)

form = FormDiagram.from_graph(graph)
force = ForceDiagram.from_formdiagram(form)

form.edge_force((0, 1), -1.0)
form.edge_force((2, 3), -1.0)
form.edge_force((4, 5), -1.0)

form.data = graphstatics.form_update_q_from_qind_proxy(form.data)
force.data = graphstatics.force_update_from_form_proxy(force.data, form.data)

formobject = FormObject(form, layer="AGS::FormDiagram")

formobject.artist.anchor_vertex = 9
formobject.artist.draw()
formobject.artist.redraw()

vertex = formobject.select_vertex()
print(vertex)

if formobject.move_vertex(vertex):
    formobject.artist.draw()
    formobject.artist.redraw()

formobject.unselect()

vertices = formobject.select_vertices()
print(vertices)

if formobject.move_vertices(vertices):
    formobject.artist.draw()
    formobject.artist.redraw()
