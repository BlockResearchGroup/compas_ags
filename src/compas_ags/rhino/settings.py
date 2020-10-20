from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

from collections import OrderedDict
import scriptcontext as sc

import Eto.Drawing as drawing
import Eto.Forms as forms
import Rhino.UI


__all__ = ["SettingsForm", "Settings_Tab"]


def get_scene():
    return sc.sticky['AGS']['scene']


class Settings_Tab(forms.TabPage):

    @classmethod
    def from_settings(cls, object_name, settings):
        tab = cls()
        tab.Text = object_name
        layout = forms.StackLayout()
        layout.Spacing = 2
        layout.HorizontalContentAlignment = forms.HorizontalAlignment.Stretch
        tab.Content = layout

        # link to original setting and keep a temporary new settings holder
        tab.settings = settings
        tab.new_settings = settings.copy()

        # create sections
        sections = {}
        for key in settings:
            split = key.split('.')
            prefix = split[0]
            postfix = '.'.join(split[1:])

            if prefix[0] == "_":
                continue

            if prefix not in sections:
                sections[prefix] = {}
            sections[prefix][postfix] = (key, settings[key])

        for prefix in sections:

            groupbox = forms.GroupBox(Text=prefix)
            groupbox.Padding = drawing.Padding(5)
            grouplayout = forms.DynamicLayout()
            grouplayout.Spacing = drawing.Size(3, 3)

            postfixies = list(sections[prefix].keys())
            postfixies.sort()
            for postfix in postfixies:
                key, value = sections[prefix][postfix]

                if type(value) == bool:
                    control = forms.CheckBox()
                    control.Checked = value
                    control.CheckedChanged += tab.EditEvent(key)
                elif (type(value) == list or type(value) == tuple) and len(value) == 3:
                    control = forms.ColorPicker()
                    control.Value = drawing.Color.FromArgb(*value)
                    control.ValueChanged += tab.EditEvent(key)
                elif type(value) == float or type(value) == int:
                    control = forms.NumericUpDown()
                    if type(value) == float:
                        digits = len(str(value).split('.')[-1])
                        control.DecimalPlaces = digits
                        control.Increment = 0.1 ** digits
                    control.Value = value
                    control.ValueChanged += tab.EditEvent(key)
                else:
                    control = forms.TextBox()
                    control.Text = str(value)
                    control.TextChanged += tab.EditEvent(key)

                label = forms.Label(Text=postfix)
                if postfix != '':
                    grouplayout.AddRow(label, None, control)
                else:
                    grouplayout.AddRow(control)

            groupbox.Content = grouplayout
            layout.Items.Add(groupbox)

        return tab

    def EditEvent(self, key):
        def on_edited(sender, event):
            try:
                if isinstance(sender, forms.ColorPicker):
                    color = sender.Value
                    new_value = [int(color.Rb), int(color.Gb), int(color.Bb)]
                elif isinstance(sender, forms.CheckBox):
                    new_value = sender.Checked
                elif isinstance(sender, forms.NumericUpDown):
                    new_value = sender.Value
                elif isinstance(sender, forms.TextBox):
                    new_value = sender.Text

                self.new_settings.update({key: new_value})

            except Exception as e:
                print(e)
        return on_edited

    def apply(self):
        self.settings.update(self.new_settings)


class SettingsForm(forms.Dialog[bool]):

    @classmethod
    def from_scene(cls, scene, object_types=None, global_settings=None):

        all_settings = OrderedDict()

        if global_settings:
            for name in global_settings:
                all_settings[name] = scene.settings[name]

        # pre-populate class default settings
        if object_types:
            for object_type in object_types:  # avoid property objects
                all_settings[object_type.__name__] = object_type.SETTINGS

        # overwite with object setting if added as node
        for key in scene.objects:
            node = scene.objects[key]
            node_type = node.__class__.__name__
            if node_type in all_settings:
                all_settings[node_type] = node.settings

        settingsForm = cls()
        settingsForm.scene = scene
        settingsForm.setup(all_settings)
        Rhino.UI.EtoExtensions.ShowSemiModal(settingsForm, Rhino.RhinoDoc.ActiveDoc, Rhino.UI.RhinoEtoApp.MainWindow)
        return settingsForm

    @classmethod
    def from_settings(cls, settings, name):

        all_settings = {name: settings}
        settingsForm = cls()
        settingsForm.setup(all_settings)
        Rhino.UI.EtoExtensions.ShowSemiModal(settingsForm, Rhino.RhinoDoc.ActiveDoc, Rhino.UI.RhinoEtoApp.MainWindow)
        return settingsForm

    def setup(self, all_settings):

        self.Title = "Settings"
        self.TabControl = self.tabs_from_settings(all_settings)
        tab_items = forms.StackLayoutItem(self.TabControl, True)
        layout = forms.StackLayout()
        layout.Spacing = 5
        layout.HorizontalContentAlignment = forms.HorizontalAlignment.Stretch
        layout.Items.Add(tab_items)

        sub_layout = forms.DynamicLayout()
        sub_layout.Spacing = drawing.Size(5, 0)
        sub_layout.AddRow(None, self.ok, self.cancel, self.apply)
        layout.Items.Add(forms.StackLayoutItem(sub_layout))

        self.Content = layout
        self.Padding = drawing.Padding(12)
        self.Resizable = True

    def tabs_from_settings(self, all_settings):
        control = forms.TabControl()
        control.TabPosition = forms.DockPosition.Top

        for object_name in all_settings:
            tab = Settings_Tab.from_settings(object_name, all_settings[object_name])
            control.Pages.Add(tab)

        return control

    @property
    def ok(self):
        self.DefaultButton = forms.Button(Text='OK')
        self.DefaultButton.Click += self.on_ok
        return self.DefaultButton

    @property
    def cancel(self):
        self.AbortButton = forms.Button(Text='Cancel')
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
                page.apply()
            if hasattr(self, 'scene'):
                self.scene.update()
        except Exception as e:
            print(e)
        self.Close()

    def on_apply(self, sender, event):
        try:
            for page in self.TabControl.Pages:
                page.apply()
            if hasattr(self, 'scene'):
                self.scene.update()
        except Exception as e:
            print(e)

    def on_cancel(self, sender, event):
        self.Close()


if __name__ == "__main__":

    from compas_ags.rhino import FormObject
    from compas_ags.rhino import ForceObject
    scene = get_scene()
    SettingsForm.from_scene(scene, object_types=[FormObject, ForceObject])
    # SettingsForm.from_settings(scene.settings, "solver")
