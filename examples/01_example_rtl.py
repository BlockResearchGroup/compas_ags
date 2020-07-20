import compas_ags

from compas_ags.diagrams import FormGraph
from compas_ags.diagrams import FormDiagram
from compas_ags.diagrams import ForceDiagram
from compas_ags.ags import graphstatics

from compas_ags.viewers import Viewer

# ==============================================================================
# Construct the graph of a single panel truss,
# including loads and reaction forces.
# ==============================================================================

graph = FormGraph.from_obj(compas_ags.get('paper/gs_form_force.obj'))

form = FormDiagram.from_graph(graph)
force = ForceDiagram.from_formdiagram(form)

# ==============================================================================
# Fix the left and right supports.
# ==============================================================================

left = next(form.vertices_where({'x': 0.0, 'y': 0.0}))
right = next(form.vertices_where({'x': 6.0, 'y': 0.0}))

fixed = [left, right]

form.set_fixed(fixed)
force.set_fixed([0])

# ==============================================================================
# Set the magnitude of the load.
# ==============================================================================

form.edge_force(1, -10.0)

# ==============================================================================
# Update the force densities in the form diagram.
# ==============================================================================

graphstatics.form_update_q_from_qind(form)

# ==============================================================================
# Update the geometry of the force diagram.
# ==============================================================================

graphstatics.force_update_from_form(force, form)

# ==============================================================================
# Store the original geometries.
# ==============================================================================

force_key_xyz = {key: force.vertex_coordinates(key) for key in force.vertices()}

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

# ==============================================================================
# Change the position of the "free" node of the force diagram
# ==============================================================================

force.vertex[4]['x'] -= 8.0

# ==============================================================================
# Update the form diagram accordingly.
# ==============================================================================

graphstatics.form_update_from_force(form, force, kmax=100)

# ==============================================================================
# Indicate the movement of the free node in the force diagram with an arrow.
# ==============================================================================

force_lines.append({
    'start': force_key_xyz[4],
    'end': force.vertex_coordinates(4),
    'color': '#ff0000',
    'width': 10.0,
    'style': '-',
})

# ==============================================================================
# Visualize the result.
# ==============================================================================

viewer = Viewer(form, force, delay_setup=False, figsize=(12, 7.5))

viewer.draw_form(lines=form_lines,
                 forces_on=False,
                 vertexlabel={key: key for key in form.vertices()},
                 vertexsize=0.2,
                 vertexcolor={key: '#000000' for key in fixed},
                 edgelabel={key: index for index, key in enumerate(form.edges())})

viewer.draw_force(lines=force_lines,
                  vertexlabel={key: key for key in force.vertices()},
                  vertexsize=0.2)

viewer.show()
