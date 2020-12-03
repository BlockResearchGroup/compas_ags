import os
import json
import compas
import importlib
import subprocess

PLUGIN_NAME = "AGS"


def run(cmd):
    # p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=compas._os.prepare_environment())
    stdout, stderr = p.communicate()
    return stdout, stderr, p.returncode


def get_plugin_path():
    plugin_path = os.path.dirname(__file__)
    plugin_path = os.path.realpath(plugin_path)
    plugin_path = os.path.join(plugin_path, "..", "..")
    plugin_path = os.path.abspath(plugin_path)

    return plugin_path


def get_register_json():
    register_json_path = os.path.join(compas.APPDATA, "compas_plugins.json")
    if os.path.exists(register_json_path):
        return json.load(open(register_json_path))
    else:
        return None


def check():

    if not compas.WINDOWS:
        print("checking skipped on non-windows systems")
        return True

    register_json = get_register_json()
    if not register_json:
        print("register json not found")
        return False

    print("Current plugin: ", register_json["Current"])
    if PLUGIN_NAME != register_json["Current"]:
        return False

    plugin_info = register_json["Plugins"][PLUGIN_NAME]

    print("Checking Dependencies")
    all_passed = True
    for name in plugin_info["packages"]:
        package = importlib.import_module(name)
        current = package.__version__
        required = plugin_info["packages"][name]["version"]
        required = required.split("-")[0]
        passed = current == required
        print(name, current, " -> ", required, "Passed:", passed)

        if not passed:
            all_passed = False
            break

    print("All passed:", all_passed)
    return all_passed


def activate():

    register_json = get_register_json()
    plugin_info = register_json["Plugins"][PLUGIN_NAME]

    if plugin_info["dev"]:
        out, err, code = run("%s -m compas_ags.install --dev" % plugin_info["python"])
    else:
        out, err, code = run("%s -m compas_ags.install" % plugin_info["python"])

    if code == 0:
        print(out.decode())
        print("Activation finished! Please restart rhino for changes to take effect!")
        return True
    else:
        print('exit with code', code)
        print(err.decode())
        return False


if __name__ == '__main__':

    if check():
        print("Current plugin is already activated")
    else:
        print("Env has changed, re-activating ", PLUGIN_NAME)
        activate()
