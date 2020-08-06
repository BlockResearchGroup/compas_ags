from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

import scriptcontext as sc
import compas_rhino


__commandname__ = "AGS_form_fix_nodes"


def RunCommand(is_interactive):

    if 'AGS' not in sc.sticky:
        compas_rhino.display_message('AGS has not been initialised yet.')
        return

    scene = sc.sticky['AGS']['scene']
    form = scene.find_by_name('Form')[0]

    # select fixed vertices
    while True:
        vertices = form.select_vertices()
        if not vertices:
            break
        fixed = []
        unfixed = []
        for vertex in vertices:
            if form.diagram.vertex_attribute(vertex, 'is_fixed') is True:
                form.diagram.vertex_attribute(vertex, 'is_fixed', False)
                unfixed.append(vertex)
            else:
                form.diagram.vertex_attribute(vertex, 'is_fixed', True)
                fixed.append(vertex)
        scene.update()
        if fixed and unfixed: 
            print(fixed, 'nodes are fixed,', unfixed, 'nodes are unfixed') 
        if fixed and not unfixed:
            print(fixed, 'nodes are fixed')
        if unfixed and not fixed:
            print(unfixed, 'nodes are unfixed')


# ==============================================================================
# Main
# ==============================================================================

if __name__ == '__main__':

    RunCommand(True)
