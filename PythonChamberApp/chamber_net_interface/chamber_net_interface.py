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
    header_api: dict = None
    header_tjson: dict = None
    api_printhead_endpoint: str = None
    api_connection_endpoint: str = None
    api_system_cmd_endpoint: str = None
    api_printer_cmd_endpoint: str = None

    def __init__(self, ip_address: str = None, api_key: str = None):
        """stores ip address of chamber and initializes private standard headers and addresses"""
        super().set_ip_address('http://' + ip_address)
        super().set_api_key(api_key)

        # headers
        self.header_api = {
            'X-Api-Key': super().get_api_key()
        }
        self.header_tjson = {
            'X-Api-Key': super().get_api_key(),
            'Content-Type': 'application/json'
        }

        # api addresses
        self.api_connection_endpoint = super().get_ip_address() + '/api/connection'
        self.api_printhead_endpoint = super().get_ip_address() + '/api/printer/printhead'
        self.api_system_cmd_endpoint = super().get_ip_address() + '/api/system/commands'

    def chamber_connect(self):
        """
        Initiates Octoprint serial connection to chamber (printer).

        Returns dict of ['status_code' : str , 'content' : str] from server response
        """
        payload = {
            "command": "connect"
        }
        response = requests.post(url=self.api_connection_endpoint, headers=self.header_tjson, json=payload)
        return {'status_code': response.status_code, 'content': response.content}

    def chamber_disconnect(self):
        """
        Requests Octoprint to disconnect serial port to chamber (printer).

        Returns dict of ['status_code' : str , 'content' : str] from server response
        """
        payload = {
            "command": "disconnect"
        }
        response = requests.post(url=self.api_connection_endpoint, headers=self.header_tjson, json=payload)
        return {'status_code': response.status_code, 'content': response.content}

    def __chamber_jog(self, x: float = 0.0, y: float = 0.0, z: float = 0.0, speed: float = 100.0,
                      abs_coordinate: bool = False):
        """
        Receives x,y,z parameters, desired speed and coordinate-context and requests chamber movement via http-request.
        :param x: x-direction distance or coordinate [mm]
        :param y: y-direction distance or coordinate [mm]
        :param z: z-direction distance or coordinate [mm]
        :param speed: speed for movement in [mm/min]
        :param abs_coordinate: boolean flag if total coordinates should be used
        :return: dict {'status code' : str, 'content' : str} of server response
        """
        payload = {
            "command": "jog",
            "x": x,
            "y": y,
            "z": z,
            "absolute": abs_coordinate,
            "speed": speed
        }
        response = requests.post(url=self.api_printhead_endpoint, headers=self.header_tjson, json=payload)
        return {'status_code': response.status_code, 'content': response.content}

    def chamber_jog_abs(self, x: float = 0.0, y: float = 0.0, z: float = 0.0, speed: float = 5.0):
        """
        Takes absolute coordinates to move to.
        :param x: desired x position [mm]
        :param y: desired y position [mm]
        :param z: desired z position [mm]
        :param speed: speed for movement in [mm/s]
        :return: dict {'status code' : str, 'content' : str} of server response
        """
        response = self.__chamber_jog(x=x, y=y, z=z, speed=(speed * 60), abs_coordinate=True)
        return response

    def chamber_jog_rel(self, x: float = 0.0, y: float = 0.0, z: float = 0.0, speed: float = 5.0):
        """
        Takes relative coordinates to move to from current position.
        :param x: distance in x-direction [mm]
        :param y: distance in y-direction [mm]
        :param z: distance in z-direction [mm]
        :param speed: speed for movement in [mm/s]
        :return: dict {'status code' : str, 'content' : str} of server response
        """
        response = self.__chamber_jog(x=x, y=y, z=z, speed=(speed * 60), abs_coordinate=False)
        return response

    def chamber_home(self, axis: str = ''):
        """
        Receives axis to home as string. Independent of upper or lower case.

        [**WARNING**]

        Default home procedure of all axis places head in middle of the bed!
        If the bed is modified in some way (holes etc.), better use
        chamber_safe_home to account for a valid sensor-position while homing z.

        :param axis: arbitrary string containing x/X, y/Y, z/Z. e.g. axis = 'xyz' or 'xy' or 'Zyx' ...
        :return: dict {'status code' : str, 'content' : str} of server response
        """
        # initialize flags if letter found
        flag_x = False
        flag_y = False
        flag_z = False

        # check for letters in string
        for i in axis:
            if i == 'x' or i == 'X':
                flag_x = True
            if i == 'y' or i == 'Y':
                flag_y = True
            if i == 'z' or i == 'Z':
                flag_z = True

        # set up request list
        list = []
        if flag_x: list.append('x')
        if flag_y: list.append('y')
        if flag_z: list.append('z')

        # formulate and send request
        payload = {
            "command": "home",
            "axes": list
        }
        response = requests.post(self.api_printhead_endpoint, headers=self.header_tjson, json=payload)
        return {'status_code': response.status_code, 'content': response.content}

    def chamber_safe_home(self):
        """
        Homes all axis in safe mode by first homing XY axis and then placing the head in a preconfigured
        spot declared in the printer.cfg file, that makes sure the Z-sensor (BL-Touch) is not placed
        above a screwing hole or similar.
        :return: dict {'status code' : str, 'content' : str} of server response
        """
        gcode_cmd = {
            "command": ""
        }
        response = requests.post(url=self.api_printer_cmd_endpoint, headers=self.header_tjson, json=gcode_cmd)
        return {'status_code': response.status_code, 'content': response.content}

    def chamber_system_restart(self):
        """
        Initiates an overall system restart of the chamber (Server and Klipper).
        :return: dict {'status code' : str, 'content' : str} of server response
        """
        response = requests.post(url=self.api_system_cmd_endpoint + '/core/restart', headers=self.header_api)
        return {'status_code': response.status_code, 'content': response.content}

    def chamber_level_bed(self):
        """
        Sends Klipper command for Z-Tilt compensation. Probes three points defined in printer.cfg and adjusts the
        position of each z-stepper accordingly.
        :return: dict {'status code' : str, 'content' : str} of server response
        """
        gcode_cmd = {
            "command": "Z_TILT_ADJUST"
        }
        response = requests.post(url=self.api_printer_cmd_endpoint, headers=self.header_tjson, json=gcode_cmd)
        return {'status_code': response.status_code, 'content': response.content}
