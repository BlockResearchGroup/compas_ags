from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

import scriptcontext as sc

import compas_rhino

import AGS_assign_forces_cmd
import AGS_form_toggle_fix_cmd


__commandname__ = "AGS_toolbar_form_attribute"


def RunCommand(is_interactive):

    if 'AGS' not in sc.sticky:
        compas_rhino.display_message('AGS has not been initialised yet.')
        return

    options = ["AssignForces", "FixNodes"]
    option = compas_rhino.rs.GetString("Assign Attribute:", strings=options)

    if not option:
        return

    if option == "AssignForces":
        AGS_assign_forces_cmd.RunCommand(True)

    elif option == "FixNodes":
        AGS_form_toggle_fix_cmd.RunCommand(True)


# ==============================================================================
# Main
# ==============================================================================

if __name__ == '__main__':

    RunCommand(True)
