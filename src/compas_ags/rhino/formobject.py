from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

import compas_rhino
from compas_ags.rhino.diagramobject import DiagramObject


__all__ = ['FormObject']


class FormObject(DiagramObject):
    """A form object represents a form diagram in the Rhino model space.
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
