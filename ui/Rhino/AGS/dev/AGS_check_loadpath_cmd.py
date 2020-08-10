from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

import scriptcontext as sc

import compas_rhino


__commandname__ = "AGS_check_loadpath"


def RunCommand(is_interactive):

    if 'AGS' not in sc.sticky:
        compas_rhino.display_message('AGS has not been initialised yet.')
        return

    proxy = sc.sticky['AGS']['proxy']
    scene = sc.sticky['AGS']['scene']
    form = scene.find_by_name('Form')[0]
    force = scene.find_by_name('Force')[0]

    proxy.package = 'compas_ags.ags.loadpath'

    lp = proxy.compute_loadpath_proxy(form.diagram.data, force.diagram.data)
    print('Loadpath of the structure is {} kNm.'.format(lp))


# ==============================================================================
# Main
# ==============================================================================

if __name__ == '__main__':

    RunCommand(True)
