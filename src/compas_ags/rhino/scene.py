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

    def __init__(self, db, depth=10):
        self._current = -1
        self._depth = depth
        self._db = db
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

    def find_by_name(self, name):
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

    def redraw(self):
        """Redraw the entire scene."""
        compas_rhino.rs.EnableRedraw(False)
        try:
            for guid in self.objects:
                self.objects[guid].clear()
                self.objects[guid].draw()
        except Exception:
            pass
        compas_rhino.rs.EnableRedraw(True)
        compas_rhino.rs.Redraw()

    def update(self):
        """Redraw all objects in the scene."""
        self.redraw()
        states = self._db['states']
        if self._current < -1:
            del states[self._current + 1:]
        self._current = -1
        state = []
        for guid, obj in self.objects.items():
            # the definition of a state should be formalised
            # this is equivalent to the data schema of data objects
            # the scene has a state schema
            # whether or not to store a state could be the responsibility of the caller...
            state.append({
                'object': {
                    'name': obj.name,
                    'layer': obj.layer,
                    'visible': obj.visible},
                'diagram': {
                    'type': type(obj.diagram),
                    'data': obj.diagram.to_data()},
                'artist': {
                    'settings': obj.artist.settings,
                    'anchor_vertex': obj.artist.anchor_vertex,
                    'anchor_point': obj.artist.anchor_point,
                    'scale': obj.artist.scale}
            })
        states.append(state)
        if len(states) > self._depth:
            del states[0]
        self._db['states'] = states

    def undo(self):
        """Undo scene updates.

        Returns
        -------
        bool
            False if there is nothing (more) to undo.
            True if undo was successful.
        """
        if self._current <= - self._depth:
            return False
        if len(self._db['states']) < 2:
            return False
        self.clear()
        self._current -= 1
        state = self._db['states'][self._current]
        form = None
        force = None
        for data in state:
            diagram = data['diagram']['type'].from_data(data['diagram']['data'])
            guid = self.add(diagram, **data['object'])
            obj = self.find(guid)
            obj.artist.settings.update(data['artist']['settings'])
            obj.artist.anchor_vertex = data['artist']['anchor_vertex']
            obj.artist.anchor_point = data['artist']['anchor_point']
            obj.artist.scale = data['artist']['scale']
            if obj.name == 'Form':
                form = obj
            elif obj.name == 'Force':
                force = obj
        if form and force:
            form.diagram.dual = force.diagram
            force.diagram.dual = form.diagram
        self.redraw()
        return True

    def redo(self):
        """Redo scene updates.

        Returns
        -------
        bool
            False if there is nothing (more) to redo.
            True if redo was successful.
        """
        if len(self._db['states']) < 2:
            return False
        if self._current >= -1:
            return False
        self.clear()
        self._current += 1
        state = self._db['states'][self._current]
        form = None
        force = None
        for data in state:
            diagram = data['diagram']['type'].from_data(data['diagram']['data'])
            guid = self.add(diagram, **data['object'])
            obj = self.find(guid)
            obj.artist.settings.update(data['artist']['settings'])
            obj.artist.anchor_vertex = data['artist']['anchor_vertex']
            obj.artist.anchor_point = data['artist']['anchor_point']
            obj.artist.scale = data['artist']['scale']
            if obj.name == 'Form':
                form = obj
            elif obj.name == 'Force':
                force = obj
        if form and force:
            form.diagram.dual = force.diagram
            force.diagram.dual = form.diagram
        self.redraw()
        return True


# ==============================================================================
# Main
# ==============================================================================

if __name__ == '__main__':
    pass
