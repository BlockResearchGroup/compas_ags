from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

from uuid import uuid4

import compas_rhino
from compas_ags.rhino.diagramobject import DiagramObject


__all__ = ['Scene']


class Scene(object):
    """A Rhino scene for AGS.

    Attributes
    ----------
    objects : dict
        Mapping between GUIDs and diagram objects added to the scene.
        The GUIDs are automatically generated and assigned.

    Examples
    --------
    .. code-block:: python

        from compas_ags.diagrams import FormGraph
        from compas_ags.diagrams import FormDiagram

        from compas_ags.rhino import Scene

        graph = FormGraph.from_obj(FILE)
        form = FormDiagram.from_graph(graph)

        scene = Scene()

        guid = scene.add(form, name="Form", layer="AGS::FormDiagram")
        form = scene.find(guid)

        scene.clear()
        scene.update()

    """

    def __init__(self):
        self.objects = {}

    def add(self, item, name=None, layer=None, visible=None, settings=None):
        """Add an object to the scene matching the provided item.

        Parameters
        ----------
        item : :class:`compas_ags.diagrams.Diagram`
        name : str, optional
        layer : str, optional
        visible : bool, optional
        settings : dict, optional

        Returns
        -------
        GUID
        """
        guid = uuid4()
        obj = DiagramObject.build(item, scene=self, name=name, layer=layer, visible=visible, settings=settings)
        self.objects[guid] = obj
        return guid

    def find(self, guid):
        """Find an object using its GUID.

        Parameters
        ----------
        guid : str

        Returns
        -------
        :class:`compas_ags.rhino.DiagramObject`
        """
        if guid in self.objects:
            return self.objects[guid]

    def find_by_name(self,  name):
        """Find an object using its name.

        Parameters
        ----------
        name : str

        Returns
        -------
        list of :class:`compas_ags.rhino.DiagramObject`
        """
        objects = []
        for obj in self.objects.values():
            if obj.name == name:
                objects.append(obj)
        return objects

    def clear(self):
        """Clear all objects from the scene."""
        compas_rhino.rs.EnableRedraw(False)
        try:
            for guid in list(self.objects.keys()):
                self.objects[guid].clear()
                del self.objects[guid]
        except Exception:
            pass
        compas_rhino.rs.EnableRedraw(True)
        compas_rhino.rs.Redraw()

    def update(self):
        """Redraw all objects in the scene."""
        compas_rhino.rs.EnableRedraw(False)
        try:
            for guid in self.objects:
                self.objects[guid].clear()
                self.objects[guid].draw()
        except Exception:
            pass
        compas_rhino.rs.EnableRedraw(True)
        compas_rhino.rs.Redraw()


# ==============================================================================
# Main
# ==============================================================================

if __name__ == '__main__':
    pass
