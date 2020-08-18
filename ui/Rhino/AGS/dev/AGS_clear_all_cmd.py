from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

import scriptcontext as sc

import compas_rhino

from compas_ags.rhino import Scene


__commandname__ = "AGS_clear_all"


def RunCommand(is_interactive):

    if 'AGS' not in sc.sticky:
        compas_rhino.display_message('AGS has not been initialised yet.')
        return

    scene = sc.sticky['AGS']['scene']
    if not scene:
        return

    options = ["Yes", "No"]
    option = compas_rhino.rs.GetString("Clear all RV2 objects?", strings=options, defaultString="No")
    if not option:
        return

    if option == "Yes":
        scene.clear()
        sc.sticky['AGS']['scene'] = Scene()


# ==============================================================================
# Main
# ==============================================================================

if __name__ == '__main__':

    RunCommand(True)
