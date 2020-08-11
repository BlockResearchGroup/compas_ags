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
    form = scene.find_by_name('Form')[0]
    force = scene.find_by_name('Force')[0]

    proxy.package = 'compas_ags.ags.graphstatics'

    while True:
        vertices = force.select_vertices()
        if not vertices:
            break
        if vertices and force.move_vertices(vertices):
            scene.clear()
            scene.update()

        toggle = compas_rhino.rs.GetString("Keep selecting?", defaultString="True", strings=["True", "False"])
        if toggle == "True":
            continue
        else:
            form.diagram.data = proxy.form_update_from_force_proxy(form.diagram.data, force.diagram.data)
            scene.clear()
            scene.update()
            
        # if force.move_vertices(vertices):
        #     # update form diagram
        #     form.diagram.data = proxy.form_update_from_force_proxy(form.diagram.data, force.diagram.data, kmax=100)
        #     # update the scene
        #     scene.clear()
        #     scene.update()


# ==============================================================================
# Main
# ==============================================================================

if __name__ == '__main__':

    RunCommand(True)
