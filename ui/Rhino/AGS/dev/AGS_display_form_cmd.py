from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

import scriptcontext as sc
import rhinoscriptsyntax as rs

import compas_rhino


__commandname__ = "AGS_display_form"


def RunCommand(is_interactive):

    if 'AGS' not in sc.sticky:
        compas_rhino.display_message('AGS has not been initialised yet.')
        return

    scene = sc.sticky['AGS']['scene']

    form = scene.find_by_name('Form')[0]

    options = ["Vertexlabels", "Edgelabels", "ForceMagnitude", "CompressionTension", ]

    while True:
        option = compas_rhino.rs.GetString("FormDiagram Display", strings=options)

        if not option:
            return

        if option == "Vertexlabels":
            current = str(form.artist.settings['show.vertexlabels'])
            show = compas_rhino.rs.GetString("Vertexlabels", defaultString=current, strings=["True", "False"])
            if show == "True":
                form.artist.settings['show.vertexlabels'] = True
            elif show == "False":
                form.artist.settings['show.vertexlabels'] = False

        elif option == "Edgelabels":
            current = str(form.artist.settings['show.edgelabels'])
            show = compas_rhino.rs.GetString("Edgelabels", defaultString=current, strings=["True", "False"])
            if show == "True":
                form.artist.settings['show.edgelabels'] = True
                form.artist.settings['show.edgelabels_force'] = False
            elif show == "False":
                form.artist.settings['show.edgelabels'] = False

        elif option == "ForceMagnitude":
            current = str(form.artist.settings['show.edgelabels_force'])
            show = compas_rhino.rs.GetString("Force Magnitude", defaultString=current, strings=["True", "False"])
            if show == "True":
                form.artist.settings['show.edgelabels_force'] = True
                form.artist.settings['show.edgelabels'] = False
            elif show == "False":
                form.artist.settings['show.edgelabels_force'] = False

        elif option == "CompressionTension":
            current = str(form.artist.settings['show.forces'])
            show = compas_rhino.rs.GetString("Show Compression / Tension", defaultString=current, strings=["True", "False"])
            if show == "True":
                form.artist.settings['show.forces'] = True
            elif show == "False":
                form.artist.settings['show.forces'] = False

        scene.update()


# ==============================================================================
# Main
# ==============================================================================

if __name__ == '__main__':

    RunCommand(True)
