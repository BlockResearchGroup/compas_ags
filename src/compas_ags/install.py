import compas
import sys
import json

PLUGIN_NAME = "AGS"

if __name__ == '__main__':

    packages = ['compas', 'compas_rhino', 'compas_ags']

    import importlib

    print("\n", "-"*10, "Checking packages", "-"*10)
    for p in packages:
        try:
            importlib.import_module(p)
            print('   {} {}'.format(p.ljust(20), "OK"))
        except ImportError as e:
            print(p, "ERROR: cannot be imported, make sure it is installed")
            raise ImportError(e)

    from compas_rhino.install import install
    from compas_rhino.install_plugin import install_plugin
    import argparse
    import os

    parser = argparse.ArgumentParser(
        description='COMPAS_AGS Installation command-line utility.')

    parser.add_argument('--dev', action='store_true', help="install dev version of AGS from current env")
    parser.add_argument('--plugin_path', help="The path to the plugin directory.")
    args = parser.parse_args()

    print("\n", "-"*10, "Installing AGS python plugin", "-"*10)

    if args.dev:
        rpy_plugin_path = os.path.join(os.path.dirname(__file__), "..", "..", 'ui/Rhino/AGS')
        rpy_plugin_path = os.path.abspath(rpy_plugin_path)
    elif args.plugin_path:
        rpy_plugin_path = os.path.abspath(args.plugin_path)
    else:
        rpy_plugin_path = os.path.dirname(__file__)
        rpy_plugin_path = os.path.join(rpy_plugin_path, "..", "..", "..", "..", "..")
        rpy_plugin_path = os.path.abspath(rpy_plugin_path)

    install_plugin(rpy_plugin_path, version="6.0")

    print("\n", "-"*10, "Installing COMPAS packages", "-"*10)

    install(packages=packages)

    print("\n", "-"*10, "Installation is successful", "-"*10)

    print("\n", "-"*10, "Registering Installation", "-"*10)

    os.makedirs(compas.APPDATA, exist_ok=True)
    register_json_path = os.path.join(compas.APPDATA, "compas_plugins.json")
    if os.path.exists(register_json_path):
        register_json = json.load(open(register_json_path))
        if not isinstance(register_json["Plugins"], dict):
            register_json["Plugins"] = {}
    else:
        register_json = {"Plugins": {}, "Current": None}

    if args.dev:
        plugin_path = os.path.dirname(__file__)
        plugin_path = os.path.join(plugin_path, "..", "..")
        plugin_path = os.path.abspath(plugin_path)

    else:
        plugin_path = rpy_plugin_path

    plugin_info = {
        "dev": args.dev,
        "path": plugin_path,
        "python": sys.executable,
        "packages": {},
    }

    for name in packages:
        package = importlib.import_module(name)
        plugin_info["packages"][name] = {"version": package.__version__}

    print(plugin_info)

    print("registering to", register_json_path)

    register_json["Plugins"][PLUGIN_NAME] = plugin_info
    register_json["Current"] = PLUGIN_NAME

    print(" "*4, plugin_path, "is registered")

    for name in register_json["Plugins"]:
        plugin = register_json["Plugins"][name]
        if not os.path.exists(plugin["path"]):
            del register_json["Plugins"][name]
            print("    Removed un-existed path: ", plugin_path)

    json.dump(register_json, open(register_json_path, "w"), indent=4)

    print("\n", "-"*10, "Installation is Registered", "-"*10)
