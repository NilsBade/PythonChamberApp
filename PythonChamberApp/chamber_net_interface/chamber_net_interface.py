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
import time


class ChamberNetworkCommands(connection_handler.NetworkDevice):
    # private properties
    header_api: dict = None
    header_tjson: dict = None
    api_printhead_endpoint: str = None
    api_connection_endpoint: str = None
    api_system_cmd_endpoint: str = None
    api_printer_cmd_endpoint: str = None
    api_printer_tool_endpoint: str = None

    gcode_set_flag = 'M104 T0 S1'  # used to mark when (jog) cmd started
    gcode_reset_flag = 'M104 T0 S0'  # used to mark when (jog) cmd completed

    def __init__(self, ip_address: str = None, api_key: str = None):
        """
        Stores ip address of chamber and initializes private standard headers and addresses.
        Also, directly requests the chamber to connect to driver board via serial
        when initialized.

        :param ip_address:  ip address of chamber in local network. e.g. '134.28.25.201'
        :param api_key:     octoprint's application specific api key (self-generated) to register http requests
        """
        super().set_ip_address('http://' + ip_address)
        super().set_api_key(api_key)

        # initialize headers
        self.header_api = {
            'X-Api-Key': super().get_api_key()
        }
        self.header_tjson = {
            'X-Api-Key': super().get_api_key(),
            'Content-Type': 'application/json'
        }

        # initialize api addresses
        self.api_connection_endpoint = super().get_ip_address() + '/api/connection'
        self.api_printhead_endpoint = super().get_ip_address() + '/api/printer/printhead'
        self.api_system_cmd_endpoint = super().get_ip_address() + '/api/system/commands'
        self.api_printer_cmd_endpoint = super().get_ip_address() + '/api/printer/command'
        self.api_printer_tool_endpoint = super().get_ip_address() + '/api/printer/tool'

        # connect to driver board
        self.chamber_connect_serial()

    def chamber_connect_serial(self):
        """
        Initiates Octoprint serial connection to chamber (printer).
        Function can handle request exceptions! In case of an error other return.

        **This function should be called first and enable all other chamber http-requests since it is
        the only exception-proof implementation!**

        :return: Success >> dict of {'status_code' : int , 'content' : str} from server response |
                Exception >> dict of {'status_code' : int = -1, 'error' : str} from requests module
        """
        payload = {
            "command": "connect"
        }
        try:    # handle wrong ip address or similar network connection problems
            response = requests.post(url=self.api_connection_endpoint, headers=self.header_tjson, json=payload, timeout=2)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            return {'status_code': -1, 'error': 'An error occurred' + str(e)}

        return {'status_code': response.status_code, 'content': response.content}

    def chamber_disconnect_serial(self):
        """
        Requests Octoprint to disconnect serial port to chamber (printer).

        :return: dict of {'status_code' : str , 'content' : str} from server response
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

    def __chamber_jog_with_flag(self, x: float = 0.0, y: float = 0.0, z: float = 0.0, speed: float = 100.0,
                                abs_coordinate: bool = False):
        """
        Receives x,y,z parameters, desired speed and coordinate-context and requests chamber movement via custom
        G-Code list via http. This enables busy waiting for chamber movements to finish!

        **This function only returns once the jog operation is finished! Polls every 0.5 sec**
        :param x: x-direction distance or coordinate [mm], 2 decimal
        :param y: y-direction distance or coordinate [mm], 2 decimal
        :param z: z-direction distance or coordinate [mm], 2 decimal
        :param speed: speed for movement in [mm/min], 2 decimal
        :param abs_coordinate: boolean flag if total coordinates should be used
        :return: dict {'status code' : str, 'content' : str} of server response
        """
        # round numbers and build XYZ-parts
        x_code = ' X' + str(round(x, 2))
        y_code = ' Y' + str(round(y, 2))
        z_code = ' Z' + str(round(z, 2))
        speed_code = ' S' + str(round(speed, 2))

        # assemble custom GCode...
        g_code_list = [self.gcode_set_flag]
        if abs_coordinate:
            g_code_list.append("G90")  # set absolute coordinates
        else:
            g_code_list.append("G91")  # set relative coordinates
        g_code_list.append('G1' + x_code + y_code + z_code + speed_code)
        g_code_list.append(self.gcode_reset_flag)
        g_code_list.append('M105')  # requests Tool 0 Temp info. Necessary in first server request.

        # send g-code-cmd-request via http
        payload = {
            "commands": g_code_list
        }
        response = requests.post(url=self.api_printer_cmd_endpoint, headers=self.header_tjson, json=payload)

        while self.chamber_isflagset():
            time.sleep(0.5)

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
        response = self.__chamber_jog_with_flag(x=x, y=y, z=z, speed=(speed * 60), abs_coordinate=True)
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
        response = self.__chamber_jog_with_flag(x=x, y=y, z=z, speed=(speed * 60), abs_coordinate=False)
        return response

    def chamber_home(self, axis: str = ''):
        """
        Receives axis to home as string. Independent of upper or lower case.
        printer.cfg [safe_z_home] should make sure that head is in right position when probing for z-axis.

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

    def chamber_isflagset(self):
        """
        Reads Tool 0 target temperature and checks if it is ...

        0   >>  flag was reset. Commands before are done.
        1   >>  flag is still set. Commands are still running

        This function can be used to realise busy waiting on the movements of the chamber.
        :return: TRUE > flag is set | FALSE > flag not set
        """
        str_found_position = -1
        flag_position_offset = 10
        info_str = ""
        while str_found_position < 0:
            response = requests.get(url=self.api_printer_tool_endpoint, headers=self.header_tjson)
            info = response.content
            info_str = str(info, encoding='utf-8')
            str_found_position = info_str.find('"target": ')
            time.sleep(0.5)

        flag_position = str_found_position + flag_position_offset

        isflagset = bool(info_str[flag_position] == '1')
        return isflagset

    def chamber_set_flag(self):
        """
        **Debug function**
        Tool 0 target temperature is set 1.

        Tool 0 target temperature is used as flag to show position in G-Code.
        Before every jog command the target is set to 1 and at the end reset to 0.
        Thus reading the target value gives information if the jog command is done.
        :return: dict {'status code' : str, 'content' : str} of server response
        """
        payload = {
            "command": "target",
            "targets": {
                "tool0": 1
            }
        }
        response = requests.post(url=self.api_printer_tool_endpoint, headers=self.header_tjson, json=payload)
        return {'status_code': response.status_code, 'content': response.content}

    def chamber_reset_flag(self):
        """
        **Debug function**
        Tool 0 target temperature is set 0.

        Tool 0 target temperature is used as flag to show position in G-Code.
        Before every jog command the target is set to 1 and at the end reset to 0.
        Thus reading the target value gives information if the jog command is done.
        :return: dict {'status code' : str, 'content' : str} of server response
        """
        payload = {
            "command": "target",
            "targets": {
                "tool0": 0
            }
        }
        response = requests.post(url=self.api_printer_tool_endpoint, headers=self.header_tjson, json=payload)
        return {'status_code': response.status_code, 'content': response.content}
