import compas_ags

from compas_ags.diagrams import FormGraph
from compas_ags.diagrams import FormDiagram
from compas_ags.ags import graphstatics
from compas.rpc import Proxy

graphstatics = Proxy('compas_ags.ags.graphstatics')

graph = FormGraph.from_obj(compas_ags.get('paper/gs_form_force.obj'))
form = FormDiagram.from_graph(graph)

dof = graphstatics.form_count_dof_proxy(form.data)

print(dof)
