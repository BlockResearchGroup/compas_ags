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

    if not form:
        print("There is no FormDiagram in the scene.")
        return

    proxy.package = 'compas_ags.ags.graphstatics'

    dof = proxy.form_count_dof(form.diagram)
    k = dof[0]
    inds = len(list(form.diagram.edges_where({'is_ind': True})))

    if k == inds:
        print('Success: You have identified the correct number of externally applied loads.')
    elif k > inds:
        compas_rhino.display_message('Warning: You have not yet identified all external loads. (%s required and %s selected)' % (k, inds))
    else:
        compas_rhino.display_message('Warning: You have identified too many external forces as loads. (%s required and %s selected)' % (k, inds))


# ==============================================================================
# Main
# ==============================================================================

if __name__ == '__main__':

    RunCommand(True)
