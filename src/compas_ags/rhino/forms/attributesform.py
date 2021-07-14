from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

import ast

import rhinoscriptsyntax as rs
import scriptcontext as sc
import Eto.Drawing as drawing
import Eto.Forms as forms
import Rhino

find_object = sc.doc.Objects.Find


__all__ = ["AttributesForm"]


def get_scene():
    return sc.sticky['AGS']['scene']


class Tree_Table(forms.TreeGridView):
    def __init__(self, ShowHeader=True, sceneNode=None, table_type=None):
        self.ShowHeader = ShowHeader
        self.Height = 300
        self.last_sorted_to = None
        self.table_type = table_type
        self.sceneNode = sceneNode
        self.to_update = {}
        # self.AllowMultipleSelection=True

        # give colors to each item cells according to object settings
        color = {}
        if sceneNode and table_type:
            settings = sceneNode.settings

            # print(sceneNode.settings)

            # update general color settings for this table
            general_setting_key = "color.%s" % table_type

            if getattr(sceneNode.diagram, table_type):
                color.update({str(key): settings.get(general_setting_key) for key in getattr(sceneNode.diagram, table_type)()})

            # gather and update subsettings
            for full_setting_key in settings:
                sub_setting_str = full_setting_key.split(":")
                if len(sub_setting_str) > 1 and sub_setting_str[0] == general_setting_key:
                    sub_setting_key = sub_setting_str[-1]
                    items_where = getattr(sceneNode.diagram, '%s_where' % table_type)
                    color.update({str(key): settings.get(full_setting_key) for key in items_where({sub_setting_key: True})})
                    color.update({str(key): settings.get(full_setting_key) for key in items_where({'_'+sub_setting_key: True})})  # including read-only ones
                    color.update({str(key): settings.get("color.edges:is_ind") for key in items_where({"is_ind": True})})  # overwrite is_ind lastly

            # Additional settings for AGS
            tol = 0.001
            for edge in sceneNode.diagram.edges_where({'is_external': False}):
                if sceneNode.diagram.edge_attribute(edge, 'f') > + tol:
                    color[str(edge)] = settings['color.tension']
                if sceneNode.diagram.edge_attribute(edge, 'f') < - tol:
                    color[str(edge)] = settings['color.compression']

        def OnCellFormatting(sender, e):
            try:
                attr = e.Column.HeaderText

                # if not e.Column.Editable and attr != 'key':
                #     e.ForegroundColor = drawing.Colors.DarkGray

                if attr == 'EdgeLabel':
                    key = e.Item.Values[1]
                    if key in color:
                        rgb = color[key]
                        rgb = [c/255. for c in rgb]
                        e.BackgroundColor = drawing.Color(*rgb)

            except Exception as exc:
                print('formating error', exc)

        self.CellFormatting += OnCellFormatting

    @classmethod
    def create_force_table(cls, sceneNode, dual=[]):
        datastructure = sceneNode.diagram
        table = cls(sceneNode=sceneNode, table_type='edges')
        table.add_column('EdgeLabel')
        table.add_column('Vertices')

        attributes = list(datastructure.default_edge_attributes.keys())
        attributes = table.sort_attributes(attributes)

        Allowed = ["is_ind", "f", "is_external"]
        attributes = filter(lambda attr: attr in Allowed, attributes)

        for attr in attributes:
            checkbox = type(datastructure.default_edge_attributes[attr]) == bool
            attr = attr.replace("_", "-")
            table.add_column(attr, Editable=False, checkbox=checkbox)

        treecollection = forms.TreeGridItemCollection()
        for index, edge in enumerate(datastructure.edges()):
            values = [index, str(edge)]

            for attr in attributes:
                value = datastructure.edge_attribute(edge, attr)
                if isinstance(value, float):
                    value = float("%.4g" % (value))
                values.append(value)

            edge_item = forms.TreeGridItem(Values=tuple(values))
            treecollection.Add(edge_item)
            # for key in edge:
            #     vertex_item = forms.TreeGridItem(Values=(str(key),))
            #     edge_item.Children.Add(vertex_item)

        table.DataStore = treecollection
        table.Activated += table.SelectEvent(sceneNode, 'guid_edge', dual=dual)
        table.ColumnHeaderClick += table.HeaderClickEvent()
        table.CellEdited += table.EditEvent()
        return table

    @classmethod
    def create_vertices_table(cls, sceneNode):
        datastructure = sceneNode.datastructure
        table = cls(sceneNode=sceneNode, table_type='vertices')
        table.add_column('key')
        attributes = list(datastructure.default_vertex_attributes.keys())
        attributes = table.sort_attributes(attributes)
        for attr in attributes:
            editable = attr[0] != '_'
            checkbox = type(datastructure.default_vertex_attributes[attr]) == bool
            if not editable:
                attr = attr[1:]
            table.add_column(attr, Editable=editable, checkbox=checkbox)
        treecollection = forms.TreeGridItemCollection()
        for key in datastructure.vertices():
            values = [str(key)]
            for attr in attributes:
                values.append(str(datastructure.vertex_attribute(key, attr)))
            treecollection.Add(forms.TreeGridItem(Values=tuple(values)))
        table.DataStore = treecollection
        table.Activated += table.SelectEvent(sceneNode, 'guid_vertex')
        table.ColumnHeaderClick += table.HeaderClickEvent()
        table.CellEdited += table.EditEvent()
        return table

    @classmethod
    def create_edges_table(cls, sceneNode):
        datastructure = sceneNode.datastructure
        table = cls(sceneNode=sceneNode, table_type='edges')
        table.add_column('key')
        attributes = list(datastructure.default_edge_attributes.keys())
        attributes = table.sort_attributes(attributes)

        for attr in attributes:
            editable = attr[0] != '_'
            checkbox = type(datastructure.default_edge_attributes[attr]) == bool
            if not editable:
                attr = attr[1:]
            table.add_column(attr, Editable=editable, checkbox=checkbox)

        treecollection = forms.TreeGridItemCollection()
        for key, edge in enumerate(datastructure.edges()):
            values = [str(edge)]
            for attr in attributes:
                values.append(datastructure.edge_attribute(edge, attr))
            edge_item = forms.TreeGridItem(Values=tuple(values))
            treecollection.Add(edge_item)
            for key in edge:
                vertex_item = forms.TreeGridItem(Values=(str(key),))
                edge_item.Children.Add(vertex_item)
        table.DataStore = treecollection
        table.Activated += table.SelectEvent(sceneNode, 'guid_edge', 'guid_vertex')
        table.ColumnHeaderClick += table.HeaderClickEvent()
        table.CellEdited += table.EditEvent()
        return table

    def sort_attributes(self, attributes):
        sorted_attributes = attributes[:]
        sorted_attributes.sort()

        switch = len(sorted_attributes)
        for i, attr in enumerate(sorted_attributes):
            if attr[0] != '_':
                switch = i
                break
        sorted_attributes = sorted_attributes[switch:] + sorted_attributes[:switch]

        return sorted_attributes

    def SelectEvent(self, sceneNode, guid_field, children_guid_field=None, dual=None):
        def on_selected(sender, event):
            try:
                rs.UnselectAllObjects()
                key = event.Item.Values[1]
                guid2key = getattr(sceneNode, guid_field)
                key2guid = {str(guid2key[guid]): guid for guid in guid2key}
                if key in key2guid:
                    find_object(key2guid[key]).Select(True)

                if dual:
                    force_edge_index = int(event.Item.Values[0])
                    force_edge_key2index = dual.diagram.edge_index(dual.diagram.dual)
                    force_edge_index2key = {force_edge_key2index[key]: key for key in force_edge_key2index}
                    force_edge_key = force_edge_index2key[force_edge_index]

                    guid2key = getattr(dual, guid_field)
                    key2guid = {guid2key[guid]: guid for guid in guid2key}
                    key2guid.update({(v, u): key2guid[(u, v)] for u, v in key2guid})
                    if force_edge_key in key2guid:
                        find_object(key2guid[force_edge_key]).Select(True)

                # elif children_guid_field:
                #     if key == '':
                #         key = event.Item.Values[1]
                #     guid2key = getattr(sceneNode.artist, children_guid_field)
                #     key2guid = {str(guid2key[guid]): guid for guid in guid2key}
                #     find_object(key2guid[key]).Select(True)

                # print('selected', key, key2guid[key])
                rs.Redraw()
            except Exception as e:
                print(e)

        return on_selected

    def EditEvent(self):
        def on_edited(sender, event):
            try:
                key = event.Item.Values[0]
                value = event.Item.Values[event.Column]
                attr = self.Columns[event.Column].HeaderText

                if self.table_type == 'vertices':
                    get_set_attributes = getattr(self.sceneNode.datastructure, 'vertex_attribute')
                if self.table_type == 'edges':
                    get_set_attributes = getattr(self.sceneNode.datastructure, 'edge_attribute')
                if self.table_type == 'faces':
                    get_set_attributes = getattr(self.sceneNode.datastructure, 'face_attribute')

                try:
                    new_value = ast.literal_eval(str(value))  # checkboxes value type is bool, turn them into str first to be parsed back to bool
                except Exception:
                    new_value = str(value)

                # convert key from str to original type: int,tuple...
                try:
                    key = ast.literal_eval(key)
                except Exception:
                    pass

                original_value = get_set_attributes(key, attr)

                if type(original_value) == float and type(new_value) == int:
                    new_value = float(new_value)
                if new_value != original_value:
                    if type(new_value) == type(original_value):
                        print('will update key: %s, attr: %s, value: %s' % (key, attr, new_value))
                        self.to_update[(key, attr)] = (get_set_attributes, new_value)
                    else:
                        print('invalid value type, needs: %s, got %s instead' % (type(original_value), type(new_value)))
                        event.Item.Values[event.Column] = original_value
                else:
                    print('value not changed from', original_value)

            except Exception as e:
                print("cell edit failed:", type(e), e)
        return on_edited

    def HeaderClickEvent(self):
        def on_hearderClick(sender, event):
            try:
                # print(event.Column.HeaderText)
                sender.sort(event.Column.HeaderText)
            except Exception as e:
                print(e)
        return on_hearderClick

    def add_column(self, HeaderText=None, Editable=False, checkbox=False):
        column = forms.GridColumn()
        if self.ShowHeader:
            column.HeaderText = HeaderText
        column.Editable = Editable
        if not checkbox:
            column.DataCell = forms.TextBoxCell(self.Columns.Count)
        else:
            column.DataCell = forms.CheckBoxCell(self.Columns.Count)
        column.Sortable = True
        self.Columns.Add(column)

    def sort(self, key):
        headerTexts = [column.HeaderText for column in self.Columns]
        index = headerTexts.index(key)
        print(key, index)

        def getValue(item):
            try:
                value = ast.literal_eval(item.Values[index])
            except (ValueError, TypeError):
                value = item.Values[index]
            return value

        items = sorted(self.DataStore, key=getValue, reverse=True)
        if self.last_sorted_to == key:
            items.reverse()
            self.last_sorted_to = None
        else:
            self.last_sorted_to = key

        self.DataStore = forms.TreeGridItemCollection(items)

    def apply(self):
        for _key in self.to_update:
            get_set_attributes, new_value = self.to_update[_key]
            key, attr = _key
            get_set_attributes(key, attr, new_value)


