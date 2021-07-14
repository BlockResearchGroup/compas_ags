from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

import os

import System
import Eto.Drawing as drawing
import Eto.Forms as forms
import Rhino
import compas


class BrowserForm(forms.Form):

    def __init__(self, url=None, width=800, height=400):
        self.Owner = Rhino.UI.RhinoEtoApp.MainWindow
        self.Title = 'RhinoVault2'
        self.Padding = drawing.Padding(0)
        self.Resizable = False

        self.m_webview = forms.WebView()
        self.m_webview.Size = drawing.Size(width, height)

        if not url:
            url = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'src', 'index.html')
        self.m_webview.Url = System.Uri(url)
        self.m_webview.BrowserContextMenuEnabled = True

        layout = forms.DynamicLayout()
        layout.Spacing = drawing.Size(5, 5)
        layout.BeginVertical()
        layout.AddRow(self.m_webview)
        layout.EndVertical()
        self.Content = layout

        self.WindowStyle = forms.WindowStyle.None  # noqa E999
        self.m_webview.DocumentLoading += self.action
        if compas.WINDOWS:
            self.Location = drawing.Point(self.Owner.Location.X + self.Owner.Size.Width / 2 - 400, self.Owner.Location.Y + self.Owner.Size.Height / 2 - 200)

    def action(self, sender, e):
        if e.Uri.Scheme == "action" and e.Uri.Host == "close":
            self.Close()


def Browser():
    browserForm = BrowserForm()
    browserForm.Show()


if __name__ == "__main__":
    Browser()
