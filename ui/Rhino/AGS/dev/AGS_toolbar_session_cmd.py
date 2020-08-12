from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

import os
import json

import scriptcontext as sc

import compas_rhino

from . import AGS_restart_cmd
from . import AGS_session_load_cmd
from . import AGS_session_save_cmd


__commandname__ = "AGS_toolbar_session"


def RunCommand(is_interactive):

    if 'AGS' not in sc.sticky:
        compas_rhino.display_message('AGS has not been initialised yet.')
        return

    options = ["Restart, LoadSession, SaveSession"]
    option = compas_rhino.rs.GetString("Session: ", strings=options)

    if not option:
        return
    
    if option == "Restart":
        AGS_restart_cmd.RunCommand(True)
    
    elif option == "LoadSession":
        AGS_session_load_cmd.RunCommand(True)

    elif option == "SaveSession":
        AGS_session_save_cmd.RunCommand(True)


# ==============================================================================
# Main
# ==============================================================================

if __name__ == '__main__':

    RunCommand(True)
