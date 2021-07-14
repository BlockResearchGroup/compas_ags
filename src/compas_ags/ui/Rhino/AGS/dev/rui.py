import os
import json
import uuid
import base64
from xml.etree import ElementTree as ET
from xml.dom import minidom

TPL_RUI = """<?xml version="1.0" encoding="utf-8"?>
<RhinoUI major_ver="2"
         minor_ver="0"
         guid="{0}"
         localize="False"
         default_language_id="1033">
    <extend_rhino_menus>
        <menu guid="{1}">
          <text>
            <locale_1033>Extend Rhino Menus</locale_1033>
          </text>
        </menu>
    </extend_rhino_menus>
    <menus />
    <tool_bar_groups />
    <tool_bars />
    <macros />
    <bitmaps>
        <small_bitmap item_width="16" item_height="16">
            <bitmap>iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAYAAAAf8/9hAAAABGdBTUEAALGPC/xhBQAAAAlwSFlz
AAAOvAAADrwBlbxySQAAABNJREFUOE9jGAWjYBSMAjBgYAAABBAAAadEfGMAAAAASUVORK5CYIIA
AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA==</bitmap>
        </small_bitmap>
        <normal_bitmap item_width="24" item_height="24">
            <bitmap>iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAYAAAAf8/9hAAAABGdBTUEAALGPC/xhBQAAAAlwSFlz
AAAOvAAADrwBlbxySQAAABNJREFUOE9jGAWjYBSMAjBgYAAABBAAAadEfGMAAAAASUVORK5CYIIA
AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA==</bitmap>
        </normal_bitmap>
        <large_bitmap item_width="32" item_height="32">
            <bitmap>iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAYAAAAf8/9hAAAABGdBTUEAALGPC/xhBQAAAAlwSFlz
AAAOvAAADrwBlbxySQAAABNJREFUOE9jGAWjYBSMAjBgYAAABBAAAadEfGMAAAAASUVORK5CYIIA
AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA==</bitmap>
        </large_bitmap>
    </bitmaps>
    <scripts />
</RhinoUI>
"""

TPL_BITMAP_ITEM = """
<bitmap_item guid="{0}" index="{1}" />
"""

TPL_MACRO_ICON = """
<macro_item guid="{0}" bitmap_id="{7}">
    <text>
        <locale_1033>{1}</locale_1033>
    </text>
    <script>{2}</script>
    <tooltip>
        <locale_1033>{3}</locale_1033>
    </tooltip>
    <help_text>
        <locale_1033>{4}</locale_1033>
    </help_text>
    <button_text>
        <locale_1033>{5}</locale_1033>
    </button_text>
    <menu_text>
        <locale_1033>{6}</locale_1033>
    </menu_text>
</macro_item>
"""

TPL_MACRO = """
<macro_item guid="{0}">
    <text>
        <locale_1033>{1}</locale_1033>
    </text>
    <script>{2}</script>
    <tooltip>
        <locale_1033>{3}</locale_1033>
    </tooltip>
    <help_text>
        <locale_1033>{4}</locale_1033>
    </help_text>
    <button_text>
        <locale_1033>{5}</locale_1033>
    </button_text>
    <menu_text>
        <locale_1033>{6}</locale_1033>
    </menu_text>
</macro_item>
"""

TPL_MENUITEM = """
<menu_item guid="{0}" item_type="normal">
    <macro_id>{1}</macro_id>
</menu_item>
"""

TPL_MENUSEPARATOR = """
<menu_item guid="{0}" item_type="separator"></menu_item>
"""

TPL_TOOLBARITEM = """
<tool_bar_item guid="{0}" button_style="normal">
    <left_macro_id>{1}</left_macro_id>
    <right_macro_id>{2}</right_macro_id>
</tool_bar_item>
"""

TPL_TOOLBARSEPARATOR = """
<tool_bar_item guid="{0}" button_display_mode="control_only" button_style="spacer">
</tool_bar_item>
"""

TPL_TOOLBAR = """
<tool_bar guid="{0}" item_display_style="{2[item_display_style]}">
    <text>
        <locale_1033>{1}</locale_1033>
    </text>
</tool_bar>
"""

TPL_TOOLBARGROUP = """
<tool_bar_group guid="{0}"
                dock_bar_guid32=""
                dock_bar_guid64=""
                active_tool_bar_group=""
                single_file="{2[single_file]}"
                hide_single_tab="{2[hide_single_tab]}"
                point_floating="0,0">
    <text>
        <locale_1033>{1}</locale_1033>
    </text>
</tool_bar_group>
"""

