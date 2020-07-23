from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

import compas_rhino

from compas_ags.rhino.diagramobject import DiagramObject


__all__ = ['FormObject']


class FormObject(DiagramObject):
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
    """

    def unselect(self):
        """Unselect all Rhino objects associated with this diagram object."""
        super(FormObject, self).unselect()
        guids = []
        guids += list(self.artist.guid_force.keys())
        compas_rhino.rs.UnselectObjects(guids)


# ==============================================================================
# Main
# ==============================================================================

if __name__ == '__main__':

    pass
