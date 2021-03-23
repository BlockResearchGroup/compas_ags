import compas_ags
from compas_ags.diagrams import FormGraph
from compas_ags.diagrams import FormDiagram
from compas_ags.diagrams import ForceDiagram


# Sniplets syle

# ------------------------------------------------------------------------------
#   1. create a simple arch from nodes and edges and visualise
# ------------------------------------------------------------------------------

from compas_ags.diagrams import FormGraph
from compas_ags.diagrams import FormDiagram
from compas_ags.viewers import Viewer

graph = FormGraph.from_obj(compas_ags.get('paper/ex1_arch.obj'))
form = FormDiagram.from_graph(graph)

# viewer = Viewer(form)
# viewer.draw_form(vertexlabel={key: key for key in form.vertices()},
#                 vertexsize=0.2)
# viewer.show()

# ------------------------------------------------------------------------------
#   2. prescribe edge force density to independent edge
# ------------------------------------------------------------------------------

edges_ind = [
    (1, 8),
]
for index in edges_ind:
    u, v = index
    form.edge_attribute((u, v), 'is_ind', True)
    form.edge_attribute((u, v), 'q', -1.0)

# fix_vertices = [0 , 7]
# for key in fix_vertices:
#     form.vertex_attribute(key, 'is_fixed', True)

# ------------------------------------------------------------------------------
#   3. create force diagram and compute equilibrium
# ------------------------------------------------------------------------------

from compas_ags.diagrams import ForceDiagram
from compas_ags.ags import form_update_q_from_qind
from compas_ags.ags import force_update_from_form

# create a dual force diagram
force = ForceDiagram.from_formdiagram(form)

# update the diagrams
form_update_q_from_qind(form)
force_update_from_form(force, form)
force_update_from_form(force, form)


force_edges = force.ordered_edges(form)

force_edge_labels1 = {(u, v): index for index, (u, v) in enumerate(force_edges)}
force_edge_labels2 = {(v, u): index for index, (u, v) in enumerate(force_edges)}
force_edge_labels = {**force_edge_labels1, **force_edge_labels2}

# viewer = Viewer(form, force, delay_setup=False)
# viewer.draw_form(vertexlabel={key: key for key in form.vertices()},
#                  edgelabel={uv: index for index, uv in enumerate(form.edges())},
#                  vertexsize=0.2,
#                  forces_on=True)
# viewer.draw_force(vertexlabel={key: key for key in force.vertices()},
#                   vertexsize=0.2,
#                   edgelabel=force_edge_labels)
# viewer.show()

# viewer = Viewer(form, force, delay_setup=False)
# viewer.draw_form(vertexlabel={key: key for key in form.vertices()},
#                  edgelabel={(u, v): form.edge_length(u, v) for u, v in form.edges()},
#                  vertexsize=0.2,
#                  forces_on=True)
# viewer.draw_force(vertexlabel={key: key for key in force.vertices()},
#                   vertexsize=0.2,
#                   edgelabel={(u, v): force.edge_length(u, v) for u, v in force.edges()})
# viewer.show()

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
#   4. Set default constraints based on the direction of the external loads
# --------------------------------------------------------------------------

# Identify auto constraints
form.identify_constraints()

# Reflect all constraints to force diagram
force.constraints_from_dual()

# --------------------------------------------------------------------------
#   5. force diagram manipulation and modify the form diagram
# --------------------------------------------------------------------------

from compas_ags.ags import form_update_from_force

# modify the geometry of the force diagram moving nodes further at right to the left
move_vertices = [0, 9, 8]
translation = +1.0
for key in move_vertices:
    x0 = force.vertex_attribute(key, 'x')
    force.vertex_attribute(key, 'x', x0 + translation)

form_update_from_force(form, force)

viewer = Viewer(form, force, delay_setup=False)

viewer.draw_form(lines=form_lines,
                 forces_on=True,
                 vertexlabel={key: key for key in form.vertices()},
                 external_on=True,
                 vertexsize=0.2,
                 edgelabel={uv: index for index, uv in enumerate(form.edges())}
                 )

viewer.draw_force(lines=force_lines,
                  vertexlabel={key: key for key in force.vertices()},
                  vertexsize=0.2,
                  edgelabel=force_edge_labels
                  )

