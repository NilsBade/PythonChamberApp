"""
In this file the core chamber-class is defined. It is derived from network device class
and implements all high level commands necessary to control the measurement process.
"""

import PythonChamberApp.connection_handler as connection_handler


class ChamberNetworkCommands(connection_handler.NetworkDevice):
    def __init__(self, ip_address:str = None, api_key:str = None):
        super().set_ip_address('http://' + ip_address)
        super().set_api_key(api_key)


