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

    objects = scene.find_by_name('Form')
    if not objects:
        compas_rhino.display_message("There is no FormDiagram in the scene.")
        return
    form = objects[0]

    objects = scene.find_by_name('Force')
    if not objects:
        compas_rhino.display_message("There is no ForceDiagram in the scene.")
        return
    force = objects[0]

    proxy.package = 'compas_ags.ags.graphstatics'

    form.settings['show.edgelabels'] = True
    form.settings['show.forcelabels'] = False
    force.settings['show.edgelabels'] = True

    scene.update()

    while True:
        vertices = form.select_vertices()
        if not vertices:
            break

        if form.move_vertices(vertices):
            if scene.settings['AGS']['autoupdate']:
                form.diagram.data = proxy.form_update_q_from_qind_proxy(form.diagram.data)
                force.diagram.data = proxy.force_update_from_form_proxy(force.diagram.data, form.diagram.data)
            scene.update()

    form.settings['show.edgelabels'] = False
    form.settings['show.forcelabels'] = True
    force.settings['show.edgelabels'] = False

    scene.update()
    scene.save()


# ==============================================================================
# Main
# ==============================================================================

if __name__ == '__main__':

    RunCommand(True)
