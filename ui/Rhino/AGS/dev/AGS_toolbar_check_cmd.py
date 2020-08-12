from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

import scriptcontext as sc

import compas_rhino

from . import AGS_check_dof_cmd
from . import AGS_check_loadpath_cmd


__commandname__ = "AGS_toolbar_check"


def RunCommand(is_interactive):

    if 'AGS' not in sc.sticky:
        compas_rhino.display_message('AGS has not been initialised yet.')
        return

    options = ["DoF, Loadpath"]
    option = compas_rhino.rs.GetString("Session: ", strings=options)

    if not option:
        return

    if option == "DoF":
        AGS_check_dof_cmd.RunCommand(True)

    elif option == "Loadpath":
        AGS_check_loadpath_cmd.RunCommand(True)


# ==============================================================================
# Main
# ==============================================================================

if __name__ == '__main__':

    RunCommand(True)
