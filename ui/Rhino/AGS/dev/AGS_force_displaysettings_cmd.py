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

    options = ["Vertexlabels", "Edgelabels", "Forcelabels", "CompressionTension", ]

    while True:
        option = compas_rhino.rs.GetString("FormDiagram Display", strings=options)

        if not option:
            return

        if option == "Vertexlabels":
            current = str(force.artist.settings['show.vertexlabels'])
            show = compas_rhino.rs.GetString("Vertex labels", defaultString=current, strings=["True", "False"])
            if show == "True":
                force.artist.settings['show.vertexlabels'] = True
            elif show == "False":
                force.artist.settings['show.vertexlabels'] = False

        elif option == "Edgelabels":
            current = str(force.artist.settings['show.edgelabels'])
            show = compas_rhino.rs.GetString("Edge labels", defaultString=current, strings=["True", "False"])
            if show == "True":
                force.artist.settings['show.edgelabels'] = True
                force.artist.settings['show.forcelabels'] = False
            elif show == "False":
                force.artist.settings['show.edgelabels'] = False

        elif option == "Forcelabels":
            current = str(force.artist.settings['show.forcelabels'])
            show = compas_rhino.rs.GetString("Force labels", defaultString=current, strings=["True", "False"])
            if show == "True":
                force.artist.settings['show.forcelabels'] = True
                force.artist.settings['show.edgelabels'] = False
            elif show == "False":
                force.artist.settings['show.forcelabels'] = False

        elif option == "CompressionTension":
            current = str(force.artist.settings['show.forces'])
            show = compas_rhino.rs.GetString("Compression / Tension", defaultString=current, strings=["True", "False"])
            if show == "True":
                force.artist.settings['show.forces'] = True
            elif show == "False":
                force.artist.settings['show.forces'] = False

        scene.update()


# ==============================================================================
# Main
# ==============================================================================

if __name__ == '__main__':

    RunCommand(True)
