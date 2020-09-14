import os

from compas_ags.diagrams import FormGraph
from compas_ags.diagrams import FormDiagram
from compas.rpc import Proxy

HERE = os.path.dirname(__file__)
FILE = os.path.join(HERE, '../data/paper/gs_form_force.obj')

graphstatics = Proxy('compas_ags.ags.graphstatics')

graph = FormGraph.from_obj(FILE)
form = FormDiagram.from_graph(graph)

dof = graphstatics.form_count_dof(form)

print(dof)
