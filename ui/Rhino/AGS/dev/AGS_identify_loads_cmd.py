from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

import scriptcontext as sc

import compas_rhino


__commandname__ = "AGS_identify_loads"


def RunCommand(is_interactive):

    if 'AGS' not in sc.sticky:
        compas_rhino.display_message('AGS has not been initialised yet.')
        return

    scene = sc.sticky['AGS']['scene']
    form = scene.find_by_name('Form')[0]

    edges = form.select_edges()
    if not edges:
        return

    # rename is_external to _is_external
    # this is not something the user should be allowed to change...
    if not all(form.diagram.edge_attribute(edge, 'is_external') for edge in edges):
        compas_rhino.display_message('All loads have to be external edges.')
        return

    reactions = [(u, v) for u, v in form.diagram.edges_where({'is_external': True}) if (u, v) not in edges and (v, u) not in edges]

    form.diagram.edges_attribute('is_load', False)
    form.diagram.edges_attribute('is_ind', False)
    form.diagram.edges_attribute('is_reaction', False)

    form.diagram.edges_attribute('is_load', True, keys=edges)
    form.diagram.edges_attribute('is_ind', True, keys=edges)
    form.diagram.edges_attribute('is_reaction', True, keys=reactions)

    scene.clear()
    scene.update()


# ==============================================================================
# Main
# ==============================================================================

if __name__ == '__main__':

    RunCommand(True)
