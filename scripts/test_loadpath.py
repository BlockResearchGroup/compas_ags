import compas_ags

from compas_ags.diagrams import FormGraph
from compas_ags.diagrams import ForceDiagram
from compas_ags.diagrams import FormDiagram
from compas.rpc import Proxy

#graphstatics = Proxy('compas_ags.ags.graphstatics')

graph = FormGraph.from_obj(compas_ags.get('paper/gs_form_force.obj'))
form = FormDiagram.from_graph(graph)
force = ForceDiagram.from_formdiagram(form)

loadpath = Proxy('compas_ags.ags.loadpath')
#dof = graphstatics.form_count_dof_proxy(form.data)
lp = loadpath.compute_loadpath_proxy(form.data, force.data)
print(lp)
#print(dof)
