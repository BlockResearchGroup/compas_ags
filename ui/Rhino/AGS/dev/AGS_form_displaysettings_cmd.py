from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

import scriptcontext as sc

import compas_rhino


__commandname__ = "AGS_form_displaysettings"


def RunCommand(is_interactive):

    if 'AGS' not in sc.sticky:
        compas_rhino.display_message('AGS has not been initialised yet.')
        return

    scene = sc.sticky['AGS']['scene']

    objects = scene.find_by_name('Form')
    if not objects:
        compas_rhino.display_message("There is no FormDiagram in the scene.")
        return
    form = objects[0]

    options = ["VertexLabels", "EdgeLabels", "ForceLabels", "CompressionTension", "AxialForces", "AxialForceScale"]

    while True:
        option = compas_rhino.rs.GetString("FormDiagram Display", strings=options)
        if not option:
            return

        if option == "VertexLabels":
            if form.settings['show.vertexlabels'] is True:
                form.settings['show.vertexlabels'] = False
            else:
                form.settings['show.vertexlabels'] = True

        elif option == "EdgeLabels":
            if form.settings['show.edgelabels'] is True:
                form.settings['show.edgelabels'] = False
            else:
                form.settings['show.edgelabels'] = True
                form.settings['show.forcelabels'] = False

        elif option == "ForceLabels":
            if form.settings['show.forcelabels'] is True:
                form.settings['show.forcelabels'] = False
            else:
                form.settings['show.forcelabels'] = True
                form.settings['show.edgelabels'] = False

        elif option == "CompressionTension":
            if form.settings['show.forcecolors'] is True:
                form.settings['show.forcecolors'] = False
            else:
                form.settings['show.forcecolors'] = True

        elif option == "AxialForces":
            if form.settings['show.forcepipes'] is True:
                form.settings['show.forcepipes'] = False
            else:
                form.settings['show.forcepipes'] = True

        elif option == "AxialForceScale":
            scale = compas_rhino.rs.GetReal("Scale Forces", form.settings['scale.forces'])
            scale = float(scale)
            form.settings['scale.forces'] = scale

        else:
            raise NotImplementedError

        scene.update()

    scene.save()


# ==============================================================================
# Main
# ==============================================================================

if __name__ == '__main__':

    RunCommand(True)
