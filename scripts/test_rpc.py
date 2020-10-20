from compas.rpc import Proxy

graphstatics = Proxy('compas_ags.ags.graphstatics')
graphstatics.restart_server()
