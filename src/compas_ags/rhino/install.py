from compas.plugins import plugin


@plugin(category="install", tryfirst=True)
def installable_rhino_packages():
    return ["compas_ags"]
