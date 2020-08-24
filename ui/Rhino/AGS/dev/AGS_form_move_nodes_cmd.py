from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

import scriptcontext as sc

import compas_rhino


__commandname__ = "AGS_form_move_nodes"


def RunCommand(is_interactive):

    if 'AGS' not in sc.sticky:
        compas_rhino.display_message('AGS has not been initialised yet.')
        return

    proxy = sc.sticky['AGS']['proxy']
    scene = sc.sticky['AGS']['scene']
    form = scene.find_by_name('Form')[0]
    force = scene.find_by_name('Force')[0]

    if not form:
        compas_rhino.display_message("There is no FormDiagram in the scene.")
        return

    if not force:
        compas_rhino.display_message("There is no ForceDiagram in the scene.")
        return

    proxy.package = 'compas_ags.ags.graphstatics'

    while True:
        vertices = form.select_vertices()
        if not vertices:
            break

        if form.move_vertices(vertices):
            # update force diagram
            form.diagram.data = proxy.form_update_q_from_qind_proxy(form.diagram.data)
            force.diagram.data = proxy.force_update_from_form_proxy(force.diagram.data, form.diagram.data)
            # update the scene
            scene.update()


# ==============================================================================
# Main
# ==============================================================================

if __name__ == '__main__':

    RunCommand(True)
