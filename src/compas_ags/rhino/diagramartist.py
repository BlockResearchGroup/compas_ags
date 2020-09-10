from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

from functools import partial
# import compas_rhino
# from compas.geometry import scale_vector
# from compas.geometry import add_vectors
# from compas.geometry import subtract_vectors
# from compas.geometry import centroid_points
# from compas.geometry import distance_point_point
from compas.utilities import color_to_colordict
from compas_rhino.artists import MeshArtist


colordict = partial(color_to_colordict, colorformat='rgb', normalize=False)


# def textdict(text, items):
#     if text is None:
#         item_text = {item: str(item) for item in items}
#     elif isinstance(text, dict):
#         item_text = text
#     elif text == 'key':
#         item_text = {item: str(item) for item in items}
#     elif text == 'index':
#         item_text = {item: str(index) for index, item in enumerate(items)}
#     else:
#         raise NotImplementedError
#     return item_text


__all__ = ['DiagramArtist']


class DiagramArtist(MeshArtist):
    """Base artist for diagrams in AGS.

    Attributes
    ----------
    diagram : :class:`compas_ags.diagrams.Diagram`
        The diagram associated with the artist.

    """

    @property
    def diagram(self):
        """The diagram assigned to the artist."""
        return self.mesh

    @diagram.setter
    def diagram(self, diagram):
        self.mesh = diagram


# ==============================================================================
# Main
# ==============================================================================

if __name__ == "__main__":
    pass
