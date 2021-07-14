from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

import scriptcontext as sc

import compas_rhino


__commandname__ = "AGS_form_deviation_threshold"


def RunCommand(is_interactive):

    if 'AGS' not in sc.sticky:
        compas_rhino.display_message('AGS has not been initialised yet.')
        return

    scene = sc.sticky['AGS']['scene']

    max_dev = compas_rhino.rs.GetReal(message="Assign threshold for maximum angle deviation", number=scene.settings['AGS']['max_deviation'])
    if not max_dev:
        return

    scene.settings['AGS']['max_deviation'] = max_dev


# ==============================================================================
# Main
# ==============================================================================

if __name__ == '__main__':

    RunCommand(True)
