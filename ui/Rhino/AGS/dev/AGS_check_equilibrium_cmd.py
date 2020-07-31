from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

import scriptcontext as sc
import rhinoscriptsyntax as rs

import compas_rhino

# check the degree of freedom

__commandname__ = "AGS_check_equilibrium"


def RunCommand(is_interactive):

    if 'AGS' not in sc.sticky:
        compas_rhino.display_message('AGS has not been initialised yet.')
        return

    proxy = sc.sticky['AGS']['proxy']
    scene = sc.sticky['AGS']['scene']
    form = scene.find_by_name('Form')[0]

    proxy.package = 'compas_ags.ags.graphstatics'

    k, m = proxy.form_count_dof_proxy(form.diagram.data)

    if k == 0 and m == 0: 
        compas_rhino.display_message('the system is statically determined.')
    elif k > 0 and m == 0:
        compas_rhino.display_message('the system is statically indetermined with %s independent states of stress.' % k)
    elif k ==0 and m > 0:
        compas_rhino.display_message('the system is unstable with %s independent mechanisms.' % m)


# ==============================================================================
# Main
# ==============================================================================

if __name__ == '__main__':

    RunCommand(True)