TPL_TOOLBARGROUPITEM = """
<tool_bar_group_item guid="{0}" major_version="1" minor_version="1">
    <text>
        <locale_1033>{1}</locale_1033>
    </text>
    <tool_bar_id>{2}</tool_bar_id>
</tool_bar_group_item>
"""


class Rui(object):
    """Class for generating *.rui files.

    Parameters
    ----------
    filepath : str
        Path to the *.rui file.

    """

    def __init__(self, filepath):
        self.filepath = filepath
        self.icons = []
        self.macros = {}
        self.toolbars = {}
        self.xml = None
        self.root = None
        self.root_bitmaps = []
        self.root_macros = []
        self.root_menus = []
        self.root_toolbargroups = []
        self.root_toolbars = []
        self.check()

    def check(self):
        if not os.path.exists(os.path.dirname(self.filepath)):
            try:
                os.makedirs(os.path.dirname(self.filepath))
            except OSError as e:
                if e.errno != os.errno.EEXIST:
                    raise e
        if not os.path.exists(self.filepath):
            with open(self.filepath, "w+"):
                pass

    def init(self):
        with open(self.filepath, "w+") as f:
            f.write(TPL_RUI.format(uuid.uuid4(), uuid.uuid4()))
        self.xml = ET.parse(self.filepath)
        self.root = self.xml.getroot()
        self.root_bitmaps = self.root.find("bitmaps")
        self.root_macros = self.root.find("macros")
        self.root_menus = self.root.find("menus")
        self.root_toolbargroups = self.root.find("tool_bar_groups")
        self.root_toolbars = self.root.find("tool_bars")

    def parse(self):
        raise NotImplementedError

    def write(self):
        root = ET.tostring(self.root)
        xml = minidom.parseString(root).toprettyxml(indent="  ")
        xml = "\n".join([line for line in xml.split("\n") if line.strip()])
        with open(self.filepath, "w+") as fh:
            fh.write(xml)

    # --------------------------------------------------------------------------
    # add icons
    # --------------------------------------------------------------------------

    def add_bitmap(self, path):
        with open(path, "rb") as f:
            bitmap = base64.b64encode(f.read()).decode("utf-8")
        self.root_bitmaps.find("large_bitmap").find("bitmap").text = bitmap

    def add_bitmap_items(self, items):
        small = self.root_bitmaps.find("small_bitmap")
        normal = self.root_bitmaps.find("normal_bitmap")
        large = self.root_bitmaps.find("large_bitmap")
        for index, name in enumerate(items):
            guid = str(uuid.uuid4())
            s = TPL_BITMAP_ITEM.format(guid, index)
            e = ET.fromstring(s)
            small.append(e)
            normal.append(e)
            large.append(e)
            self.icons.append(guid)

    # --------------------------------------------------------------------------
    # add macros
    # --------------------------------------------------------------------------

    def add_macros(self, macros):
        for macro in macros:
            guid = str(uuid.uuid4())
            name = macro["name"]
            script = macro["script"]
            tooltip = macro.get("tooltip", "")
            help_text = macro.get("help_text", "")
            button_text = macro.get("button_text", name)
            menu_text = macro.get("menu_text", name.replace("_", " "))
            icon_index = macro.get("icon")
            self.add_macro(name, guid, script, tooltip, help_text, button_text, menu_text, icon_index)

    def add_macro(self, name, guid, script, tooltip, help_text, button_text, menu_text, icon_index=None):
        if icon_index is not None:
            icon_guid = self.icons[icon_index]
            s_macro = TPL_MACRO_ICON.format(guid, name, script, tooltip, help_text, button_text, menu_text, icon_guid)
        else:
            s_macro = TPL_MACRO.format(guid, name, script, tooltip, help_text, button_text, menu_text)
        e_macro = ET.fromstring(s_macro)
        self.root_macros.append(e_macro)
        self.macros[name] = e_macro

    # --------------------------------------------------------------------------
    # add menus
    # --------------------------------------------------------------------------

    def add_menus(self, menus):
        for menu in menus:
            self.add_menu(menu)

    def add_menu(self, menu, root=None):
        if root is None:
            root = self.root_menus
        e_menu = ET.SubElement(root, "menu")
        e_menu.set("guid", str(uuid.uuid4()))
        e_text = ET.SubElement(e_menu, "text")
        e_locale = ET.SubElement(e_text, "locale_1033")
        e_locale.text = menu["name"]
        for item in menu["items"]:
            if "command" in item:
                e_macro = self.macros[item["command"]]
                macro_guid = e_macro.attrib["guid"]
                self.add_menuitem(e_menu, macro_guid)
            elif "items" in item:
                self.add_menu(item, root=e_menu)
            elif item.get("type") == "separator":
                self.add_menuseparator(e_menu)

    def add_menuitem(self, root, macro_id):
        guid = uuid.uuid4()
        s_item = TPL_MENUITEM.format(guid, macro_id)
        e_item = ET.fromstring(s_item)
        root.append(e_item)

    def add_menuseparator(self, root):
        guid = uuid.uuid4()
        s_sep = TPL_MENUSEPARATOR.format(guid)
        e_sep = ET.fromstring(s_sep)
        root.append(e_sep)

    # --------------------------------------------------------------------------
    # add toolbars
    # --------------------------------------------------------------------------

    def add_toolbars(self, toolbars):
        for toolbar in toolbars:
            self.add_toolbar(toolbar)

    def add_toolbar(self, toolbar):
        options = {
            "item_display_style": "control"
        }
        guid = uuid.uuid4()
        s_tb = TPL_TOOLBAR.format(guid, toolbar["name"], options)
        e_tb = ET.fromstring(s_tb)
        self.root_toolbars.append(e_tb)
        self.toolbars[toolbar["name"]] = e_tb
        for item in toolbar["items"]:
            if item.get("type") == "separator":
                self.add_toolbarseparator(e_tb)
                continue
            left_guid = None
            left_macro = item.get("left")
            if left_macro:
                e_left = self.macros[left_macro]
                left_guid = e_left.attrib["guid"]
            right_guid = None
            right_macro = item.get("right")
            if right_macro:
                e_right = self.macros[right_macro]
                right_guid = e_right.attrib["guid"]
            self.add_toolbaritem(e_tb, left_guid, right_guid)

    def add_toolbaritem(self, root, left_macro_id, right_macro_id):
        guid = uuid.uuid4()
        s_item = TPL_TOOLBARITEM.format(guid, left_macro_id, right_macro_id)
        e_item = ET.fromstring(s_item)
        root.append(e_item)

    def add_toolbarseparator(self, root):
        guid = uuid.uuid4()
        s_sep = TPL_TOOLBARSEPARATOR.format(guid)
        e_sep = ET.fromstring(s_sep)
        root.append(e_sep)

    # --------------------------------------------------------------------------
    # add toolbargroups
    # --------------------------------------------------------------------------

    def add_toolbargroups(self, toolbargroups):
        for tbg in toolbargroups:
            self.add_toolbargroup(tbg)

    def add_toolbargroup(self, tbg):
        options = {
            "single_file": "False",
            "hide_single_tab": "False",
        }
        guid = uuid.uuid4()
        s_tbg = TPL_TOOLBARGROUP.format(guid, tbg["name"], options)
        e_tbg = ET.fromstring(s_tbg)
        self.root_toolbargroups.append(e_tbg)
        for tb_name in tbg["toolbars"]:
            e_tb = self.toolbars[tb_name]
            tb_guid = e_tb.attrib["guid"]
            self.add_toolbargroupitem(e_tbg, tb_name, tb_guid)

    def add_toolbargroupitem(self, root, tb_name, tb_guid):
        guid = uuid.uuid4()
        s_item = TPL_TOOLBARGROUPITEM.format(guid, tb_name, tb_guid)
        e_item = ET.fromstring(s_item)
        root.append(e_item)


# ==============================================================================
# Main
# ==============================================================================

if __name__ == "__main__":

    HERE = os.path.dirname(__file__)
    FILE_I = os.path.join(HERE, "config.json")
    FILE_O = os.path.join(HERE, "AGS.rui")

    rui = Rui(FILE_O)

    # add this to from_json
    with open(FILE_I, "r") as f:
        config = json.load(f)

    # move this to add_commands
    commands = []
    for cmd in config["ui"]["commands"]:
        commands.append({
            "name": cmd["name"],
            "script": "-_{}".format(cmd["name"]),
            "tooltip": cmd.get("tooltip"),
            "help_text": cmd.get("help_text"),
            "button_text": cmd.get("button_text"),
            "menu_text": cmd.get("menu_text"),
            "icon": cmd.get("icon"),
        })

    rui.init()

    rui.add_bitmap(os.path.join(HERE, config["ui"]["icons"]["bitmap"]))
    rui.add_bitmap_items(config["ui"]["icons"]["images"])

    rui.add_macros(commands)
    rui.add_menus(config["ui"]["menus"])
    rui.add_toolbars(config["ui"]["toolbars"])
    rui.add_toolbargroups(config["ui"]["toolbargroups"])

    rui.write()
