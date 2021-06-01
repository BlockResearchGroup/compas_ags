from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

import scriptcontext as sc

import compas_rhino
# import AGS_form_check_deviation_cmd
from compas_ags.utilities.equilibrium import check_deviations


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

    proxy.package = 'compas_ags.ags.graphstatics'

    form.diagram.data = proxy.form_update_from_force_proxy(form.diagram.data, force.diagram.data)
    if not check_deviations(form.diagram, force.diagram, tol=scene.settings['AGS']['max_deviation']):
        compas_rhino.display_message('Error: Invalid movement on force diagram nodes or insuficient constraints in the form diagram.')
        max_dev, limit = max(form.diagram.edges_attribute('a')), scene.settings['AGS']['max_deviation']
        compas_rhino.display_message('Diagrams are not parallel!\nMax. angle deviation: {0:.2g} deg\nThreshold assumed: {1:.2g} deg.'.format(max_dev, limit))

    scene.update()
    scene.save()


# ==============================================================================
# Main
# ==============================================================================

if __name__ == '__main__':

    RunCommand(True)
