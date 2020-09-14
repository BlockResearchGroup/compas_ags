from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

import scriptcontext as sc

import compas_rhino


__commandname__ = "AGS_force_move_nodes"


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

    fixed = list(form.diagram.vertices_where({'is_fixed': True}))
    if len(fixed) < 2:
        answer = compas_rhino.rs.GetString("You only have {} fixed vertices in the Form Diagram. Continue?", "No", ["Yes", "No"])
        if not answer:
            return
        if answer == "No":
            return

    proxy.package = 'compas_ags.ags.graphstatics'

    form.settings['show.edgelabels'] = True
    form.settings['show.forcelabels'] = False
    force.settings['show.edgelabels'] = True

    scene.update()

    while True:
        vertices = force.select_vertices()
        if not vertices:
            break

        if force.move_vertices(vertices):
            scene.update()

    form.diagram.data = proxy.form_update_from_force_proxy(form.diagram.data, force.diagram.data)

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
