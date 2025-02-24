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

import connection_handler
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
    gcode_wait_for_moves_to_finish = 'M400'
    __debug_gcode_sleep_5s = 'G4 P5000'

    __checkFlagTimeout = 0.05    # timeout for checking flag in seconds. Compromise between speed of measurement (low timeout, frequent checking) and responsiveness of chamber (do not overload chamber with requests)

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
            return {'status_code': -1, 'error': 'An error occurred! Status Code: ' + str(e)}

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


    def __chamber_jog_with_flag(self, x: float = 0.0, y: float = 0.0, z: float = 0.0, speed: float = 100.0,
                                abs_coordinate: bool = False):
        """
        Receives x,y,z parameters, desired speed and coordinate-context and requests chamber movement via custom
        G-Code list via http. This enables busy waiting for chamber movements to finish!

        **This function only returns once the jog operation is finished! Polls every 0.05 sec**
        :param x: x-direction distance or coordinate [mm], 2 decimal
        :param y: y-direction distance or coordinate [mm], 2 decimal
        :param z: z-direction distance or coordinate [mm], 2 decimal
        :param speed: speed for movement in [mm/min], 2 decimal
        :param abs_coordinate: boolean flag if total coordinates should be used
        :return: dict {'status code' : str, 'content' : str} of server response
        """
        # todo: Check why the coordinates are rounded to two decimals! why did I set this limit? this limits accuracy to +/- 5um. Did not find any reason in klipper or octoprint documentation (11.02.2025)
        # round numbers and build XYZ-parts
        x_code = ' X' + str(round(x, 2))
        y_code = ' Y' + str(round(y, 2))
        z_code = ' Z' + str(round(z, 2))
        speed_code = ' F' + str(round(speed, 2))

        # assemble custom GCode...
        g_code_list = [self.gcode_set_flag]
        g_code_list.append('M105')  # requests Tool 0 Temp info. Necessary in first server request.
        if abs_coordinate:
            g_code_list.append("G90")  # set absolute coordinates
        else:
            g_code_list.append("G91")  # set relative coordinates
        g_code_list.append('G1' + x_code + y_code + z_code + speed_code)
        g_code_list.append(self.gcode_wait_for_moves_to_finish)
        g_code_list.append(self.gcode_reset_flag)
        g_code_list.append("G90")   # always set global coordinates in the end to prevent malfunction when octoprint used in webbrowser at the same time

        # send g-code-cmd-request via http
        payload = {
            "commands": g_code_list
        }
        response = requests.post(url=self.api_printer_cmd_endpoint, headers=self.header_tjson, json=payload)

        while self.chamber_isflagset():
            time.sleep(self.__checkFlagTimeout)

        return {'status_code': response.status_code, 'content': response.content}

    def chamber_jog_abs(self, x: float = 0.0, y: float = 0.0, z: float = 0.0, speed: float = 5.0):
        """
        Takes absolute coordinates to move to.
        :param x: desired x position [mm], 2 decimal
        :param y: desired y position [mm], 2 decimal
        :param z: desired z position [mm], 2 decimal
        :param speed: speed for movement in [mm/s]
        :return: dict {'status code' : str, 'content' : str} of server response
        """
        response = self.__chamber_jog_with_flag(x=x, y=y, z=z, speed=(speed * 60), abs_coordinate=True)
        return response

    def chamber_jog_rel(self, x: float = 0.0, y: float = 0.0, z: float = 0.0, speed: float = 5.0):
        """
        Takes relative coordinates to move to from current position.
        :param x: distance in x-direction [mm], 2 decimal
        :param y: distance in y-direction [mm], 2 decimal
        :param z: distance in z-direction [mm], 2 decimal
        :param speed: speed for movement in [mm/s]
        :return: dict {'status code' : str, 'content' : str} of server response
        """
        response = self.__chamber_jog_with_flag(x=x, y=y, z=z, speed=(speed * 60), abs_coordinate=False)
        return response

    def chamber_home_with_flag(self,axis: str = ''):
        """
        Receives axis to home as string. Independent of upper or lower case.
        printer.cfg [safe_z_home] should make sure that head is in right position when probing for z-axis.
        The used custom GCode request, send via http, enables busy waiting until homing is finished.

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

        home_gcode = 'G28 '
        if flag_x:
            home_gcode += 'X0 '
        if flag_y:
            home_gcode += 'Y0 '
        if flag_z:
            home_gcode += 'Z0'

        # assemble custom GCode...
        g_code_list = [self.gcode_set_flag]
        g_code_list.append(home_gcode)
        g_code_list.append(self.gcode_reset_flag)

        # send g-code-cmd-request via http
        payload = {
            "commands": g_code_list
        }
        response = requests.post(url=self.api_printer_cmd_endpoint, headers=self.header_tjson, json=payload)

        while self.chamber_isflagset():
            time.sleep(self.__checkFlagTimeout)

        return {'status_code': response.status_code, 'content': response.content}

    def chamber_system_restart(self):
        """
        Initiates an overall system restart of the chamber (Server and Klipper).
        :return: dict {'status code' : str, 'content' : str} of server response
        """
        response = requests.post(url=self.api_system_cmd_endpoint + '/core/restart', headers=self.header_api)
        return {'status_code': response.status_code, 'content': response.content}

    def chamber_z_tilt_with_flag(self):
        """
        Sends Klipper command for Z-Tilt compensation. Probes three points defined in printer.cfg and adjusts the
        position of each z-stepper accordingly.
        :return: dict {'status code' : str, 'content' : str} of server response
        """
        g_code_list = [self.gcode_set_flag]
        g_code_list.append("Z_tilt_adjust") # Custom GCode command of klipper
        g_code_list.append(self.gcode_wait_for_moves_to_finish)
        g_code_list.append(self.gcode_reset_flag)

        # send g-code-cmd-request via http
        payload = {
            "commands": g_code_list
        }
        response = requests.post(url=self.api_printer_cmd_endpoint, headers=self.header_tjson, json=payload)

        while self.chamber_isflagset():
            time.sleep(self.__checkFlagTimeout)
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
        while str_found_position < 0:   # ask chamber multiple times until valid response is received
            response = requests.get(url=self.api_printer_tool_endpoint, headers=self.header_tjson)
            info = response.content
            info_str = str(info, encoding='utf-8')
            str_found_position = info_str.find('"target": ')
            if str_found_position < 0:
                print("Chamber Error: Flag not found in octoprint response. Trying again...") # debug - never triggered with 0.05s timeout - 18.12.2024
                time.sleep(self.__checkFlagTimeout)   # wait a little to not overload chamber with requests

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

    def chamber_send_custom_GCode_with_flag(self, g_code_list: list):
        """
        Sends custom G-Code list via http to chamber.
        :param g_code_list: list of G-Code commands
        :return: dict {'status code' : str, 'content' : str} of server response
        """
        send_list = [self.gcode_set_flag]
        send_list.extend(g_code_list)
        g_code_list.append(self.gcode_reset_flag)

        payload = {
            "commands": g_code_list
        }
        response = requests.post(url=self.api_printer_cmd_endpoint, headers=self.header_tjson, json=payload)

        while self.chamber_isflagset():
            time.sleep(self.__checkFlagTimeout)

        return {'status_code': response.status_code, 'content': response.content}
