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

    import compas_rhino
    from compas_rhino.install import install
    # from compas_rhino.uninstall import uninstall
    from compas_rhino.install_plugin import install_plugin
    from compas_rhino.uninstall_plugin import uninstall_plugin
    import argparse
    import os

    parser = argparse.ArgumentParser(
        description='COMPAS_AGS Installation command-line utility.')

    parser.add_argument('--dev', action='store_true', help="install dev version of RV2 from current env")
    parser.add_argument('--remove_plugins', action='store_true', help="remove all existing plugins")
    parser.add_argument('--plugin_path', help="The path to the plugin directory.")
    args = parser.parse_args()

    if args.remove_plugins:
        print("\n", "-"*10, "Removing existing plugins", "-"*10)
        python_plugins_path = compas_rhino._get_python_plugins_path("6.0")
        print("Plugin location: ", python_plugins_path)
        plugins = os.listdir(python_plugins_path)
        for p in plugins:
            uninstall_plugin(p, version="6.0")

    # print("\n", "-"*10, "Removing existing packages", "-"*10)
    # uninstall()

    print("\n", "-"*10, "Installing AGS python plugin", "-"*10)
    if args.dev:
        install_plugin('ui/Rhino/AGS', version="6.0")
    elif args.plugin_path:
        install_plugin(args.plugin_path, version="6.0")

    print("\n", "-"*10, "Installing COMPAS packages", "-"*10)

    install(packages=packages)

    print("\n", "-"*10, "Installation is successful", "-"*10)
