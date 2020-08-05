from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

import scriptcontext as sc

import compas_rhino


__commandname__ = "AGS_check_dof"


def RunCommand(is_interactive):

    if 'AGS' not in sc.sticky:
        compas_rhino.display_message('AGS has not been initialised yet.')
        return

    proxy = sc.sticky['AGS']['proxy']
    scene = sc.sticky['AGS']['scene']
    form = scene.find_by_name('Form')[0]

    proxy.package = 'compas_ags.ags.graphstatics'

    dof = proxy.form_count_dof_proxy(form.diagram.data)
    k = dof[0]
    inds = len(list(form.diagram.edges_where({'is_ind': True})))

    if k == inds:
        print('Correct number of loaded edges (%s) selected.' % k)
    elif k > inds:
        compas_rhino.display_message('Warning: Insuficient number of loaded edges selected (%s required and %s selected), solution is not unique.' % (k, inds))
    elif k < inds:
        compas_rhino.display_message('Warning: Too many loaded edges selected (%s required and %s selected), some will be ignored.' % (k, inds))


# ==============================================================================
# Main
# ==============================================================================

if __name__ == '__main__':

    RunCommand(True)
