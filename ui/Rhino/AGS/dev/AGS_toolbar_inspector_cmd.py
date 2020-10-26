from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

import scriptcontext as sc

import compas_rhino

import AGS_edges_table_cmd
import AGS_edge_information_cmd
import AGS_form_inspector_control_cmd


__commandname__ = "AGS_toolbar_inspector"


def RunCommand(is_interactive):

    if 'AGS' not in sc.sticky:
        compas_rhino.display_message('AGS has not been initialised yet.')
        return

    options = ["EdgesTable", "EdgeInformation", "ForcePolygons"]
    option = compas_rhino.rs.GetString("Create Form:", strings=options)

    if not option:
        return

    if option == "EdgesTable":
        AGS_edges_table_cmd.RunCommand(True)

    elif option == "EdgeInformation":
        AGS_edge_information_cmd.RunCommand(True)

    elif option == "ForcePolygons":
        AGS_form_inspector_control_cmd.RunCommand(True)


# ==============================================================================
# Main
# ==============================================================================

if __name__ == '__main__':

    RunCommand(True)
