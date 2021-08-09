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
# ------------------------------------------------------------------------------
# ------------------------------------------------------------------------------



# ------------------------------------------------------------------------------
#   1. Dragging nodes of form and force diagram
#       - Input a parabolic arch (uniform load case).
#       - Drag nodes to increase sag - drag nodes to invert to tension.
#       - Drag nodes of
#       - No vertex constraints apply on the force diag. (only to the ind. edge)
# ------------------------------------------------------------------------------

import compas_ags
from compas_ags.diagrams import FormGraph
from compas_ags.diagrams import FormDiagram
from compas_ags.diagrams import ForceDiagram
from compas_ags.ags import form_update_q_from_qind
from compas_ags.ags import force_update_from_form
from compas_ags.ags import update_diagrams_from_constraints
from compas_ags.ags import form_update_from_force
from compas_ags.viewers import Viewer

graph = FormGraph.from_obj(compas_ags.get('paper/exD_zeroforce.obj'))
form = FormDiagram.from_graph(graph)
force = ForceDiagram.from_formdiagram(form)
index_edge = form.index_edge()

# create label for plots
force_edges = force.ordered_edges(form)
force_edge_labels = {(u, v): index for index, (u, v) in enumerate(force_edges)}
force_edge_labels.update({(v, u): index for index, (u, v) in enumerate(force_edges)})

view_form_force(form, force, forcescale=2.0)

ind_edges = [0, 4, 9, 12, 17]
for index in ind_edges:
    form.edge_attribute(index_edge[index], 'is_ind', True)
    form.edge_attribute(index_edge[index], 'q', 1.0)

supports = [12, 14]
for key in supports:
    form.vertex_attribute(key, 'is_fixed', True)

# update the diagrams
form_update_q_from_qind(form)
force_update_from_form(force, form)

for key in force.vertices():
    print(key, force.vertex_coordinates(key))

# visualise initial solution
view_form_force(form, force, forcescale=2.0)
view_with_force_lengths(form, force)

form_lines, force_lines = store_initial_lines(form, force)

# ---------------------------------------------
########## Movement exact to solution:

# 13, 12 move left
x0 = 5.333333333333331
y0 = -2.1666666666666674
force.vertex_attribute(13, 'x', x0)
force.vertex_attribute(12, 'x', x0)
# 11, 10, 15, 14 move right and split
force.vertex_attribute(11, 'x', x0)#5.333333333333331)
force.vertex_attribute(10, 'x', x0)#5.333333333333331)
force.vertex_attribute(15, 'x', x0)#5.333333333333331)
force.vertex_attribute(14, 'x', x0)#5.333333333333331)
force.vertex_attribute(11, 'y', y0 + 0.5)#5.333333333333331)
force.vertex_attribute(10, 'y', y0 + 1.5)#5.333333333333331)
force.vertex_attribute(15, 'y', y0 - 1.5)#5.333333333333331)
force.vertex_attribute(14, 'y', y0 - 0.5)#5.333333333333331)

# Identify auto constraints
form.identify_constraints()

form_update_from_force(form, force)

view_with_initial_stage(form, force, forcescale=2.0)
view_with_force_lengths(form, force)

# ---------------------------------------------
########## Add constraints on force for constant force

# top_chord = [22, 23, 27, 28, 20, 21]
# bottom_chord = [18, 13, 10, 5, 2, 1]
# struts = [19, 15, 11, 7, 3]
# diagonals = [16, 14, 8, 6]
# loads = [17, 12, 9, 4, 0]

# L = force.edge_length(*force_edges[21])
# # top chord
# for index in top_chord:
#     form.edge_attribute(index_edge[index], 'target_length', L)

# # bottom chord
# for index in bottom_chord:
#     form.edge_attribute(index_edge[index], 'has_fixed_orientation', True)
# # bottom chord L = 2.5
# # for index in bottom_chord:
# #     form.edge_attribute(index_edge[index], 'target_length', L)

# # for index in loads:
# #     form.edge_attribute(index_edge[index], 'target_length', 1.0)

# # for index in struts:
# #     form.edge_attribute(index_edge[index], 'target_length', 1.0)

# # zero on diagonals
# for index in diagonals:
#     form.edge_attribute(index_edge[index], 'target_length', 0.0)

# # Identify auto constraints
# form.identify_constraints()

# # Reflect all constraints to force diagram
# force.constraints_from_dual()

# #vertices force loadline
# vertices_loadline = [2, 3, 4, 5, 6, 7, 0, 1]
# for key in vertices_loadline:
#     force.vertex_attribute(key, 'is_fixed_x', True)
#     force.vertex_attribute(key, 'is_fixed_y', True)

# vertices_force_fix = [9, 16]
# for key in vertices_force_fix:
#     force.vertex_attribute(key, 'is_fixed_x', True)
#     force.vertex_attribute(key, 'is_fixed_y', True)

# form_vertices_bottom_chord = [14, 9, 7, 5, 3, 1, 12]
# for key in form_vertices_bottom_chord:
#     form.vertex_attribute(key, 'is_fixed_y', True)

# form_vertices_top_chord = [11, 19, 17, 18, 10]
# for key in form_vertices_top_chord:
#     form.vertex_attribute(key, 'is_fixed_x', True)

# show_constraints(form, force)

# update_diagrams_from_constraints(form, force, max_iter=20, callback=view_with_initial_stage, printout=True)
# # update_diagrams_from_constraints(form, force, max_iter=200, callback=None, printout=True)

# view_with_initial_stage(form, force)
# view_with_force_lengths(form, force)



