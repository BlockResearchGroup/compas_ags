import os

from compas_ags.diagrams import FormGraph
from compas_ags.diagrams import ForceDiagram
from compas_ags.diagrams import FormDiagram
from compas.rpc import Proxy

HERE = os.path.dirname(__file__)
FILE = os.path.join(HERE, '../data/paper/gs_form_force.obj')

graph = FormGraph.from_obj(FILE)
form = FormDiagram.from_graph(graph)
force = ForceDiagram.from_formdiagram(form)

loadpath = Proxy('compas_ags.ags.loadpath')

lp = loadpath.compute_loadpath(form, force)

print(lp)
