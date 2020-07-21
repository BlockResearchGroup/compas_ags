import os

from compas_ags.diagrams import FormGraph
from compas_ags.diagrams import FormDiagram
from compas_ags.diagrams import ForceDiagram
from compas_ags.rhino import FormArtist
from compas_ags.rhino import ForceArtist

from compas.rpc import Proxy

graphstatics = Proxy('compas_ags.ags.graphstatics')

HERE = os.path.dirname(__file__)
DATA = os.path.join(HERE, '../data')
FILE = os.path.join(DATA, 'paper', 'gs_form_force.obj')

graph = FormGraph.from_obj(FILE)

form = FormDiagram.from_graph(graph)
force = ForceDiagram.from_formdiagram(form)

form.edge_force(0, -30.0)

form.data = graphstatics.form_update_q_from_qind_proxy(form.data)
force.data = graphstatics.force_update_from_form_proxy(force.data, form.data)

left = list(form.vertices_where({'x': 0.0, 'y': 0.0}))[0]
right = list(form.vertices_where({'x': 6.0, 'y': 0.0}))[0]

formartist = FormArtist(form, layer="AGS::FormDiagram")
forceartist = ForceArtist(force, layer="AGS::ForceDiagram")

forceartist.anchor_vertex = 3
forceartist.anchor_point = [13, 0, 0]
forceartist.scale = 0.3

formartist.draw()
forceartist.draw()

formartist.redraw()
