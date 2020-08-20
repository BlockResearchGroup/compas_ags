from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

import scriptcontext as sc

import compas_rhino


__commandname__ = "AGS_assign_forces"


def RunCommand(is_interactive):

    if 'AGS' not in sc.sticky:
        compas_rhino.display_message('AGS has not been initialised yet.')
        return

    scene = sc.sticky['AGS']['scene']
    form = scene.find_by_name('Form')[0]

    if not form:
        print("There is no FormDiagram in the scene.")
        return

    # select edges and assign forces
    while True:
        edges = form.select_edges()
        if not edges:
            break
        force_value = compas_rhino.rs.GetReal("Force on Edges (kN)", 1.0)
        for edge in edges:
            form.diagram.edge_force(edge, force_value)
        scene.update()

    edge_index = form.diagram.edge_index()

    edges = list(form.diagram.edges_where({'is_ind': True}))

    names = [str(edge_index[edge]) for edge in edges]
    values = ["{:.3f}".format(form.diagram.edge_force(edge)) for edge in edges]
    values = compas_rhino.update_named_values(names, values)

    if values:
        for name, value in zip(names, values):
            form.diagram.edge_force(int(name), float(value))


# ==============================================================================
# Main
# ==============================================================================

if __name__ == '__main__':

    RunCommand(True)
