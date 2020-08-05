import compas_ags

from compas_ags.diagrams import FormGraph
from compas_ags.diagrams import FormDiagram
from compas_ags.diagrams import ForceDiagram

FILE = compas_ags.get('debugging/zero.obj')

graph = FormGraph.from_obj(FILE)
form = FormDiagram.from_graph(graph)
force = ForceDiagram.from_formdiagram(form)

for edge in force.edges_where_dual({'is_external': True}):
    dual_edge = force.dual_edge(edge)
    print(edge, (form.halfedge[dual_edge[0]][dual_edge[1]], form.halfedge[dual_edge[1]][dual_edge[0]]))
