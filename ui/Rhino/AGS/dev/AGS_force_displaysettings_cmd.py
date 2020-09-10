from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

import scriptcontext as sc

import compas_rhino


__commandname__ = "AGS_force_displaysettings"


def RunCommand(is_interactive):

    if 'AGS' not in sc.sticky:
        compas_rhino.display_message('AGS has not been initialised yet.')
        return

    scene = sc.sticky['AGS']['scene']

    objects = scene.find_by_name('Force')
    if not objects:
        compas_rhino.display_message("There is no ForceDiagram in the scene.")
        return
    force = objects[0]

    options = ["VertexLabels", "EdgeLabels", "ForceLabels", "CompressionTension"]

    while True:
        option = compas_rhino.rs.GetString("FormDiagram Display", strings=options)
        if not option:
            return

        if option == "VertexLabels":
            if force.settings['show.vertexlabels'] is True:
                force.settings['show.vertexlabels'] = False
            else:
                force.settings['show.vertexlabels'] = True

        elif option == "EdgeLabels":
            if force.settings['show.edgelabels'] is True:
                force.settings['show.edgelabels'] = False
            else:
                force.settings['show.edgelabels'] = True
                force.settings['show.forcelabels'] = False

        elif option == "ForceLabels":
            if force.settings['show.forcelabels'] is True:
                force.settings['show.forcelabels'] = False
            else:
                force.settings['show.forcelabels'] = True
                force.settings['show.edgelabels'] = False

        elif option == "CompressionTension":
            if force.settings['show.forcecolors'] is True:
                force.settings['show.forcecolors'] = False
            else:
                force.settings['show.forcecolors'] = True

        scene.update()

    scene.save()


# ==============================================================================
# Main
# ==============================================================================

if __name__ == '__main__':

    RunCommand(True)
