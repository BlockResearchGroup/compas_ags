def show_constraints(form, force):
    viewer = Viewer(form, force, delay_setup=False)
    viewer.draw_form(vertexlabel={key: key for key in form.vertices()},
                    edgelabel={uv: index for index, uv in enumerate(form.edges())},
                    vertexsize=0.2,
                    forces_on=False,
                    vertexcolor={key: '#FF0000' for key in form.vertices_where({'is_fixed_x': True})})
    viewer.draw_force(vertexcolor={key: '#FF0000' for key in force.vertices_where({'is_fixed_x': True})})
    viewer.show()

    viewer = Viewer(form, force, delay_setup=False)
    viewer.draw_form(vertexlabel={key: key for key in form.vertices()},
                    edgelabel={uv: index for index, uv in enumerate(form.edges())},
                    vertexsize=0.2,
                    forces_on=False,
                    vertexcolor={key: '#0000FF' for key in form.vertices_where({'is_fixed_y': True})})
    viewer.draw_force(vertexcolor={key: '#0000FF' for key in force.vertices_where({'is_fixed_y': True})})
    viewer.show()

    viewer = Viewer(form, force, delay_setup=False)
    viewer.draw_form(vertexlabel={key: key for key in form.vertices()},
                    edgelabel={uv: str(form.edge_attribute(uv, 'target_vector')) for uv in form.edges()},
                    vertexsize=0.2,
                    # forces_on=False,
                    vertexcolor={key: '#000000' for key in form.vertices_where({'is_fixed': True})})
    viewer.draw_force(vertexcolor={key: '#000000' for key in force.vertices_where({'is_fixed': True})},
                    edgelabel={uv: str(force.edge_attribute(uv, 'target_vector')) for uv in force.edges()})
    viewer.show()

    viewer = Viewer(form, force, delay_setup=False)
    viewer.draw_form(vertexlabel={key: key for key in form.vertices()},
                    edgelabel={uv: form.edge_attribute(uv, 'target_length') for uv in form.edges()},
                    vertexsize=0.2,
                    forces_on=False,
                    vertexcolor={key: '#000000' for key in form.vertices_where({'is_fixed': True})})
    viewer.draw_force(vertexcolor={key: '#000000' for key in force.vertices_where({'is_fixed': True})},
                    edgelabel={uv: force.edge_attribute(uv, 'target_length') for uv in force.edges()})
    viewer.show()


def view_with_initial_stage(form, force, forcescale=0.5):
    viewer = Viewer(form, force, delay_setup=False)

    viewer.draw_form(lines=form_lines,
                    forces_on=True,
                    vertexlabel={key: key for key in form.vertices()},
                    external_on=True,
                    vertexsize=0.2,
                    forcescale=forcescale,
                    edgelabel={uv: index for index, uv in enumerate(form.edges())}
                    )

    viewer.draw_force(lines=force_lines,
                    vertexlabel={key: key for key in force.vertices()},
                    vertexsize=0.2,
                    edgelabel=force_edge_labels
                    )

    viewer.show()

def view_with_force_lengths(form, force):
    viewer = Viewer(form, force, delay_setup=False)
    viewer.draw_form(vertexlabel={key: key for key in form.vertices()},
                    edgelabel={(u, v): round(form.edge_length(u, v), 3) for u, v in form.edges()},
                    vertexsize=0.2,
                    forces_on=True)
    viewer.draw_force(vertexlabel={key: key for key in force.vertices()},
                    vertexsize=0.2,
                    edgelabel={(u, v): round(force.edge_length(u, v), 3) for u, v in force.edges()})
    viewer.show()

def view_form_force(form, force, forcescale=0.5):
    viewer = Viewer(form, force, delay_setup=False)
    viewer.draw_form(vertexlabel={key: key for key in form.vertices()},
                    edgelabel={uv: index for index, uv in enumerate(form.edges())},
                    vertexsize=0.2,
                    forces_on=True,
                    forcescale=forcescale,
                    vertexcolor={key: '#000000' for key in form.vertices_where({'is_fixed': True})})
    viewer.draw_force(vertexlabel={key: key for key in force.vertices()},
                    vertexsize=0.2,
                    edgelabel=force_edge_labels)
    viewer.show()

def store_initial_lines(form, force):

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

    return form_lines, force_lines

# ------------------------------------------------------------------------------
#   1. create a simple arch from nodes and edges and visualise
# ------------------------------------------------------------------------------

