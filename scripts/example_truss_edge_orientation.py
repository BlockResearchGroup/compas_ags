import compas_ags
from compas_ags.diagrams import FormGraph
from compas_ags.diagrams import FormDiagram
from compas_ags.diagrams import ForceDiagram
from compas_ags.viewers import Viewer
from compas_ags.ags import form_update_from_force
from compas_ags.ags import form_update_q_from_qind
from compas_ags.ags import force_update_from_form
from compas_ags.ags import ConstraintsCollection
from compas_ags.ags import form_update_from_force_newton
from compas_ags.ags import form_update_from_force

# ------------------------------------------------------------------------------
#   1. create a simple arch from nodes and edges, make form and force diagrams
# ------------------------------------------------------------------------------

graph = FormGraph.from_obj(compas_ags.get('paper/gs_truss.obj'))
form = FormDiagram.from_graph(graph)
force = ForceDiagram.from_formdiagram(form)

# ------------------------------------------------------------------------------
#   2. prescribe edge force density and set fixed vertices
# ------------------------------------------------------------------------------
# prescribe force density to edge
edges_ind = [
    (6, 14),
]
for index in edges_ind:
    u, v = index
    form.edge_attribute((u, v), 'is_ind', True)
    form.edge_attribute((u, v), 'q', +1.)

# set the fixed corners
left = 5
right = 1
fixed = [left, right]

for key in fixed:
    form.vertex_attribute(key, 'is_fixed', True)

# set the horizontal fix in internal nodes:
internal = [0, 2, 3, 4]

for key in internal:
    form.vertex_attribute(key, 'fix_x', True)

# update the diagrams
form_update_q_from_qind(form)
force_update_from_form(force, form)

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

viewer = Viewer(form, force, delay_setup=False)
viewer.draw_form(vertexlabel={key: key for key in form.vertices()})
viewer.draw_force(vertexlabel={key: key for key in force.vertices()})
viewer.show()

# --------------------------------------------------------------------------
#   3. force diagram manipulation and modify the form diagram
# --------------------------------------------------------------------------

# modify the geometry of the force diagram moving nodes further at right to the left
move_vertices = [6, 7, 8, 9, 10]
translation = +2.0
for key in move_vertices:
    x0 = force.vertex_attribute(key, 'x')
    force.vertex_attribute(key, 'x', x0 + translation)

# set constraints automatically with the form diagram's attributes
C = ConstraintsCollection(form)
C.constraints_from_form()

# form_update_from_force_newton(form, force, constraints=C)
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
