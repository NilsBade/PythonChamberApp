"""
In this file the core chamber-class is defined. It is derived from network device class
and implements all high level commands necessary to control the measurement process.

Server response status codes:
200 -   Ok
204 -   No Content (no error)
400 -   Bad Request (server did not understand message)
403 -   Server denied access
409 -   Conflict
"""

import PythonChamberApp.connection_handler as connection_handler
import json
import requests


class ChamberNetworkCommands(connection_handler.NetworkDevice):

    # private properties
    header_api = None
    header_tjson = None

    def __init__(self, ip_address: str = None, api_key: str = None):
        """stores ip address of chamber and initializes private standard headers"""
        super().set_ip_address('http://' + ip_address)
        super().set_api_key(api_key)
        self.header_api = {
            'X-Api-Key': super().get_api_key()
        }
        self.header_tjson = {
            'X-Api-Key': super().get_api_key(),
            'Content-Type': 'application/json'
        }

    def chamber_connect(self):
        """Initiates Octoprint serial connection to chamber (printer).
        Returns dict of ['status_code' : str , 'content' : str] from server response"""
        url = super().get_ip_address() + '/api/connection'
        payload = {
            "command": "connect"
        }
        response = requests.post(url=url, headers=self.header_tjson, json=payload)
        return {
            'status_code': response.status_code,
            'content': response.content
        }

    def chamber_disconnect(self):
        """Requests Octoprint to disconnect serial port to chamber (printer).
        Returns dict of ['status_code' : str , 'content' : str] from server response"""
        url = super().get_ip_address() + '/api/connection'
        payload = {
            "command": "disconnect"
        }
        response = requests.post(url=url, headers=self.header_tjson, json=payload)
        return {
            'status_code': response.status_code,
            'content': response.content
        }

    def chamber_jog_rel(self, x: float = 0.0, y: float = 0.0, z: float = 0.0):
        url = super().get_ip_address() + 'api/printer/printhead'
        payload = {
            "command": "jog",
            "x": x,
            "y": y,
            "z": z,
            "absolute": False
        }
        response = requests.post(url, headers=self.header_tjson, json=payload)
        return {
            'status_code': response.status_code,
            'content': response.content
        }

    # Kümmer dich im den Jog-Speed!