class Tree_Tab(forms.TabPage):

    @classmethod
    def from_sceneNode(cls, sceneNode, tab_type, dual=None):
        tab = cls()
        tab.Text = tab_type
        # create_table = getattr(Tree_Table, "create_%s_table" % tab_type)
        tab.Content = Tree_Table.create_force_table(sceneNode, dual=dual)
        return tab

    def apply(self):
        self.Content.apply()


class AttributesForm(forms.Dialog[bool]):

    @classmethod
    def from_sceneNode(cls, sceneNode, dual=None):
        attributesForm = cls()
        attributesForm.setup(sceneNode, dual=dual)
        Rhino.UI.EtoExtensions.ShowSemiModal(attributesForm, Rhino.RhinoDoc.ActiveDoc, Rhino.UI.RhinoEtoApp.MainWindow)
        return attributesForm

    def setup(self, sceneNode, dual=None):
        self.Title = "Attributes"
        self.sceneNode = sceneNode

        control = forms.TabControl()
        control.TabPosition = forms.DockPosition.Top

        tab = Tree_Tab.from_sceneNode(sceneNode, 'Edges', dual=dual)
        control.Pages.Add(tab)

        self.TabControl = control

        tab_items = forms.StackLayoutItem(self.TabControl, True)
        layout = forms.StackLayout()
        layout.Spacing = 5
        layout.HorizontalContentAlignment = forms.HorizontalAlignment.Stretch
        layout.Items.Add(tab_items)

        sub_layout = forms.DynamicLayout()
        sub_layout.Spacing = drawing.Size(5, 0)
        # sub_layout.AddRow(None, self.ok, self.cancel, self.apply)
        sub_layout.AddRow(None, self.cancel)
        layout.Items.Add(forms.StackLayoutItem(sub_layout))

        self.Content = layout
        self.Padding = drawing.Padding(12)
        self.Resizable = True
        self.ClientSize = drawing.Size(400, 600)

    @property
    def ok(self):
        self.DefaultButton = forms.Button(Text='OK')
        self.DefaultButton.Click += self.on_ok
        return self.DefaultButton

    @property
    def cancel(self):
        # self.AbortButton = forms.Button(Text='Cancel')
        self.AbortButton = forms.Button(Text='Close')
        self.AbortButton.Click += self.on_cancel
        return self.AbortButton

    @property
    def apply(self):
        self.ApplyButton = forms.Button(Text='Apply')
        self.ApplyButton.Click += self.on_apply
        return self.ApplyButton

    def on_ok(self, sender, event):
        try:
            for page in self.TabControl.Pages:
                if hasattr(page, 'apply'):
                    page.apply()
            get_scene().update()
        except Exception as e:
            print(e)
        self.Close()

    def on_apply(self, sender, event):
        try:
            for page in self.TabControl.Pages:
                if hasattr(page, 'apply'):
                    page.apply()
            get_scene().update()
        except Exception as e:
            print(e)

    def on_cancel(self, sender, event):
        self.Close()


if __name__ == "__main__":

    scene = get_scene()
    form = scene.find_by_name("Form")[0]
    force = scene.find_by_name("Force")[0]
    AttributesForm.from_sceneNode(form, dual=force)
