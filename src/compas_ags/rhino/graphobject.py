from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

from compas_ags.rhino.diagramobject import DiagramObject


__all__ = ['GraphObject']


class GraphObject(DiagramObject):
    """A graph object represents an input graph in the Rhino view.
    """

    def unselect(self):
        """Unselect all Rhino objects associated with this diagram object."""
        super(GraphObject, self).unselect()


# ==============================================================================
# Main
# ==============================================================================

if __name__ == '__main__':

    pass
