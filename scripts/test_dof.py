import compas_ags

from compas_ags.diagrams import FormGraph
from compas_ags.diagrams import FormDiagram
# from compas_ags.ags import graphstatics
from compas.rpc import Proxy

proxy = Proxy()
proxy.start_server()
proxy.stop_server()

graphstatics = Proxy('compas_ags.ags.graphstatics')

path = '/Users/mricardo/compas_dev/compas_ags/data/paper/gs_form_force.obj'

graph = FormGraph.from_obj(path)
form = FormDiagram.from_graph(graph)

dof = graphstatics.form_count_dof_proxy(form.data)

print(dof)
