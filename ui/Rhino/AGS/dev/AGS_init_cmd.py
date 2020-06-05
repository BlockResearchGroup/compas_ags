from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

import scriptcontext as sc
import compas_rhino

from compas.rpc import Proxy


__commandname__ = "AGS_init"


def RunCommand(is_interactive):
    sc.sticky["AGS"] = {
        'proxy': Proxy(),
        'formdiagram': None,
        'forcediagram': None,
        'settings': {}
    }


# ==============================================================================
# Main
# ==============================================================================

if __name__ == '__main__':

    RunCommand(True)