viewer.show()

# --------------------------------------------------------------------------
#   6. Assign target length to hor. reaction forces = 6.0 kN
# --------------------------------------------------------------------------

from compas_ags.ags import force_update_from_constraints

# fix force of edges 1, 15 force fixed:
index_edges_constant_force = [14, 2]
index_edge = form.index_edge()
L = 6.0

for index in index_edges_constant_force:
    form.edge_attribute(index_edge[index], 'target_length', L)

# Reflect all constraints to force diagram
force.constraints_from_dual()

# Release vertices 0, 8, 9 force fixity on x:
for key in move_vertices:
    force.vertex_attribute(key, 'is_fixed_x', False)

release_form = []  #[0, 7]

for key in release_form:
    form.vertex_attribute(key, 'is_fixed_y', False)

# View Constraints in x and in y

viewer = Viewer(form, force, delay_setup=False)
viewer.draw_form(vertexlabel={key: key for key in form.vertices()},
                 edgelabel={uv: index for index, uv in enumerate(form.edges())},
                 vertexsize=0.2,
                 forces_on=False,
                 vertexcolor={key: '#FF0000' for key in form.vertices_where({'is_fixed_x': True})})
viewer.draw_force(edgelabel=force_edge_labels,
                 vertexcolor={key: '#FF0000' for key in force.vertices_where({'is_fixed_x': True})})
viewer.show()

viewer = Viewer(form, force, delay_setup=False)
viewer.draw_form(vertexlabel={key: key for key in form.vertices()},
                 edgelabel={uv: index for index, uv in enumerate(form.edges())},
                 vertexsize=0.2,
                 forces_on=False,
                 vertexcolor={key: '#0000FF' for key in form.vertices_where({'is_fixed_y': True})})
viewer.draw_force(edgelabel=force_edge_labels,
                 vertexcolor={key: '#0000FF' for key in force.vertices_where({'is_fixed_y': True})})
viewer.show()

# Update force diagram given constraints
force_update_from_constraints(force)

# Update form diagram based on force diagram
# form_update_from_force(form, force)

# Update form diagram based on force diagram eith Bi-ags

from compas_ags.ags import ConstraintsCollection
from compas_ags.ags import form_update_from_force_newton

C = ConstraintsCollection(form)
C.constraints_from_form()

form_update_from_force_newton(form, force, constraints=C)

viewer = Viewer(form, force, delay_setup=False)

viewer.draw_form(lines=form_lines,
                 forces_on=True,
                 vertexlabel={key: key for key in form.vertices()},
                 external_on=True,
                 vertexsize=0.2,
                 edgelabel={uv: index for index, uv in enumerate(form.edges())}
                 )

viewer.draw_force(lines=force_lines,
                  vertexlabel={key: key for key in force.vertices()},
                  vertexsize=0.2,
                  edgelabel=force_edge_labels
                  )

viewer.show()

viewer = Viewer(form, force, delay_setup=False)

viewer.draw_form(vertexlabel={key: key for key in form.vertices()},
                 edgelabel={uv: index for index, uv in enumerate(form.edges())},
                 vertexsize=0.2,
                 forces_on=True)
viewer.draw_force(vertexlabel={key: key for key in force.vertices()},
                  vertexsize=0.2,
                  edgelabel={(u, v): force.edge_length(u, v) for u, v in force.edges()})
viewer.show()


# modify the geometry of the force diagram moving nodes further at right to the left
move_vertices = [0, 9, 8]
translation = +1.0
for key in move_vertices:
    x0 = force.vertex_attribute(key, 'x')
    force.vertex_attribute(key, 'x', x0 + translation)

form_update_from_force_newton(form, force, constraints=C)

viewer = Viewer(form, force, delay_setup=False)

viewer.draw_form(lines=form_lines,
                 forces_on=True,
                 vertexlabel={key: key for key in form.vertices()},
                 external_on=True,
                 vertexsize=0.2,
                 edgelabel={uv: index for index, uv in enumerate(form.edges())}
                 )

viewer.draw_force(lines=force_lines,
                  vertexlabel={key: key for key in force.vertices()},
                  vertexsize=0.2,
                  edgelabel=force_edge_labels
                  )

viewer.show()
