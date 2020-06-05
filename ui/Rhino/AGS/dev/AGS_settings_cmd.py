from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

import scriptcontext as sc
import compas_rhino


__commandname__ = "AGS_settings"


def RunCommand(is_interactive):
    if "AGS" not in sc.sticky:
        raise Exception("Initialise the plugin first!")

    AGS = sc.sticky['AGS']

    if compas_rhino.update_settings(AGS['settings']):
        pass


# ==============================================================================
# Main
# ==============================================================================

if __name__ == '__main__':

    RunCommand(True)
