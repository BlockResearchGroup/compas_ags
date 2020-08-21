from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

import scriptcontext as sc

import compas_rhino


__commandname__ = "AGS_compute_loadpath"


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

    proxy.package = 'compas_ags.ags.loadpath'

    lp = proxy.compute_loadpath(form.diagram, force.diagram)
    compas_rhino.display_message('Loadpath of the structure is {} kNm.'.format(round(lp, 2)))


# ==============================================================================
# Main
# ==============================================================================

if __name__ == '__main__':

    RunCommand(True)
