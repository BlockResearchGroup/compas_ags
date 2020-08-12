from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

import scriptcontext as sc

import compas_rhino

from . import AGS_form_move_nodes_cmd

__commandname__ = "AGS_toolbar_form_modify"


def RunCommand(is_interactive):

    if 'AGS' not in sc.sticky:
        compas_rhino.display_message('AGS has not been initialised yet.')
        return

    options = ["MoveNodes"]
    option = compas_rhino.rs.GetString("Modify Form: ", strings=options)

    if not option:
        return

    if option == "MoveNodes":
        AGS_form_move_nodes_cmd.RunCommand(True)


# ==============================================================================
# Main
# ==============================================================================

if __name__ == '__main__':

    RunCommand(True)
