import compas
import compas_ags

from compas_ags.diagrams import FormGraph
from compas_ags.diagrams import FormDiagram
from compas_ags.diagrams import ForceDiagram
from compas_ags.ags import graphstatics

from compas_ags.viewers import Viewer

graph = FormGraph.from_obj(compas_ags.get('paper/fink.obj'))
form = FormDiagram.from_graph(graph)
force = ForceDiagram.from_formdiagram(form)

lines = []
for u, v in form.edges():
    lines.append({
        'start': form.vertex_coordinates(u),
        'end': form.vertex_coordinates(v),
        'color': '#cccccc',
        'width': 0.5,
    })

form.identify_fixed()

viewer = Viewer(form, force, delay_setup=False, figsize=(9, 6))

viewer.draw_form()
viewer.draw_force()
viewer.show()
