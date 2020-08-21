from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

import scriptcontext as sc

import compas_rhino


__commandname__ = "AGS_form_assign_forces"


def RunCommand(is_interactive):

    if 'AGS' not in sc.sticky:
        compas_rhino.display_message('AGS has not been initialised yet.')
        return

    scene = sc.sticky['AGS']['scene']
    form = scene.find_by_name('Form')[0]

    if not form:
        compas_rhino.display_message("There is no FormDiagram in the scene.")
        return

    edge_index = form.diagram.edge_index()

    # select edges and assign forces
    while True:
        edges = form.select_edges()
        if not edges:
            break

        for edge in edges:
            form.diagram.edge_attribute(edge, 'is_ind', not form.diagram.edge_attribute(edge, 'is_ind'))
        scene.update()

    edges = list(form.diagram.edges_where({'is_ind': True}))
    names = [edge_index[edge] for edge in edges]
    values = [form.diagram.edge_attribute(edge, 'f') for edge in edges]
    values = compas_rhino.update_named_values(names, values, message='Independent edges.', title='Update force values.')
    if values:
        for edge, value in zip(edges, values):
            try:
                F = float(value)
            except (ValueError, TypeError):
                pass
            else:
                L = form.diagram.edge_length(*edge)
                Q = F / L
                form.diagram.edge_attribute(edge, 'f', F)
                form.diagram.edge_attribute(edge, 'q', Q)


# ==============================================================================
# Main
# ==============================================================================

if __name__ == '__main__':

    RunCommand(True)
