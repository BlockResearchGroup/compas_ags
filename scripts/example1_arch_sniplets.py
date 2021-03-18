import compas_ags
from compas_ags.diagrams import FormGraph
from compas_ags.diagrams import FormDiagram
from compas_ags.diagrams import ForceDiagram
from compas_ags.ags import form_update_from_force
from compas_ags.ags import ConstraintsCollection
from compas_ags.ags import form_update_from_force


# Sniplets syle



# ------------------------------------------------------------------------------
#   1. create a simple arch from nodes and edges and visualise
# ------------------------------------------------------------------------------

from compas_ags.diagrams import FormGraph
from compas_ags.diagrams import FormDiagram
from compas_ags.viewers import Viewer

graph = FormGraph.from_json(compas_ags.get('paper/gs_arch.json'))
form = FormDiagram.from_graph(graph)

# viewer = Viewer(form)
# viewer.draw_form(vertexlabel={key: key for key in form.vertices()},
#                 vertexsize=0.2)
# viewer.show()

# ------------------------------------------------------------------------------
#   2. prescribe edge force density to independent edge
# ------------------------------------------------------------------------------

edges_ind = [
    (10, 0),
]
for index in edges_ind:
    u, v = index
    form.edge_attribute((u, v), 'is_ind', True)
    form.edge_attribute((u, v), 'q', -1.0)


# ------------------------------------------------------------------------------
#   3. create force diagram and compute equilibrium
# ------------------------------------------------------------------------------

from compas_ags.ags import form_update_q_from_qind
from compas_ags.ags import force_update_from_form


# create a dual force diagram
force = ForceDiagram.from_formdiagram(form)

# update the diagrams
form_update_q_from_qind(form)
force_update_from_form(force, form)
force_update_from_form(force, form)

viewer = Viewer(form, force, delay_setup=False)
viewer.draw_form(vertexlabel={key: key for key in form.vertices()},
                 edgelabel={uv: index for index, uv in enumerate(form.edges())},
                 vertexsize=0.2,
                 forces_on=True,
                 forcescale=0.5)
viewer.draw_force(edgelabel={uv: index for index, uv in enumerate(force.edges())})
viewer.show()

# store lines representing the current state of equilibrium
form_lines = []
for u, v in form.edges():
    form_lines.append({
        'start': form.vertex_coordinates(u, 'xy'),
        'end': form.vertex_coordinates(v, 'xy'),
        'width': 1.0,
        'color': '#cccccc',
        'style': '--'
    })

force_lines = []
for u, v in force.edges():
    force_lines.append({
        'start': force.vertex_coordinates(u, 'xy'),
        'end': force.vertex_coordinates(v, 'xy'),
        'width': 1.0,
        'color': '#cccccc',
        'style': '--'
    })

# --------------------------------------------------------------------------
#   3. force diagram manipulation and modify the form diagram
# --------------------------------------------------------------------------

# modify the geometry of the force diagram moving nodes further at right to the left
move_vertices = [0, 9, 8]
translation = +1.0
for key in move_vertices:
    x0 = force.vertex_attribute(key, 'x')
    force.vertex_attribute(key, 'x', x0 + translation)

form_update_from_force(form, force)

# ------------------------------------------------------------------------------
#   4. display the orginal configuration
#      and the configuration after modifying the force diagram
# ------------------------------------------------------------------------------
viewer = Viewer(form, force, delay_setup=False)

viewer.draw_form(lines=form_lines,
                 forces_on=True,
                 vertexlabel={key: key for key in form.vertices()},
                 external_on=False,
                 vertexsize=0.2,
                 vertexcolor={key: '#000000' for key in fixed},
                 edgelabel={uv: index for index, uv in enumerate(form.edges())}
                 )

viewer.draw_force(lines=force_lines,
                  vertexlabel={key: key for key in force.vertices()},
                  vertexsize=0.2,
                  edgelabel={uv: index for index, uv in enumerate(force.edges())}
                  )

viewer.show()