import compas_ags
from compas_ags.diagrams import FormGraph
from compas_ags.diagrams import FormDiagram
from compas_ags.viewers import Viewer

graph = FormGraph.from_obj(compas_ags.get('paper/ex1_arch.obj'))
form = FormDiagram.from_graph(graph)

# ------------------------------------------------------------------------------
#   2. prescribe edge force density to independent edge and supports
# ------------------------------------------------------------------------------

edges_ind = [(1, 8)]
for index in edges_ind:
    u, v = index
    form.edge_attribute((u, v), 'is_ind', True)
    form.edge_attribute((u, v), 'q', -1.0)

supports = [0, 7]
for key in supports:
    form.vertex_attribute(key, 'is_fixed', True)

for key in form.vertices():
    print(form.vertex_attribute(key,  'is_fixed'))

for u, v in form.leaf_edges():
    print(form.edge_attribute((u, v), 'is_reaction'))

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

force_edges = force.ordered_edges(form)

force_edge_labels1 = {(u, v): index for index, (u, v) in enumerate(force_edges)}
force_edge_labels2 = {(v, u): index for index, (u, v) in enumerate(force_edges)}
force_edge_labels = {**force_edge_labels1, **force_edge_labels2}

# store lines representing the current state of equilibrium
form_lines, force_lines = store_initial_lines(form, force)

# view_form_force(form, force)

# --------------------------------------------------------------------------
#   4. Set default constraints based on the direction of the external loads
# --------------------------------------------------------------------------

# Identify auto constraints
form.identify_constraints()

# Reflect all constraints to force diagram
force.constraints_from_dual()

show_constraints(form, force)

# --------------------------------------------------------------------------
#   5. force diagram manipulation and modify the form diagram
# --------------------------------------------------------------------------

from compas_ags.ags import form_update_from_force

# modify the geometry of the force diagram moving nodes further at right to the left
move_vertices = [0, 9, 8]
translation = +7.0
for key in move_vertices:
    x0 = force.vertex_attribute(key, 'x')
    force.vertex_attribute(key, 'x', x0 + translation)

form_update_from_force(form, force)

view_with_initial_stage(form, force)
view_with_force_lengths(form, force)


# --------------------------------------------------------------------------
#   6. Assign target length to edge #2 = 7.0 kN
# --------------------------------------------------------------------------

from compas_ags.ags import update_diagrams_from_constraints

index_edge = form.index_edge()

# # define loads and reactions:
# edges_load = [3, 5, 7, 9, 11, 13]
# edges_reaction = [0, 1, 15, 16]
# for i in edges_load:
#     form.edge_attribute(index_edge[i], 'is_load', True)
# for i in edges_reaction:
#     form.edge_attribute(index_edge[i], 'is_reaction', True)

# define constant force
edges_constant_force = [2]
L = 7.0
for index in edges_constant_force:
    form.edge_attribute(index_edge[index], 'target_length', L)

for edge in form.edges_where({'is_load': True}):
    length = form.edge_length(*edge)
    form.edge_attribute(edge, 'target_length', length)

# Reflect all constraints to force diagram
force.constraints_from_dual()

# Release vertices 0, 8, 9 force fixity on x:       # are already released
for key in move_vertices:
    force.vertex_attribute(key, 'is_fixed_x', False)
    force.vertex_attribute(key, 'is_fixed_y', True)

load_vertices = [1, 2, 3, 4, 5, 6, 7]
# fix load vertices on y:
for key in load_vertices:
    force.vertex_attribute(key, 'is_fixed_y', True)

release_form_y = []  #[0, 7]
for key in release_form_y:
    form.vertex_attribute(key, 'is_fixed_y', False)

release_form_x = []  #[0, 7]
for key in release_form_x:
    form.vertex_attribute(key, 'is_fixed_x', False)

show_constraints(form, force)

update_diagrams_from_constraints(form, force, callback=view_with_initial_stage)

view_with_initial_stage(form, force)
view_with_force_lengths(form, force)

# # modify the geometry of the force diagram moving nodes further at right to the left
# move_vertices = [0, 9, 8]
# translation = -1.0
# for key in move_vertices:
#     x0 = force.vertex_attribute(key, 'x')
#     force.vertex_attribute(key, 'x', x0 + translation)

# form_update_from_force(form, force)
# # form_update_from force_newton

# view_with_initial_stage(form, force)

