from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

import scriptcontext as sc

import compas_rhino

import AGS_form_location_cmd
import AGS_form_displaysettings_cmd
import AGS_force_location_cmd
import AGS_force_scale_cmd
import AGS_force_displaysettings_cmd


__commandname__ = "AGS_toolbar_display"


def RunCommand(is_interactive):

    if 'AGS' not in sc.sticky:
        compas_rhino.display_message('AGS has not been initialised yet.')
        return

    options = ["FormLocation", "FormDiaplay", "ForceLocation", "ForceScale", "ForceDisplay"]
    option = compas_rhino.rs.GetString("Display:", strings=options)

    if not option:
        return

    if option == "FormLocation":
        AGS_form_location_cmd.RunCommand(True)

    elif option == "FormDiaplay":
        AGS_form_displaysettings_cmd.RunCommand(True)

    elif option == "ForceLocation":
        AGS_force_location_cmd.RunCommand(True)

    elif option == "ForceScale":
        AGS_force_scale_cmd.RunCommand(True)

    elif option == "ForceDisplay":
        AGS_force_displaysettings_cmd.RunCommand(True)


# ==============================================================================
# Main
# ==============================================================================

if __name__ == '__main__':

    RunCommand(True)
