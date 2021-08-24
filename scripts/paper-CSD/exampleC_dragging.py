import compas_ags
from compas_ags.diagrams import FormDiagram
from compas_ags.diagrams import ForceDiagram
from compas_ags.ags import form_update_q_from_qind
from compas_ags.ags import force_update_from_form
from compas_ags.ags import update_diagrams_from_constraints
from compas_ags.viewers import Viewer


def view_form_force(form, force, forcescale=0.5, edge_label=True):
    if edge_label:
        form_edge_label = {uv: index for index, uv in enumerate(form.edges())}
        force_edge_label = force_edge_labels
    else:
        form_edge_label = None
        force_edge_label = None

    viewer = Viewer(form, force, delay_setup=False)
    viewer.draw_form(edgelabel=form_edge_label,
                     forces_on=True,
                     forcescale=forcescale,
                     vertexcolor={key: '#000000' for key in form.vertices_where({'is_fixed': True})})
    viewer.draw_force(edgelabel=force_edge_label)
    viewer.show()


def view_with_initial_stage(form, force, forcescale=0.5, edge_label=True):
    if edge_label:
        form_edge_label = {uv: index for index, uv in enumerate(form.edges())}
        force_edge_label = force_edge_labels
    else:
        form_edge_label = None
        force_edge_label = None

    viewer = Viewer(form, force, delay_setup=False)
    viewer.draw_form(lines=form_lines,
                     forces_on=True,
                     external_on=True,
                     forcescale=forcescale,
                     edgelabel=form_edge_label,
                     vertexcolor={key: '#000000' for key in form.vertices_where({'is_fixed': True})})
    viewer.draw_force(lines=force_lines,
                      edgelabel=force_edge_label
                      )
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


# ---------------------------------------------------------------------------------------
#   3. Dragging nodes of form diagram and updating both diagrams according to constraints
#       - Input a parabolic arch (uniform load case).
#       - Move the form diagram support
#       - Move one of the internal nodes to a specific position
# ---------------------------------------------------------------------------------------

input_file = compas_ags.get('paper/exB_arch-output.obj')

form = FormDiagram.from_json(input_file)
force = ForceDiagram.from_formdiagram(form)

# create label for plots
force_edges = force.ordered_edges(form)
force_edge_labels = {(u, v): index for index, (u, v) in enumerate(force_edges)}
force_edge_labels.update({(v, u): index for index, (u, v) in enumerate(force_edges)})

# update the diagrams
form_update_q_from_qind(form)
force_update_from_form(force, form)

# visualise initial solution
view_form_force(form, force, forcescale=2.0)

form_lines, force_lines = store_initial_lines(form, force)

# ---------------------------------------------
# Move the form diagram support

# Reflect all constraints to force diagram
force.constraints_from_dual()

form_nodes_move = [1, 8, 11]  # move the support and all leaf nodes connected to it
move_support_dist = +2.0
for key in form_nodes_move:
    _, y, _ = form.vertex_coordinates(key)
    form.vertex_attribute(key, 'y', y + move_support_dist)

update_diagrams_from_constraints(form, force)

view_with_initial_stage(form, force, forcescale=2.0, edge_label=False)

# ---------------------------------------------
# Move the form diagram midspan

# Reflect all constraints to force diagram
force.constraints_from_dual()

form_nodes_move = [4, 15]  # move the node and all leaf nodes connected to it
move_support_dist = +1.5
for key in form_nodes_move:
    _, y, _ = form.vertex_coordinates(key)
    form.vertex_attribute(key, 'y', y + move_support_dist)
    form.vertex_attribute(key, 'is_fixed_y', True)

update_diagrams_from_constraints(form, force)

view_with_initial_stage(form, force, forcescale=2.0, edge_label=False)
