from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

from compas_ags.rhino.formartist import FormArtist


__all__ = ['FormObject']


class FormObject(object):
    """A form object represents a form diagram in the Rhino model space.

    Parameters
    ----------
    diagram : :class:`compas_ags.diagrams.FormDiagram`
        The form diagram instance.
    settings : dict, optional
        Visualisation settings for the corresponding Rhino object(s).
        Default is ``None``, in which case the default settings of the artist are used.

    Attributes
    ----------
    item : :class:`compas_ags.diagrams.FormDiagram`
        Stores the form diagram instance.
    diagram : :class:`compas_ags.diagrams.FormDiagram`
        Alias for ``item``.
    artist : :class:`compas_ags.rhino.FormArtist`.
        Instance of a form diagram artist.

    Notes
    -----
    The form diagram object is responsible for managing a form diagram in a Rhino scene.

    """

    def __init__(self, diagram, settings=None, **kwargs):
        self.item = diagram
        self.artist = FormArtist(self.item, settings=settings, **kwargs)

    @property
    def diagram(self):
        return self.item

    @diagram.setter
    def diagram(self, diagram):
        self.item = diagram

    def draw(self):
        self.artist.draw()

    def clear(self):
        self.artist.clear_layer()
        self.artist.clear()


# ==============================================================================
# Main
# ==============================================================================

if __name__ == '__main__':

    pass
