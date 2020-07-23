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
FILE = os.path.join(DATA, 'debugging', 'truss.obj')

graph = FormGraph.from_obj(FILE)

form = FormDiagram.from_graph(graph)
force = ForceDiagram.from_formdiagram(form)

form.edge_force((0, 1), -1.0)
form.edge_force((2, 3), -1.0)
form.edge_force((4, 5), -1.0)

form.data = graphstatics.form_update_q_from_qind_proxy(form.data)
force.data = graphstatics.force_update_from_form_proxy(force.data, form.data)

formartist = FormArtist(form, layer="AGS::FormDiagram")
forceartist = ForceArtist(force, layer="AGS::ForceDiagram")

formartist.anchor_vertex = 9

forceartist.anchor_vertex = 5
forceartist.anchor_point = [35, 0, 0]
forceartist.scale = 5.0

formartist.settings['show.forces'] = True

formartist.draw()
forceartist.draw()

formartist.redraw()
