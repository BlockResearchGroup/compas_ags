from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

import scriptcontext as sc


__commandname__ = "AGS_restart"


def RunCommand(is_interactive):
    if 'AGS' not in sc.sticky:
        print("Initialise the plugin first!")
        return

    AGS = sc.sticky['AGS']

    proxy = AGS['proxy']
    proxy.stop_server()
    proxy.start_server()


# ==============================================================================
# Main
# ==============================================================================

if __name__ == '__main__':

    RunCommand(True)
