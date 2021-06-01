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

    objects = scene.find_by_name('Form')
    if not objects:
        compas_rhino.display_message("There is no FormDiagram in the scene.")
        return
    form = objects[0]

    edges = list(form.diagram.edges_where({'is_ind': True}))

    if not len(edges):
        compas_rhino.display_message(
            "Warning: None of the edges of the diagram are marked as 'independent'. Forces can only be assigned to independent edges. Please select the independent edges first.")
        return

    form.settings['show.edgelabels'] = True
    form.settings['show.forcelabels'] = False
    scene.update()

    edge_index = form.diagram.edge_index()

    names = [edge_index[edge] for edge in edges]

    values = [str(form.diagram.edge_attribute(edge, 'f')) for edge in edges]
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

        scene.update()
        scene.save()

    form.settings['show.edgelabels'] = False
    form.settings['show.forcelabels'] = True
    scene.update()


# ==============================================================================
# Main
# ==============================================================================

if __name__ == '__main__':

    RunCommand(True)
