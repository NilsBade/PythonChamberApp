"""
This is the core control-unit that stores all relevant data to reach network devices and
operates as interface between GUI and Network commands.
"""
import os.path

from chamber_net_interface import ChamberNetworkCommands
import user_interface as ui_pkg
from PyQt6.QtWidgets import QApplication, QMessageBox
from PyQt6.QtCore import QThreadPool, QObject, pyqtSignal
from .AutoMeasurement_Thread import AutoMeasurement
from .multithread_worker import Worker
from .CalibrationRoutine_Thread import CalibrationRoutine
from vna_net_interface import E8361RemoteGPIB
import numpy as np
import json


class ProcessController:
    # Properties
    chamber: ChamberNetworkCommands = None
    vna: E8361RemoteGPIB = None
    gui_mainWindow: ui_pkg.MainWindow = None
    gui_app: QApplication = None

    threadpool: QThreadPool = None
    auto_measurement_process: AutoMeasurement = None  # Automation thread that runs in parallel
    ui_chamber_control_process: Worker = None  # Assure that only one jog command at a time is requested
    ui_vna_control_process: Worker = None   # Assure that only one GPIB command/request is sent to VNA at a time
    ui_chamber_control_calibration_process: CalibrationRoutine = None  # Stores the calibration routine thread for convenience

    # Position logging & validity check
    __x_live: float = None
    __y_live: float = None
    __z_live: float = None
    __x_max_coor: float = 510.0  # Measured with V1 BL Touch sensor mount, 30.05.2024
    __y_max_coor: float = 454.0
    __z_max_coor: float = 908.0
    __z_head_bed_offset: float = 49.0

    # Auto measurement data
    zero_pos_x: float = None
    zero_pos_y: float = None
    zero_pos_z: float = None

    # Measurement Display Data
    read_in_measurement_data_buffer: dict = None

    def __init__(self):
        self.gui_app = QApplication([])
        self.gui_mainWindow = ui_pkg.MainWindow(chamber_x_max_coor=self.__x_max_coor,
                                                chamber_y_max_coor=self.__y_max_coor,
                                                chamber_z_max_coor=self.__z_max_coor,
                                                chamber_z_head_bed_offset=self.__z_head_bed_offset)
        self.gui_mainWindow.show()

        # input default values into config GUI
        self.gui_mainWindow.ui_config_window.chamber_ip_line_edit.setText("134.28.25.201")
        self.gui_mainWindow.ui_config_window.chamber_api_line_edit.setText("03DEBAA8A11941879C08AE1C224A6E2C")

        # Connect all Slots & Signals config_window - **CHAMBER**
        self.gui_mainWindow.ui_config_window.chamber_connect_button.pressed.connect(
            self.chamber_connect_button_handler_threaded)

        # Connect all Slots & Signals config_window - **VNA**
        self.gui_mainWindow.ui_config_window.vna_list_ressources_button.pressed.connect(self.vna_list_resources_button_handler)
        self.gui_mainWindow.ui_config_window.vna_connect_button.pressed.connect(self.vna_connect_button_handler)

        # connect all Slots & Signals Chamber control window
        self.gui_mainWindow.ui_chamber_control_window.home_all_axis_button.pressed.connect(
            self.chamber_control_home_all_button_handler)
        self.gui_mainWindow.ui_chamber_control_window.z_tilt_adjust_button.pressed.connect(
            self.chamber_control_z_tilt_button_handler)
        self.gui_mainWindow.ui_chamber_control_window.calibration_routine_button.pressed.connect(
            self.chamber_control_calibration_routine_button_handler)
        self.gui_mainWindow.ui_chamber_control_window.button_move_home_xy.pressed.connect(
            self.chamber_control_home_xy_button_handler)
        self.gui_mainWindow.ui_chamber_control_window.button_move_home_z.pressed.connect(
            self.chamber_control_home_z_button_handler)
        self.gui_mainWindow.ui_chamber_control_window.button_move_x_inc.pressed.connect(
            self.chamber_control_x_inc_button_handler)
        self.gui_mainWindow.ui_chamber_control_window.button_move_x_dec.pressed.connect(
            self.chamber_control_x_dec_button_handler)
        self.gui_mainWindow.ui_chamber_control_window.button_move_y_inc.pressed.connect(
            self.chamber_control_y_inc_button_handler)
        self.gui_mainWindow.ui_chamber_control_window.button_move_y_dec.pressed.connect(
            self.chamber_control_y_dec_button_handler)
        self.gui_mainWindow.ui_chamber_control_window.button_move_z_inc.pressed.connect(
            self.chamber_control_z_inc_button_handler)
        self.gui_mainWindow.ui_chamber_control_window.button_move_z_dec.pressed.connect(
            self.chamber_control_z_dec_button_handler)
        self.gui_mainWindow.ui_chamber_control_window.go_abs_coor_go_button.pressed.connect(
            self.chamber_control_go_to_button_handler)

        # connect all Slots & Signals VNA control window
        self.gui_mainWindow.ui_vna_control_window.visa_read_button.pressed.connect(self.vna_read_button_handler)
        self.gui_mainWindow.ui_vna_control_window.visa_write_button.pressed.connect(self.vna_write_button_handler)
        self.gui_mainWindow.ui_vna_control_window.visa_query_button.pressed.connect(self.vna_query_button_handler)

        # setup AutoMeasurement
        self.zero_pos_x = 258.0     # measured with V1 BL Touch sensor mount and ProbeHead V4, 03.07.2024
        self.zero_pos_y = 225.5     # measured with V1 BL Touch sensor mount and ProbeHead V4, 03.07.2024
        self.zero_pos_z = None
        self.gui_mainWindow.ui_auto_measurement_window.update_current_zero_pos(self.zero_pos_x, self.zero_pos_y,
                                                                               self.zero_pos_z)
        # connect all Slots & Signals Auto measurement window
        self.gui_mainWindow.ui_auto_measurement_window.button_move_to_zero.pressed.connect(
            self.auto_measurement_goZero_button_handler)
        self.gui_mainWindow.ui_auto_measurement_window.button_set_current_as_zero.pressed.connect(
            self.auto_measurement_setZero_button_handler)
        self.gui_mainWindow.ui_auto_measurement_window.button_set_z_zero_from_antennas.pressed.connect(
            self.auto_measurement_set_z_zero_from_antenna_dimensions_button_handler)
        self.gui_mainWindow.ui_auto_measurement_window.vna_config_filepath_check_button.pressed.connect(
            self.auto_measurement_vna_config_check_button_handler)
        self.gui_mainWindow.ui_auto_measurement_window.auto_measurement_start_button.pressed.connect(
            self.auto_measurement_start_handler)
        self.gui_mainWindow.ui_auto_measurement_window.auto_measurement_stop_button.pressed.connect(
            self.auto_measurement_terminate_thread_handler)

        # connect all Slots & Signals display measurement window
        self.gui_mainWindow.ui_display_measurement_window.file_select_refresh_button.pressed.connect(
            self.display_measurement_refresh_file_dropdown)
        self.gui_mainWindow.ui_display_measurement_window.file_select_read_button.pressed.connect(
            self.display_measurement_read_file)
        self.gui_mainWindow.ui_display_measurement_window.parameter_select_comboBox.currentTextChanged.connect(
            self.display_measurement_update_xz_plot_callback)
        self.gui_mainWindow.ui_display_measurement_window.parameter_select_comboBox.currentTextChanged.connect(
            self.display_measurement_update_yz_plot_callback)
        self.gui_mainWindow.ui_display_measurement_window.parameter_select_comboBox.currentTextChanged.connect(
            self.display_measurement_update_xy_plot_callback)
        self.gui_mainWindow.ui_display_measurement_window.coor_AUT_checkBox.checkStateChanged.connect(
            self.display_measurement_update_xz_plot_callback)
        self.gui_mainWindow.ui_display_measurement_window.coor_AUT_checkBox.checkStateChanged.connect(
            self.display_measurement_update_yz_plot_callback)
        self.gui_mainWindow.ui_display_measurement_window.coor_AUT_checkBox.checkStateChanged.connect(
            self.display_measurement_update_xy_plot_callback)
        self.gui_mainWindow.ui_display_measurement_window.coor_AUT_checkBox.checkStateChanged.connect(
            self.display_measurement_update_coordinate_lineEdits)
        self.gui_mainWindow.ui_display_measurement_window.unit_display_comboBox.currentTextChanged.connect(
            self.display_measurement_update_xz_plot_callback)
        self.gui_mainWindow.ui_display_measurement_window.unit_display_comboBox.currentTextChanged.connect(
            self.display_measurement_update_yz_plot_callback)
        self.gui_mainWindow.ui_display_measurement_window.unit_display_comboBox.currentTextChanged.connect(
            self.display_measurement_update_xy_plot_callback)
        # >> slider
        self.gui_mainWindow.ui_display_measurement_window.frequency_select_slider.valueChanged.connect(
            self.display_measurement_update_xz_plot_callback)
        self.gui_mainWindow.ui_display_measurement_window.frequency_select_slider.valueChanged.connect(
            self.display_measurement_update_yz_plot_callback)
        self.gui_mainWindow.ui_display_measurement_window.frequency_select_slider.valueChanged.connect(
            self.display_measurement_update_xy_plot_callback)
        self.gui_mainWindow.ui_display_measurement_window.xz_plot_y_select_slider.valueChanged.connect(
            self.display_measurement_update_xz_plot_callback)
        self.gui_mainWindow.ui_display_measurement_window.yz_plot_x_select_slider.valueChanged.connect(
            self.display_measurement_update_yz_plot_callback)
        self.gui_mainWindow.ui_display_measurement_window.xy_plot_z_select_slider.valueChanged.connect(
            self.display_measurement_update_xy_plot_callback)

        # enable Multithread via threadpool
        self.threadpool = QThreadPool()
        print("Multithreading with maximum %d threads" % self.threadpool.maxThreadCount())

    # General Callbacks
    def chamber_control_update_live_position(self, pos_update_info: dict):
        """
        This function **must be connected to POSITION_UPDATE SIGNAL of every method that requests movement by the chamber** and therefore changes its head position.
        Given the movement information via the 'pos_update_info : dict', this function logs and updates the live position of the chamber head
        to enable display in the UI and start of AutoMeasurements without homing the chamber.

        There are following keywords that can be used to describe a postion change:
            >> 'abs_x' : the new absolute x coordinate of the chamber head [mm]

            >> 'abs_y' : the new absolute y coordinate of the chamber head [mm]

            >> 'abs_z' : the new absolute z coordinate of the chamber head [mm]

            >> 'rel_x' : the new relative change to x position [mm]

            >> 'rel_y' : the new relative change to y position [mm]

            >> 'rel_z' : the new relative change to z position [mm]

        If a key is not used in the info dct, it is ignored. Thus it is possible to give the change-info only.
        There is no need for 'zero-changes' or similar.

        :param pos_update_info: {'abs_x': float, 'abs_y': float, 'abs_z': float, 'rel_x': float, 'rel_y': float, 'rel_z': float} all key-values optional!
        """
        if 'abs_x' in pos_update_info:
            self.__x_live = pos_update_info['abs_x']
        if 'abs_y' in pos_update_info:
            self.__y_live = pos_update_info['abs_y']
        if 'abs_z' in pos_update_info:
            self.__z_live = pos_update_info['abs_z']
        if 'rel_x' in pos_update_info:
            self.__x_live += pos_update_info['rel_x']
        if 'rel_y' in pos_update_info:
            self.__y_live += pos_update_info['rel_y']
        if 'rel_z' in pos_update_info:
            self.__z_live += pos_update_info['rel_z']

        self.gui_mainWindow.ui_chamber_control_window.update_live_coor_display(self.__x_live, self.__y_live,
                                                                               self.__z_live)
        self.gui_mainWindow.ui_auto_measurement_window.update_live_coor_display(self.__x_live, self.__y_live,
                                                                                self.__z_live)

        return

    def check_movement_valid(self, pos_update_info: dict) -> bool:
        """
        This function checks if the requested movement leads to a valid position.
        If not a warning is prompted that gives the reason for position-error in detail.

        :param pos_update_info: {'abs_x': float, 'abs_y': float, 'abs_z': float, 'rel_x': float, 'rel_y': float, 'rel_z': float} all key-values optional!
        :return: True >> movement valid, False >> invalid movement request
        """
        invalid_flag = False
        warn_msg = ""

        if 'abs_x' in pos_update_info:
            new_x = pos_update_info['abs_x']
            if new_x < 0 or new_x > self.__x_max_coor:
                invalid_flag = True
                warn_msg += "Invalid absolute movement!\nRequest leads to X: " + str(
                    new_x) + " but allowed range is [0, " + str(self.__x_max_coor) + "].\n"
        if 'abs_y' in pos_update_info:
            new_y = pos_update_info['abs_y']
            if new_y < 0 or new_y > self.__y_max_coor:
                invalid_flag = True
                warn_msg += "Invalid absolute movement!\nRequest leads to Y: " + str(
                    new_y) + " but allowed range is [0, " + str(self.__y_max_coor) + "].\n"
        if 'abs_z' in pos_update_info:
            new_z = pos_update_info['abs_z']
            if new_z < 0 or new_z > self.__z_max_coor:
                invalid_flag = True
                warn_msg += "Invalid absolute movement!\nRequest leads to Z: " + str(
                    new_z) + " but allowed range is [0, " + str(self.__z_max_coor) + "].\n"
        if 'rel_x' in pos_update_info:
            new_x = self.__x_live + pos_update_info['rel_x']
            if new_x < 0 or new_x > self.__x_max_coor:
                invalid_flag = True
                warn_msg += "Invalid relative movement!\nRequest leads to X: " + str(
                    new_x) + " but allowed range is [0, " + str(self.__x_max_coor) + "].\n"
        if 'rel_y' in pos_update_info:
            new_y = self.__y_live + pos_update_info['rel_y']
            if new_y < 0 or new_y > self.__y_max_coor:
                invalid_flag = True
                warn_msg += "Invalid relative movement!\nRequest leads to Y: " + str(
                    new_y) + " but allowed range is [0, " + str(self.__y_max_coor) + "].\n"
        if 'rel_z' in pos_update_info:
            new_z = self.__z_live + pos_update_info['rel_z']
            if new_z < 0 or new_z > self.__z_max_coor:
                invalid_flag = True
                warn_msg += "Invalid relative movement!\nRequest leads to Z: " + str(
                    new_z) + " but allowed range is [0, " + str(self.__z_max_coor) + "].\n"

        if invalid_flag:
            self.gui_mainWindow.prompt_warning(warn_msg=warn_msg, window_title="Invalid movement requested")
            return False
        else:
            return True

    # **UI_config_window Callbacks** ################################################
    def chamber_connect_button_handler_threaded(self):
        """
        Reads ip and api-key from user interface.
        Resets connection status label and disables chamber control tab.

        Starts up a chamber-serial-connect routine in a separate thread that pushes updates to config-window-console.

        Also checks if ip-api_key-combination is valid by requesting a zero movement and checking the response.

        Once finished, Output can be seen in status label of GUI and in the console of config window.
        """
        # read data from GUI
        connect_data = self.gui_mainWindow.ui_config_window.get_chamber_connect_data()
        ip_address = connect_data['ip_address']
        api_key = connect_data['api_key']

        # reset chamber data and disable chamber control section when clicked 'connect'
        self.chamber: ChamberNetworkCommands = None
        self.gui_mainWindow.ui_config_window.set_chamber_connected(False)
        self.gui_mainWindow.disable_chamber_control_window()
        self.gui_mainWindow.ui_auto_measurement_window.auto_measurement_start_button.setEnabled(False)      # Comment here when testing without chamber

        connect_thread = Worker(self.chamber_connect_routine, ip_address, api_key)
        connect_thread.signals.update.connect(self.gui_mainWindow.ui_config_window.append_message2console)
        connect_thread.signals.update.connect(self.gui_mainWindow.update_status_bar)
        connect_thread.signals.result.connect(self.chamber_connect_result_handler)

        self.threadpool.start(connect_thread)

    def chamber_connect_routine(self, ip_address: str, api_key: str, update_callback, progress_callback,
                                position_update_callback):
        """
        This routine can be run by a worker thread and pushes intermediate updates as string via signals.update
        """
        # initialize ChamberNetworkCommands Object and store in 'chamber' property if valid
        update_callback.emit(f"Trying to connect to chamber\n ip: {ip_address}, Api-key: {api_key}")
        new_chamber = ChamberNetworkCommands(ip_address=ip_address, api_key=api_key)

        update_callback.emit("Requesting to connect serial port to driver board...")
        response_connect = new_chamber.chamber_connect_serial()

        if response_connect['status_code'] == 204:
            update_callback.emit("OK")
            update_callback.emit("Requesting a zero movement to check API-key...")
            response_jog = new_chamber.chamber_jog_rel(x=0, y=0, z=0, speed=50)
        else:
            update_callback.emit("Connect request failed! No chamber saved.\n" + response_connect['error'])
            raise Exception("Connection request failed" + response_connect['error'])

        if response_jog['status_code'] == 204:
            update_callback.emit("OK")
            return new_chamber
        else:
            update_callback.emit("Jog request failed! No chamber saved.")
            raise Exception("Jog request failed")

    def chamber_connect_result_handler(self, new_chamber: ChamberNetworkCommands):
        self.chamber = new_chamber
        self.gui_mainWindow.enable_chamber_control_window()
        self.gui_mainWindow.enable_auto_measurement_window()
        self.gui_mainWindow.ui_config_window.set_chamber_connected(True)
        self.gui_mainWindow.ui_config_window.append_message2console(
            "Printer object was generated and saved to app. Chamber control enabled.")
        if self.vna is not None:                                                                            # Comment here when testing without chamber
            self.gui_mainWindow.ui_auto_measurement_window.auto_measurement_start_button.setEnabled(True)   # Comment here when testing without chamber
        return

    def vna_list_resources_button_handler(self):
        """
        Detects all available instruments of pyvisa ResourceManager object and prints them to console
        of config window. Differs which visa implementation is used according to checkbox in config window
        """
        resource_strings = E8361RemoteGPIB(self.gui_mainWindow.ui_config_window.get_use_keysight()).list_resources()
        self.gui_mainWindow.ui_config_window.append_message2console(f"Available Resources detected: {resource_strings}")
        self.gui_mainWindow.ui_config_window.update_vna_visa_address_dropdown(resource_strings)
        return

    def vna_connect_button_handler(self):
        """
        Reads input visa address from ui config window and starts vna_connect_routine.
        """
        visa_address = self.gui_mainWindow.ui_config_window.get_vna_visa_address()
        # print error if invalid visa address
        if visa_address == "run list first..."  or visa_address == "select...":
            self.gui_mainWindow.ui_config_window.append_message2console("Please input a visa address first. Available addresses are printed to console when clicking on 'List available resources' on the left.")
            return

        # reset vna property and tab
        self.vna = None
        self.gui_mainWindow.ui_config_window.set_vna_connected(False)
        self.gui_mainWindow.disable_vna_control_window()
        self.gui_mainWindow.ui_auto_measurement_window.auto_measurement_start_button.setEnabled(False)      # Comment here when testing without chamber

        # start connect routine
        connect_thread = Worker(self.vna_connect_routine, visa_address, self.gui_mainWindow.ui_config_window.get_use_keysight())
        connect_thread.signals.update.connect(self.gui_mainWindow.ui_config_window.append_message2console)
        connect_thread.signals.update.connect(self.gui_mainWindow.update_status_bar)
        connect_thread.signals.result.connect(self.vna_connect_result_handler)

        self.threadpool.start(connect_thread)

    def vna_connect_routine(self, visa_address: str, use_keysight_flag: bool, update_callback, progress_callback, position_update_callback):
        """
        Sends '*IDN?' query to given visa_address-device and pushes the answer or error to update_callback.
        """
        update_callback.emit("Check if visa address is valid...")
        new_vna = E8361RemoteGPIB(use_keysight=use_keysight_flag)
        available_resources = new_vna.list_resources()
        if visa_address in available_resources:     # check if given address available

            if new_vna.connect_pna(visa_address) is False:
                update_callback.emit("ERROR - Failed to open resource with pyvisa.")
                return None

            update_callback.emit(f"Opened resource {visa_address} with pyvisa.")
            idn_response = new_vna.pna_read_idn()
            # Some Instruments respond with ERROR, so separate reaction necessary
            if 'ERROR' in idn_response:
                update_callback.emit(f"Instrument response to IDN returned Error: {idn_response}")
                return None

            update_callback.emit(f"Instrument response to IDN: {idn_response}")
            return new_vna
        else:
            update_callback.emit("ERROR - Given visa address matches no available resource.")
            return None

    def vna_connect_result_handler(self, new_vna: E8361RemoteGPIB):
        """
        Detects if IDN query failed by comparing 'new_vna' to None type.
        If new_vna is not None-type, it is stored in process controller's vna property.
        """
        if new_vna is not None:
            self.vna = new_vna
            self.gui_mainWindow.enable_vna_control_window()
            self.gui_mainWindow.ui_config_window.set_vna_connected(True)
            self.gui_mainWindow.ui_config_window.append_message2console(
                "VNA object was generated and saved to app. VNA control tab enabled.")
            if self.chamber is not None:                                                                        # Comment here when testing without chamber
                self.gui_mainWindow.ui_auto_measurement_window.auto_measurement_start_button.setEnabled(True)   # Comment here when testing without chamber
        return

    # **UI_chamber_control_window Callbacks** ################################################
    def chamber_control_thread_finished_handler(self):
        if self.ui_chamber_control_process is None:
            raise Exception("chamber control finished handler was called but no thread was running!")
        else:
            self.ui_chamber_control_process = None
        return

    def chamber_control_home_all_button_handler(self):
        if self.ui_chamber_control_process is None:
            # Assure that Z-sensor is mounted
            if self.__accept_home_dialog() is False:
                return

            # disable all chamber buttons until routine finished
            self.gui_mainWindow.ui_chamber_control_window.control_buttons_widget.setEnabled(False)
            self.gui_mainWindow.ui_chamber_control_window.z_tilt_adjust_button.setEnabled(False)
            self.gui_mainWindow.ui_chamber_control_window.calibration_routine_button.setEnabled(False)

            self.ui_chamber_control_process = Worker(self.chamber_control_home_all_routine, self.chamber)

            self.ui_chamber_control_process.signals.update.connect(
                self.gui_mainWindow.ui_chamber_control_window.append_message2console)
            self.ui_chamber_control_process.signals.update.connect(self.gui_mainWindow.update_status_bar)

            self.ui_chamber_control_process.signals.position_update.connect(self.chamber_control_update_live_position)

            self.ui_chamber_control_process.signals.progress.connect(self.chamber_control_home_all_progress_handler)

            self.ui_chamber_control_process.signals.finished.connect(self.chamber_control_thread_finished_handler)

            self.threadpool.start(self.ui_chamber_control_process)
        else:
            self.gui_mainWindow.prompt_warning(
                "Another chamber control request is processing at the moment!\nPlease wait until it is finished.",
                "Too many Requests")
        return

    def chamber_control_home_all_progress_handler(self, progress: dict):
        """
        This handler enables all chamber control widgets if server response to home request valid
        """
        if progress['status_code'] == 204:
            self.gui_mainWindow.ui_chamber_control_window.control_buttons_widget.setEnabled(True)
            self.gui_mainWindow.ui_chamber_control_window.z_tilt_adjust_button.setEnabled(True)
            self.gui_mainWindow.ui_chamber_control_window.calibration_routine_button.setEnabled(True)
            self.gui_mainWindow.ui_auto_measurement_window.enable_chamber_move_interaction()
            self.gui_mainWindow.prompt_info(
                "Homing seems to be finished.\nCoordinates will be logged from now on and manual control is enabled.",
                "Check chamber state manually")
        return

    def chamber_control_home_all_routine(self, chamber: ChamberNetworkCommands, update_callback, progress_callback,
                                         position_update_callback):
        """
        This routine can be given to a worker to request all-axis-homing in separate thread
        Afterward move the head to a known position and give the updated position
        """
        update_callback.emit("Request to home all axis")
        response = chamber.chamber_home_with_flag(axis='xyz')
        if response['status_code'] == 204:
            position_update_callback.emit({'abs_x': 0.0, 'abs_y': 0.0, 'abs_z': 0.0})
            update_callback.emit("Requests Movement to Middle")
            chamber.chamber_jog_abs(x=self.zero_pos_x, y=self.zero_pos_y, z=150, speed=75.0)
            position_update_callback.emit({'abs_x': self.zero_pos_x, 'abs_y': self.zero_pos_y, 'abs_z': 150.0})
            update_callback.emit("Manual chamber control enabled")
            progress_callback.emit(response)
        else:
            update_callback.emit(
                "Something went wrong! HTTP response status code: " + response['status_code'] + ' ' + response[
                    'content'])
        return

    def __accept_home_dialog(self):
        """
        Function prompts a dialog asking for a mounted BL Touch sensor to the chamber.
        Homing is started only when sensor-mounting confirmed!
        """
        dlg = QMessageBox(self.gui_mainWindow)
        dlg.setWindowTitle("Start Homing - Z-sensor mounting")
        dlg.setText("Do you really want to start homing?\n"
                    "To Home Z-axis the BL-Touch sensor MUST be mounted to the Probehead!\n"
                    "Click ok once the sensor is mounted and wired correctly.")
        dlg.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        dlg.setIcon(QMessageBox.Icon.Question)
        button = dlg.exec()

        if button == QMessageBox.StandardButton.Yes:
            return True
        else:
            return False

    def chamber_control_home_xy_button_handler(self):
        if self.ui_chamber_control_process is None:
            self.ui_chamber_control_process = Worker(self.chamber_control_home_xy_routine, self.chamber)

            self.ui_chamber_control_process.signals.update.connect(
                self.gui_mainWindow.ui_chamber_control_window.append_message2console)
            self.ui_chamber_control_process.signals.update.connect(self.gui_mainWindow.update_status_bar)

            self.ui_chamber_control_process.signals.position_update.connect(self.chamber_control_update_live_position)

            self.ui_chamber_control_process.signals.finished.connect(self.chamber_control_thread_finished_handler)

            self.threadpool.start(self.ui_chamber_control_process)
        else:
            self.gui_mainWindow.prompt_warning(
                "Another chamber control request is processing at the moment!\nPlease wait until it is finished.",
                "Too many Requests")
        return

    def chamber_control_home_xy_routine(self, chamber: ChamberNetworkCommands, update_callback, progress_callback,
                                        position_update_callback):
        """
        This routine can be given to a worker to request xy-axis-homing in separate thread
        """
        update_callback.emit("Request to home xy-axis")
        response = chamber.chamber_home_with_flag(axis='xy')
        if response['status_code'] == 204:
            update_callback.emit("OK")
            position_update_callback.emit({'abs_x': 0.0, 'abs_y': 0.0})
        else:
            update_callback.emit(
                "Something went wrong! HTTP response status code: " + response['status_code'] + ' ' + response[
                    'content'])
        return

    def chamber_control_home_z_button_handler(self):
        if self.ui_chamber_control_process is None:
            self.ui_chamber_control_process = Worker(self.chamber_control_home_z_routine, self.chamber)

            self.ui_chamber_control_process.signals.update.connect(
                self.gui_mainWindow.ui_chamber_control_window.append_message2console)
            self.ui_chamber_control_process.signals.update.connect(self.gui_mainWindow.update_status_bar)

            self.ui_chamber_control_process.signals.position_update.connect(self.chamber_control_update_live_position)

            self.ui_chamber_control_process.signals.finished.connect(self.chamber_control_thread_finished_handler)

            self.threadpool.start(self.ui_chamber_control_process)
        else:
            self.gui_mainWindow.prompt_warning(
                "Another chamber control request is processing at the moment!\nPlease wait until it is finished.",
                "Too many Requests")
        return

    def chamber_control_home_z_routine(self, chamber: ChamberNetworkCommands, update_callback, progress_callback,
                                       position_update_callback):
        """
        This routine can be given to a worker to request z-axis-homing in separate thread
        """
        update_callback.emit("Request to home z-axis")
        response = chamber.chamber_home_with_flag(axis='z')
        if response['status_code'] == 204:
            update_callback.emit("OK")
            position_update_callback.emit({'abs_z': 0.0})
        else:
            update_callback.emit(
                "Something went wrong! HTTP response status code: " + response['status_code'] + ' ' + response[
                    'content'])
        return

    def chamber_control_calibration_routine_button_handler(self):
        """
        This button handler prompts a dialog if the calibration routine should really be started.
        It explains that a pen must be mounted and the current position must be at the correct height (z-wise) to draw on the print-bed.

        Cancels whole process if canceled and starts calibraton routine if accepted.

        Creates a CalibrationRoutine thread object and connects its callbacks to log in the chamber_control_tab console.
        Also disables chamber control utilities by disabling buttons.
        It re-enables the utilities via the calibration_routine_finished_handler.
        """
        if self.ui_chamber_control_calibration_process is not None:
            self.gui_mainWindow.prompt_warning("Another calibration process is running at the moment!\n", "Too many Requests")
            return
        # reassure start of routine
        start_flag = self.gui_mainWindow.prompt_question("Are you sure you want to start the calibration routine?\n"
                                           "If yes, make sure the pen is attached to the probehead and is currently positioned so that it just touches the print-bed to draw lines on it!\n\n"
                                           "The Calibration routine is a hardcoded procedure that draws squares on the print-bed to evaluate the chamber's position-accuracy.\n"
                                           "A pen-holder is already designed and should be available. It fits for 'Copic Multiliner' fine-liner pens for technical drawings.\n",
                                           "Start Calibration Routine")
        if start_flag == False:
            # Cancel routine
            return

        # Disable all chamber control buttons until routine finished
        self.gui_mainWindow.ui_chamber_control_window.home_all_axis_button.setEnabled(False)
        self.gui_mainWindow.ui_chamber_control_window.control_buttons_widget.setEnabled(False)
        self.gui_mainWindow.ui_chamber_control_window.z_tilt_adjust_button.setEnabled(False)
        self.gui_mainWindow.ui_chamber_control_window.calibration_routine_button.setEnabled(False)

        # Start calibration routine
        current_position = [self.__x_live, self.__y_live, self.__z_live]
        self.ui_chamber_control_calibration_process = CalibrationRoutine(self.chamber, current_position=current_position)

        self.ui_chamber_control_calibration_process.signals.update.connect(
            self.gui_mainWindow.ui_chamber_control_window.append_message2console)
        self.ui_chamber_control_calibration_process.signals.update.connect(self.gui_mainWindow.update_status_bar)

        self.ui_chamber_control_calibration_process.signals.position_update.connect(
            self.chamber_control_update_live_position)

        self.ui_chamber_control_calibration_process.signals.finished.connect(
            self.chamber_control_calibration_routine_finished_handler)

        self.threadpool.start(self.ui_chamber_control_calibration_process)
        return

    def chamber_control_calibration_routine_finished_handler(self):
        """
        Re-enables all chamber control buttons after calibration routine finished.
        """
        self.gui_mainWindow.ui_chamber_control_window.home_all_axis_button.setEnabled(True)
        self.gui_mainWindow.ui_chamber_control_window.control_buttons_widget.setEnabled(True)
        self.gui_mainWindow.ui_chamber_control_window.z_tilt_adjust_button.setEnabled(True)
        self.gui_mainWindow.ui_chamber_control_window.calibration_routine_button.setEnabled(True)
        self.ui_chamber_control_calibration_process = None
        return



    def chamber_control_x_inc_button_handler(self):
        if self.ui_chamber_control_process is None:
            jogspeed = self.gui_mainWindow.ui_chamber_control_window.get_button_move_jogspeed()
            stepsize = self.gui_mainWindow.ui_chamber_control_window.get_button_move_stepsize()

            if self.check_movement_valid({'rel_x': stepsize}):
                self.ui_chamber_control_process = Worker(self.chamber_control_jog_one_axis_rel_routine, self.chamber,
                                                         'x',
                                                         jogspeed, stepsize)

                self.ui_chamber_control_process.signals.update.connect(
                    self.gui_mainWindow.ui_chamber_control_window.append_message2console)
                self.ui_chamber_control_process.signals.update.connect(self.gui_mainWindow.update_status_bar)

                self.ui_chamber_control_process.signals.position_update.connect(
                    self.chamber_control_update_live_position)

                self.ui_chamber_control_process.signals.finished.connect(self.chamber_control_thread_finished_handler)

                self.threadpool.start(self.ui_chamber_control_process)
        else:
            self.gui_mainWindow.prompt_warning(
                "Another chamber control request is processing at the moment!\nPlease wait until it is finished.",
                "Too many Requests")
        return

    def chamber_control_x_dec_button_handler(self):
        if self.ui_chamber_control_process is None:
            jogspeed = self.gui_mainWindow.ui_chamber_control_window.get_button_move_jogspeed()
            stepsize = -1 * self.gui_mainWindow.ui_chamber_control_window.get_button_move_stepsize()

            if self.check_movement_valid({'rel_x': stepsize}):
                self.ui_chamber_control_process = Worker(self.chamber_control_jog_one_axis_rel_routine, self.chamber,
                                                         'x',
                                                         jogspeed, stepsize)

                self.ui_chamber_control_process.signals.update.connect(
                    self.gui_mainWindow.ui_chamber_control_window.append_message2console)
                self.ui_chamber_control_process.signals.update.connect(self.gui_mainWindow.update_status_bar)

                self.ui_chamber_control_process.signals.position_update.connect(
                    self.chamber_control_update_live_position)

                self.ui_chamber_control_process.signals.finished.connect(self.chamber_control_thread_finished_handler)

                self.threadpool.start(self.ui_chamber_control_process)
        else:
            self.gui_mainWindow.prompt_warning(
                "Another chamber control request is processing at the moment!\nPlease wait until it is finished.",
                "Too many Requests")
        return

    def chamber_control_y_inc_button_handler(self):
        if self.ui_chamber_control_process is None:
            jogspeed = self.gui_mainWindow.ui_chamber_control_window.get_button_move_jogspeed()
            stepsize = self.gui_mainWindow.ui_chamber_control_window.get_button_move_stepsize()

            if self.check_movement_valid({'rel_y': stepsize}):
                self.ui_chamber_control_process = Worker(self.chamber_control_jog_one_axis_rel_routine, self.chamber,
                                                         'y',
                                                         jogspeed, stepsize)

                self.ui_chamber_control_process.signals.update.connect(
                    self.gui_mainWindow.ui_chamber_control_window.append_message2console)
                self.ui_chamber_control_process.signals.update.connect(self.gui_mainWindow.update_status_bar)

                self.ui_chamber_control_process.signals.position_update.connect(
                    self.chamber_control_update_live_position)

                self.ui_chamber_control_process.signals.finished.connect(self.chamber_control_thread_finished_handler)

                self.threadpool.start(self.ui_chamber_control_process)
        else:
            self.gui_mainWindow.prompt_warning(
                "Another chamber control request is processing at the moment!\nPlease wait until it is finished.",
                "Too many Requests")
        return

    def chamber_control_y_dec_button_handler(self):
        if self.ui_chamber_control_process is None:
            jogspeed = self.gui_mainWindow.ui_chamber_control_window.get_button_move_jogspeed()
            stepsize = -1 * self.gui_mainWindow.ui_chamber_control_window.get_button_move_stepsize()

            if self.check_movement_valid({'rel_y': stepsize}):
                self.ui_chamber_control_process = Worker(self.chamber_control_jog_one_axis_rel_routine, self.chamber,
                                                         'y',
                                                         jogspeed, stepsize)

                self.ui_chamber_control_process.signals.update.connect(
                    self.gui_mainWindow.ui_chamber_control_window.append_message2console)
                self.ui_chamber_control_process.signals.update.connect(self.gui_mainWindow.update_status_bar)

                self.ui_chamber_control_process.signals.position_update.connect(
                    self.chamber_control_update_live_position)

                self.ui_chamber_control_process.signals.finished.connect(self.chamber_control_thread_finished_handler)

                self.threadpool.start(self.ui_chamber_control_process)
        else:
            self.gui_mainWindow.prompt_warning(
                "Another chamber control request is processing at the moment!\nPlease wait until it is finished.",
                "Too many Requests")
        return

    def chamber_control_z_inc_button_handler(self):
        if self.ui_chamber_control_process is None:
            jogspeed = self.gui_mainWindow.ui_chamber_control_window.get_button_move_jogspeed()
            stepsize = self.gui_mainWindow.ui_chamber_control_window.get_button_move_stepsize()

            if self.check_movement_valid({'rel_z': stepsize}):
                self.ui_chamber_control_process = Worker(self.chamber_control_jog_one_axis_rel_routine, self.chamber,
                                                         'z',
                                                         jogspeed, stepsize)

                self.ui_chamber_control_process.signals.update.connect(
                    self.gui_mainWindow.ui_chamber_control_window.append_message2console)
                self.ui_chamber_control_process.signals.update.connect(self.gui_mainWindow.update_status_bar)

                self.ui_chamber_control_process.signals.position_update.connect(
                    self.chamber_control_update_live_position)

                self.ui_chamber_control_process.signals.finished.connect(self.chamber_control_thread_finished_handler)

                self.threadpool.start(self.ui_chamber_control_process)
        else:
            self.gui_mainWindow.prompt_warning(
                "Another chamber control request is processing at the moment!\nPlease wait until it is finished.",
                "Too many Requests")
        return

    def chamber_control_z_dec_button_handler(self):
        if self.ui_chamber_control_process is None:
            jogspeed = self.gui_mainWindow.ui_chamber_control_window.get_button_move_jogspeed()
            stepsize = -1 * self.gui_mainWindow.ui_chamber_control_window.get_button_move_stepsize()

            if self.check_movement_valid({'rel_z': stepsize}):
                self.ui_chamber_control_process = Worker(self.chamber_control_jog_one_axis_rel_routine, self.chamber,
                                                         'z',
                                                         jogspeed, stepsize)

                self.ui_chamber_control_process.signals.update.connect(
                    self.gui_mainWindow.ui_chamber_control_window.append_message2console)
                self.ui_chamber_control_process.signals.update.connect(self.gui_mainWindow.update_status_bar)

                self.ui_chamber_control_process.signals.position_update.connect(
                    self.chamber_control_update_live_position)

                self.ui_chamber_control_process.signals.finished.connect(self.chamber_control_thread_finished_handler)

                self.threadpool.start(self.ui_chamber_control_process)
        else:
            self.gui_mainWindow.prompt_warning(
                "Another chamber control request is processing at the moment!\nPlease wait until it is finished.",
                "Too many Requests")
        return

    def chamber_control_jog_one_axis_rel_routine(self, chamber: ChamberNetworkCommands, axis: str, jogspeed: float,
                                                 rel_coor: float, update_callback, progress_callback,
                                                 position_update_callback):
        """
        This routine receives a chamber object and the desired relative coordinate-change on a given axis.
        It should be used in combination with arrow-button menu.
            * No Error handling when Server denies request!

        :param chamber: stored network chamber of process controller providing (network) interface to chamber
        :param axis: the axis that should be jogged - either 'x' or 'y' or 'z'
        :param jogspeed: speed to move in [mm/s]
        :param rel_coor: relative coordinate change on axis
        :param update_callback: Callback signal to send string messages to consoles, status labels or similiar. Provided by Worker-class (Thread).
        :param progress_callback: Callback signal to send dict with key-value pairs dependend on usecase. Provided by Worker-class (Thread).
        :param position_update_callback: Callback signal to send new chamber position as dict
            {'abs_x': float, 'abs_y': float, 'abs_z': float, 'rel_x': float, 'rel_y': float, 'rel_z': float}
            all key-values optional! Provided by Worker-class (Thread).
        """
        update_callback.emit(
            "Request Jog " + axis.upper() + " by " + str(rel_coor) + " mm with " + str(jogspeed) + " mm/s")
        if axis == 'x':
            response = chamber.chamber_jog_rel(x=rel_coor, speed=jogspeed)
            position_update_callback.emit({'rel_x': rel_coor})
        elif axis == 'y':
            response = chamber.chamber_jog_rel(y=rel_coor, speed=jogspeed)
            position_update_callback.emit({'rel_y': rel_coor})
        elif axis == 'z':
            response = chamber.chamber_jog_rel(z=rel_coor, speed=jogspeed)
            position_update_callback.emit({'rel_z': rel_coor})
        else:
            update_callback("jog_one_axis routine got invalid axis parameter!")
            raise Exception("jog_one_axis routine got invalid axis parameter!")

        return

    def chamber_control_go_to_button_handler(self):
        if self.ui_chamber_control_process is None:
            jogspeed = self.gui_mainWindow.ui_chamber_control_window.get_button_move_jogspeed()
            new_coordinates = self.gui_mainWindow.ui_chamber_control_window.get_go_abs_coor_inputs()
            new_x = new_coordinates['x']
            new_y = new_coordinates['y']
            new_z = new_coordinates['z']

            if self.check_movement_valid({'abs_x': new_x, 'abs_y': new_y, 'abs_z': new_z}):
                self.ui_chamber_control_process = Worker(self.chamber_control_jog_to_abs_coor_routine,
                                                         self.chamber, new_x, new_y, new_z, jogspeed)

                self.ui_chamber_control_process.signals.update.connect(
                    self.gui_mainWindow.ui_chamber_control_window.append_message2console)
                self.ui_chamber_control_process.signals.update.connect(self.gui_mainWindow.update_status_bar)

                self.ui_chamber_control_process.signals.position_update.connect(
                    self.chamber_control_update_live_position)

                self.ui_chamber_control_process.signals.finished.connect(self.chamber_control_thread_finished_handler)

                self.threadpool.start(self.ui_chamber_control_process)
        else:
            self.gui_mainWindow.prompt_warning(
                "Another chamber control request is processing at the moment!\nPlease wait until it is finished.",
                "Too many Requests")
        return

    def chamber_control_jog_to_abs_coor_routine(self, chamber: ChamberNetworkCommands, x_coor: float, y_coor: float,
                                                z_coor: float, jogspeed: float, update_callback, progress_callback,
                                                position_update_callback):
        """
        This routine a receives chamber object and the desired new position as x,y,z coordinates.
        It requests the chamber to move to the new position and signals updates.
        It should be used with the "Go to absolute coordinates" menu in UI_chamber_control_window and auto-measurement procedure.
            * No Error handling when Server denies request!

        :param chamber: stored network chamber of process controller providing (network) interface to chamber
        :param x_coor: new desired x coordinate in [mm]
        :param y_coor: new desired y coordinate in [mm]
        :param z_coor: new desired z coordinate in [mm]
        :param jogspeed: speed to move in [mm/s]
        :param update_callback: Callback signal to send string messages to consoles, status labels or similiar. Provided by Worker-class (Thread).
        :param progress_callback: Callback signal to send dict with key-value pairs dependend on usecase. Provided by Worker-class (Thread).
        :param position_update_callback: Callback signal to send new chamber position as dict
            {'abs_x': float, 'abs_y': float, 'abs_z': float, 'rel_x': float, 'rel_y': float, 'rel_z': float}
            all key-values optional! Provided by Worker-class (Thread).
        """
        update_callback.emit(
            "Request Jog to X: " + str(x_coor) + " Y: " + str(y_coor) + " Z: " + str(z_coor) + " with " + str(
                jogspeed) + "[mm/s]")
        response = chamber.chamber_jog_abs(x=x_coor, y=y_coor, z=z_coor, speed=jogspeed)
        position_update_callback.emit({'abs_x': x_coor, 'abs_y': y_coor, 'abs_z': z_coor})

        return

    def chamber_control_z_tilt_button_handler(self):
        if self.ui_chamber_control_process is None:
            self.ui_chamber_control_process = Worker(self.chamber_control_z_tilt_routine,
                                                     self.chamber)

            self.ui_chamber_control_process.signals.update.connect(
                self.gui_mainWindow.ui_chamber_control_window.append_message2console)
            self.ui_chamber_control_process.signals.update.connect(self.gui_mainWindow.update_status_bar)

            self.ui_chamber_control_process.signals.position_update.connect(self.chamber_control_update_live_position)

            self.ui_chamber_control_process.signals.finished.connect(self.chamber_control_thread_finished_handler)

            self.threadpool.start(self.ui_chamber_control_process)

            self.gui_mainWindow.prompt_info(
                "For details about tilt adjustment process look into octoprint's terminal tab on the webbrowser interface.",
                "Tilt adjustment started...")
        else:
            self.gui_mainWindow.prompt_warning(
                "Another chamber control request is processing at the moment!\nPlease wait until it is finished.",
                "Too many Requests")
        return

    def chamber_control_z_tilt_routine(self, chamber: ChamberNetworkCommands, update_callback, progress_callback,
                                       position_update_callback):
        """
        This routine requests Z-Tilt_Adjustment from Klipper in a seperate thread and sends updates to GUI
        """
        update_callback.emit("Request Z-Tilt-Adjustment...")
        chamber.chamber_z_tilt_with_flag()
        update_callback.emit("Adjustment completed. Moving to Middle...")
        chamber.chamber_jog_abs(x=self.zero_pos_x, y=self.zero_pos_y, z=150, speed=75.0)
        position_update_callback.emit({'abs_x': self.zero_pos_x, 'abs_y': self.zero_pos_y, 'abs_z': 150.0})

        return

    # **UI_vna_control_window Callbacks** ################################################

    def vna_write_button_handler(self):
        """
        Sends visa string written to VNA tab with write-command.
        Prints send-update to VNA-tab console.
        """
        if self.ui_vna_control_process is not None:
            self.gui_mainWindow.prompt_info("Another Request is still running.\n"
                                            "Please wait for it to finish.", "Other request still running")
            return

        cust_cmd = self.gui_mainWindow.ui_vna_control_window.get_visa_string()
        self.gui_mainWindow.ui_vna_control_window.append_message2console(f"Write VNA: {cust_cmd}")
        self.ui_vna_control_process = Worker(self.vna_read_write_routine, self.vna.pna_write_custom_string, cust_cmd)
        self.ui_vna_control_process.signals.update.connect(
            self.gui_mainWindow.ui_vna_control_window.append_message2console)
        self.ui_vna_control_process.signals.update.connect(self.gui_mainWindow.update_status_bar)
        self.ui_vna_control_process.signals.finished.connect(self.vna_read_write_routine_finished_handler)

        self.threadpool.start(self.ui_vna_control_process)
        return

    def vna_read_button_handler(self):
        """
        Reads from VNA and prints message to console.
        """
        if self.ui_vna_control_process is not None:
            self.gui_mainWindow.prompt_info("Another Request is still running.\n"
                                            "Please wait for it to finish.", "Other request still running")
            return

        self.gui_mainWindow.ui_vna_control_window.append_message2console(f"Reading VNA GPIB buffer...")

        read_string = ""
        self.ui_vna_control_process = Worker(self.vna_read_write_routine, self.vna.pna_read_custom_string, read_string)
        self.ui_vna_control_process.signals.update.connect(
            self.gui_mainWindow.ui_vna_control_window.append_message2console)
        self.ui_vna_control_process.signals.update.connect(self.gui_mainWindow.update_status_bar)
        self.ui_vna_control_process.signals.finished.connect(self.vna_read_write_routine_finished_handler)

        self.threadpool.start(self.ui_vna_control_process)
        return

    def vna_query_button_handler(self):
        """
        Sends visa string written to VNA tab with query command.
        Prints response to VNA-tab console.
        """
        if self.ui_vna_control_process is not None:
            self.gui_mainWindow.prompt_info("Another Request is still running.\n"
                                            "Please wait for it to finish.", "Other request still running")
            return

        cust_cmd = self.gui_mainWindow.ui_vna_control_window.get_visa_string()
        self.gui_mainWindow.ui_vna_control_window.append_message2console(f"Query VNA: {cust_cmd}")

        self.ui_vna_control_process = Worker(self.vna_read_write_routine, self.vna.pna_query_custom_string, cust_cmd)
        self.ui_vna_control_process.signals.update.connect(self.gui_mainWindow.ui_vna_control_window.append_message2console)
        self.ui_vna_control_process.signals.update.connect(self.gui_mainWindow.update_status_bar)
        self.ui_vna_control_process.signals.finished.connect(self.vna_read_write_routine_finished_handler)

        self.threadpool.start(self.ui_vna_control_process)
        return

    def vna_read_write_routine(self, vna_function, visa_str: str, update_callback, progress_callback,
                                       position_update_callback):
        """
        Routine that can be run in vna worker thread and differs query, read and write.
        """
        response = vna_function(visa_str)
        if response is None:
            update_callback.emit("Done")
        elif 'ERROR' in response:
            update_callback.emit(response)
        else:
            response = response.rstrip('\n')
            update_callback.emit(f"Response: {response}")
        return

    def vna_read_write_routine_finished_handler(self):
        """
        Once vna read write routine is finished, the property is reset to None to enable a new request.
        """
        self.ui_vna_control_process = None
        return

    # **UI_auto_measurement_window Callbacks** ################################################
    def auto_measurement_start_handler(self):
        """
        Checks if chamber is not in operation and present.
        Check if vna is available and operating (how?)
        Checks if filename is available without override, otherwise prompt warning.

        Gets config data from auto measurement window, creates auto measurement thread and starts operation
        """

        #   Check that no measurement is currently running
        if self.ui_chamber_control_process is not None:
            self.gui_mainWindow.prompt_warning("Please wait until process from chamber control menu is "
                                               "finished before starting the measurement.",
                                               "Chamber is in operation")
            return

        #   Setup results directory
        path_workdirectory = os.path.dirname(os.getcwd())
        if not os.path.exists(os.path.join(path_workdirectory + '/results')):
            os.makedirs(os.path.join(path_workdirectory + '/results'))
        path_results_folder = os.path.join(os.getcwd() + '/results')

        #   Check if filename(s) are valid, avoid override
        meas_file_name = self.gui_mainWindow.ui_auto_measurement_window.get_new_filename()
        file_type_json_flag = self.gui_mainWindow.ui_auto_measurement_window.get_is_file_json()
        file_type_json_readable = self.gui_mainWindow.ui_auto_measurement_window.get_is_file_json_readable()
        new_file_path = os.path.join(path_results_folder + '/' + meas_file_name + '.json')
        if os.path.isfile(new_file_path):
            self.gui_mainWindow.prompt_warning("A json-measurement file with the given name is already stored. \n"
                                               "Overrride is not permitted. Please change the desired file name.",
                                               "Duplicate json Filename")
            return

        #   save generic meas_file_name without type and parameter
        generic_file_path = os.path.join(path_results_folder + "/" + meas_file_name)

        #   Check if mesh coordinates are valid/reachable
        mesh_info = self.gui_mainWindow.ui_auto_measurement_window.get_mesh_cubic_data()
        if self.auto_measurement_check_move_boundary(x_vec=mesh_info['x_vec'], y_vec=mesh_info['y_vec'], z_vec=mesh_info['z_vec']) is not True:
            self.gui_mainWindow.prompt_warning("Configured mesh defines coordinates out of workspace "
                                               "boundaries.\n Please modify mesh config.",
                                               "Invalid mesh configuration")
            return

        #   Get vna config info
        vna_info = self.gui_mainWindow.ui_auto_measurement_window.get_vna_configuration()
        vna_info['meas_name'] = 'AutoMeasurement'   # default AutoMeasurement meas_name

        #   Configure vna by .cst file if selected
        if 'vna_preset_from_file' in vna_info:
            extra_info = self.vna.pna_preset_from_file(vna_info['vna_preset_from_file'], vna_info['meas_name'])
            vna_info['parameter'] = extra_info['parameter']
            vna_info['freq_start'] = extra_info['freq_start']
            vna_info['freq_stop'] = extra_info['freq_stop']
            vna_info['if_bw'] = extra_info['if_bw']
            vna_info['sweep_num_points'] = extra_info['sweep_num_points']
            vna_info['output_power'] = extra_info['output_power']
            vna_info['avg_num'] = extra_info['avg_num']
            self.gui_mainWindow.ui_auto_measurement_window.update_vna_measurement_config_entries(vna_info)
        else:   # Configure vna by manual input
            self.vna.pna_preset()   # clean up vna
            self.vna.pna_add_measurement_detailed(meas_name=vna_info['meas_name'], parameter=vna_info['parameter'],
                                                  freq_start=vna_info['freq_start'], freq_stop=vna_info['freq_stop'],
                                                  if_bw=vna_info['if_bw'],
                                                  sweep_num_points=vna_info['sweep_num_points'],
                                                  output_power=vna_info['output_power'], trigger_manual=True,
                                                  average_number=vna_info['avg_num'])

        #ToDo implement checks to prevent start of invalid auto measurements because invalid vna config

        #   Checks done. Start auto measurement configuration & process
        self.gui_mainWindow.disable_chamber_control_window()
        self.gui_mainWindow.disable_vna_control_window()
        self.gui_mainWindow.ui_auto_measurement_window.vna_config_filepath_check_button.setEnabled(False)

        jog_speed = self.gui_mainWindow.ui_auto_measurement_window.get_auto_measurement_jogspeed()
        zero_pos = (self.zero_pos_x, self.zero_pos_y, self.zero_pos_z)

        if self.auto_measurement_process is None:
            self.auto_measurement_process = AutoMeasurement(chamber=self.chamber, vna=self.vna, vna_info=vna_info,
                                                            x_vec=mesh_info['x_vec'], y_vec=mesh_info['y_vec'],
                                                            z_vec=mesh_info['z_vec'], mov_speed=jog_speed,
                                                            zero_position=zero_pos, file_location=generic_file_path,
                                                            file_type_json=file_type_json_flag,
                                                            file_type_json_readable=file_type_json_readable)

            self.auto_measurement_process.signals.update.connect(
                self.gui_mainWindow.ui_config_window.append_message2console)
            self.auto_measurement_process.signals.update.connect(self.gui_mainWindow.update_status_bar)

            self.auto_measurement_process.signals.position_update.connect(self.chamber_control_update_live_position)

            self.auto_measurement_process.signals.progress.connect(
                self.gui_mainWindow.ui_auto_measurement_window.update_auto_measurement_progress_state)

            self.auto_measurement_process.signals.finished.connect(self.auto_measurement_finished_handler)
            # Error handler to be implemented once error messages are more detailed
            # self.auto_measurement_process.signals.error.connect()

            self.threadpool.start(self.auto_measurement_process)
        else:
            self.gui_mainWindow.prompt_warning("An Automated Measurement Process Thread is already running!",
                                               "More than one Measurement Process")
        return

    def auto_measurement_vna_config_check_button_handler(self):
        """
        Callback for 'Check'-button in ui_auto_measurement > VNA configuration window.
        Sets up the PNA according to given filename and updates UI below accordingly.
        If invalid filename is given, error will occur in terminal due to pna not reacting etc.
        """
        """ Same procedure as in AutoMeasurement start_handler """
        #   Get vna config info
        vna_info = self.gui_mainWindow.ui_auto_measurement_window.get_vna_configuration()
        vna_info['meas_name'] = 'CheckMeasurement'  # default check-meas_name

        #   Configure vna by .cst file if selected
        if 'vna_preset_from_file' in vna_info:
            extra_info = self.vna.pna_preset_from_file(vna_info['vna_preset_from_file'], vna_info['meas_name'])
            vna_info['parameter'] = extra_info['parameter']
            vna_info['freq_start'] = extra_info['freq_start']
            vna_info['freq_stop'] = extra_info['freq_stop']
            vna_info['if_bw'] = extra_info['if_bw']
            vna_info['sweep_num_points'] = extra_info['sweep_num_points']
            vna_info['output_power'] = extra_info['output_power']
            vna_info['avg_num'] = extra_info['avg_num']
            self.gui_mainWindow.ui_auto_measurement_window.update_vna_measurement_config_entries(vna_info)

        return

    def auto_measurement_check_move_boundary(self, x_vec: tuple[float], y_vec: tuple[float], z_vec: tuple[float]):
        """
        Checks if rectangular / cubic mesh is out of chamber workspace.
        :return: True >> movements valid in workspace // False >> invalid mesh coordinates, movements
        """
        if x_vec[0] < 0 or x_vec[-1] > self.__x_max_coor:
            return False
        if y_vec[0] < 0 or y_vec[-1] > self.__y_max_coor:
            return False
        if z_vec[0] < 0 or z_vec[-1] > self.__z_max_coor:
            return False
        return True

    def auto_measurement_finished_handler(self, finished_info: dict):
        self.auto_measurement_process = None
        self.gui_mainWindow.prompt_info(
            info_msg="Auto Measurement process completed.\nData was saved to " + finished_info['file_location'] +
                     '\nMeasurement took ' + finished_info['duration'] + '.',
            window_title="Auto Measurement Completed")
        self.gui_mainWindow.ui_config_window.append_message2console("Auto Measurement Instance deleted.")
        self.gui_mainWindow.enable_chamber_control_window()
        self.gui_mainWindow.enable_vna_control_window()
        self.gui_mainWindow.ui_auto_measurement_window.vna_config_filepath_check_button.setEnabled(True)

    def auto_measurement_goZero_button_handler(self):
        """
        Jogs chamber to currently set "zero position" with z-offset of +10mm to avoid collision.
        Enables to check if position is accurate by visual inspection of the real chamber.

        "Zero Position" means the probe antenna is located exactly above the AUT's center in XY and both antennas are
        virtually touching >> End of ProbeAntenna has same height as top End of AUT
        """
        if self.zero_pos_z is None or self.zero_pos_x is None or self.zero_pos_y is None:
            self.gui_mainWindow.prompt_info("Zero Position not completely defined!\nPlease set all Coordinates of Zero "
                                            "Position first.\n\nWhat is 'Zero Position'?\nZero Position means the probe "
                                            "antenna is located exactly above the AUT's center in XY and both antennas "
                                            "are virtually touching >> End of ProbeAntenna has same height as top End "
                                            "of AUT", "Zero Position unknown")
            return

        if self.ui_chamber_control_process is None and self.auto_measurement_process is None:
            jogspeed = float(self.gui_mainWindow.ui_auto_measurement_window.auto_measurement_jogSpeed_lineEdit.text())
            new_x = self.zero_pos_x
            new_y = self.zero_pos_y
            new_z = self.zero_pos_z

            safe_z_move = new_z + 10  # 10mm offset to avoid collision of antennas

            if self.check_movement_valid({'abs_x': new_x, 'abs_y': new_y, 'abs_z': safe_z_move}):
                self.ui_chamber_control_process = Worker(self.chamber_control_jog_to_abs_coor_routine,
                                                         self.chamber, new_x, new_y, safe_z_move, jogspeed)

                self.ui_chamber_control_process.signals.update.connect(
                    self.gui_mainWindow.ui_chamber_control_window.append_message2console)
                self.ui_chamber_control_process.signals.update.connect(self.gui_mainWindow.update_status_bar)

                self.ui_chamber_control_process.signals.position_update.connect(
                    self.chamber_control_update_live_position)

                self.ui_chamber_control_process.signals.finished.connect(self.chamber_control_thread_finished_handler)

                self.threadpool.start(self.ui_chamber_control_process)
        else:
            self.gui_mainWindow.prompt_warning(
                "Another chamber control request or auto measurement process is currently running!\nPlease wait until it is finished.",
                "Too many Requests")
        return

    def auto_measurement_setZero_button_handler(self):
        """
        Overrides the saved "zero position" with the current position of the chamber.

        "Zero Position" means the probe antenna is located exactly above the AUT's center in XY and both antennas
        are virtually touching >> End of ProbeAntenna has same height as top End of AUT

        This position is used to match the coordinate systems of the AUT and the Probe antenna before starting the
        auto measurement process.
        """
        if self.__x_live is None or self.__y_live is None or self.__z_live is None:
            self.gui_mainWindow.prompt_warning("Position currently unknown!", "Invalid Live Position")
            return

        self.zero_pos_x = self.__x_live
        self.zero_pos_y = self.__y_live
        self.zero_pos_z = self.__z_live

        self.gui_mainWindow.ui_auto_measurement_window.update_current_zero_pos(self.zero_pos_x, self.zero_pos_y,
                                                                               self.zero_pos_z)
        console_msg = "Updated zero position to X:" + str(self.zero_pos_x) + " Y:" + str(self.zero_pos_y) + " Z:" + str(
            self.zero_pos_z)
        self.gui_mainWindow.ui_chamber_control_window.append_message2console(console_msg)
        self.gui_mainWindow.update_status_bar(console_msg)

        return

    def auto_measurement_set_z_zero_from_antenna_dimensions_button_handler(self):
        """
        Reads antenna info from auto measurement window and updates the Z coordinate of the current Zero position
        according to given antenna heights
        """
        self.zero_pos_z = (self.gui_mainWindow.ui_auto_measurement_window.get_probe_antenna_length() +
                           self.gui_mainWindow.ui_auto_measurement_window.get_aut_height() - self.__z_head_bed_offset)

        self.gui_mainWindow.ui_auto_measurement_window.update_current_zero_pos(self.zero_pos_x, self.zero_pos_y,
                                                                               self.zero_pos_z)
        console_msg = "Updated zero coordinate Z: " + str(self.zero_pos_z)
        self.gui_mainWindow.ui_chamber_control_window.append_message2console(console_msg)
        self.gui_mainWindow.update_status_bar(console_msg)

        self.gui_mainWindow.ui_auto_measurement_window.update_mesh_display()
        self.gui_mainWindow.ui_auto_measurement_window.update_2d_plots()

    def auto_measurement_terminate_thread_handler(self):
        """
        Issues a QThred::terminate() on the auto measurement thread that is stored in the process controller
        """
        if self.auto_measurement_process is not None:
            if self.__accept_stop_meas_dialog():
                self.auto_measurement_process.stop()

    def __accept_stop_meas_dialog(self):
        """
        prompts a dialog window asking for automeasurement process termination.
        :return: True >> ok clicked, False >> cancel clicked
        """
        dlg = QMessageBox(self.gui_mainWindow)
        dlg.setWindowTitle("Terminate Auto Measurement")
        dlg.setText("Do you really want to stop the measurement process?\n"
                    "Once stopped it can not be resumed again!\n\n"
                    "Data collected so far will be in desired file-location.")
        dlg.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        dlg.setIcon(QMessageBox.Icon.Question)
        button = dlg.exec()

        if button == QMessageBox.StandardButton.Yes:
            return True
        else:
            return False

    # **UI_display_measurement_window Callbacks** ################################################
    def display_measurement_refresh_file_dropdown(self):
        """
        Searches for available files in results-directory and updates the dropdown menu of display_measurement
        tab accordingly. This function does not filter for any file-types or similiar.
        """
        file_list = [] # delete?
        # Get path to PythonChamberApp directory or prompt warning
        path_PythonChamberApp = os.getcwd()   # should lead to lower PythonChamberApp directory
        path_results_directory = path_PythonChamberApp + "\\results"
        if os.path.isdir(path_results_directory) is False:
            self.gui_mainWindow.update_status_bar("Path-Error occurred while searching for available measurement-files")
            self.gui_mainWindow.prompt_warning("'results' directory was not found when searching for "
                                               "available\n files! This may occur when the root directory from where "
                                               "the app is\nrunning (current working directory) is in the wrong place\n"
                                               "in reference to the results folder.\nMake sure when running the "
                                               "app your working directory is the 'more general' PythonChamberApp "
                                               "folder.\n\nYour current working directory: " + path_PythonChamberApp, "Path"
                                                                                                      "issue")
            return
        file_list = os.listdir(path_results_directory)
        self.gui_mainWindow.ui_display_measurement_window.set_selectable_measurement_files(file_names=file_list)
        self.gui_mainWindow.update_status_bar("Updated available measurement-files to be read")
        return

    def display_measurement_read_file(self):
        """
        Reads file that is selected in mainwindow/display_measurement_window/dropdown to process controller buffer.
        Then initiates updates of GUI objects of display_measurement_window according to buffer.
        """
        self.read_in_measurement_data_buffer = None
        file_name = self.gui_mainWindow.ui_display_measurement_window.get_selected_measurement_file()
        # check for valid file type
        if '.json' not in file_name:
            self.gui_mainWindow.prompt_info("Other file types than json are currently not supported for "
                                            "import and display.", "Illegal file type")
            return

        self.gui_mainWindow.update_status_bar("Start reading measurement file... This may take a moment!")
        # construct path and read file to data-buffer
        path_PythonChamberApp = os.getcwd()  # should lead to lower PythonChamberApp directory
        path_results_directory = path_PythonChamberApp + "\\results"
        file_path = path_results_directory + "\\" + file_name
        with open(file_path, 'r') as json_file:
            self.read_in_measurement_data_buffer = json.load(json_file)

        # add additional vector data to dict for coherent dataflow from processcontroller to sub-methods/windows
        self.read_in_measurement_data_buffer['f_vec'] = np.linspace(
            start=self.read_in_measurement_data_buffer['measurement_config']['freq_start'],
            stop=self.read_in_measurement_data_buffer['measurement_config']['freq_stop'],
            num=self.read_in_measurement_data_buffer['measurement_config']['sweep_num_points'])
        self.read_in_measurement_data_buffer['x_vec'] = np.linspace(
            start=self.read_in_measurement_data_buffer['measurement_config']['mesh_x_min'],
            stop=self.read_in_measurement_data_buffer['measurement_config']['mesh_x_max'],
            num=self.read_in_measurement_data_buffer['measurement_config']['mesh_x_steps'])
        self.read_in_measurement_data_buffer['y_vec'] = np.linspace(
            start=self.read_in_measurement_data_buffer['measurement_config']['mesh_y_min'],
            stop=self.read_in_measurement_data_buffer['measurement_config']['mesh_y_max'],
            num=self.read_in_measurement_data_buffer['measurement_config']['mesh_y_steps'])
        self.read_in_measurement_data_buffer['z_vec'] = np.linspace(
            start=self.read_in_measurement_data_buffer['measurement_config']['mesh_z_min'],
            stop=self.read_in_measurement_data_buffer['measurement_config']['mesh_z_max'],
            num=self.read_in_measurement_data_buffer['measurement_config']['mesh_z_steps'])

        # generate numpy array in data-buffer for faster computation
        #   >> array indexing: [ Value: (1 - amplitude, 2 - phase), Parameter: (1,2,3) , frequency: (num of freq points), x_coor: (num of x steps), y_coor: (num of y steps), z_coor: (num of z steps) ]
        #   e.g. Select phase of S11, @20GHz, X:10, Y:20, Z:30 leads to
        #       >> data_array[1, p, f, x, y, z] with p = find_idx('S11' in measurement_config['parameter']), f = find_idx(20e9 in freq_vector) , ...
        data_array = np.zeros([2, self.read_in_measurement_data_buffer['measurement_config']['parameter'].__len__(),
                                self.read_in_measurement_data_buffer['measurement_config']['sweep_num_points'],
                                self.read_in_measurement_data_buffer['measurement_config']['mesh_x_steps'],
                                self.read_in_measurement_data_buffer['measurement_config']['mesh_y_steps'],
                                self.read_in_measurement_data_buffer['measurement_config']['mesh_z_steps']])
        # fill amplitude values
        parameter_idx = 0
        amplitude_idx = 4   # default for first parameter
        phase_idx = 5       # default for first parameter
        s11_idx = None
        s12_idx = None
        s22_idx = None
        # find which parameters were measured and how long list entries are - initialize indexing
        if 'S11' in self.read_in_measurement_data_buffer['measurement_config']['parameter']:
            s11_idx = [amplitude_idx, phase_idx]
            amplitude_idx += 2
            phase_idx += 2
        if 'S12' in self.read_in_measurement_data_buffer['measurement_config']['parameter']:
            s12_idx = [amplitude_idx, phase_idx]
            amplitude_idx += 2
            phase_idx += 2
        if 'S22' in self.read_in_measurement_data_buffer['measurement_config']['parameter']:
            s22_idx = [amplitude_idx, phase_idx]

        value_list = self.read_in_measurement_data_buffer['data']
        list_idx = 0
        # value_list setup like [ [x0, y0, z0, f0, s11amp0, s11phase0, s12amp0, s12phase0, s22amp0, s22phase0], ...] runs through 1. frequency, 2. x-coor, 3. y-coor, 4. z-coor
        for z_idx in range(self.read_in_measurement_data_buffer['z_vec'].__len__()):
            for y_idx in range(self.read_in_measurement_data_buffer['y_vec'].__len__()):
                for x_idx in range(self.read_in_measurement_data_buffer['x_vec'].__len__()):
                    for f_idx in range(self.read_in_measurement_data_buffer['f_vec'].__len__()):
                        # For each list entry write all S parameter values to array in one go (this inner loop)
                        parameter_idx = 0
                        if s11_idx is not None:
                            data_array[0, parameter_idx, f_idx, x_idx, y_idx, z_idx] = value_list[list_idx][s11_idx[0]]     # amplitude
                            data_array[1, parameter_idx, f_idx, x_idx, y_idx, z_idx] = value_list[list_idx][s11_idx[1]]     # phase
                            parameter_idx += 1
                        if s12_idx is not None:
                            data_array[0, parameter_idx, f_idx, x_idx, y_idx, z_idx] = value_list[list_idx][s12_idx[0]]
                            data_array[1, parameter_idx, f_idx, x_idx, y_idx, z_idx] = value_list[list_idx][s12_idx[1]]
                            parameter_idx += 1
                        if s22_idx is not None:
                            data_array[0, parameter_idx, f_idx, x_idx, y_idx, z_idx] = value_list[list_idx][s22_idx[0]]
                            data_array[1, parameter_idx, f_idx, x_idx, y_idx, z_idx] = value_list[list_idx][s22_idx[1]]
                        list_idx += 1



        self.read_in_measurement_data_buffer['data_array'] = data_array

        # update measurement-data-details in GUI
        self.gui_mainWindow.ui_display_measurement_window.set_measurement_details(
            self.read_in_measurement_data_buffer['measurement_config'])

        # update parameter/display selections and set default values
        self.gui_mainWindow.ui_display_measurement_window.set_selectable_parameters(
            self.read_in_measurement_data_buffer['measurement_config']['parameter'])
        self.gui_mainWindow.ui_display_measurement_window.set_selectable_frequency(
            f_vec=self.read_in_measurement_data_buffer['f_vec'])
        self.gui_mainWindow.ui_display_measurement_window.set_selectable_x_coordinates(
            x_vec=self.read_in_measurement_data_buffer['x_vec'])
        self.gui_mainWindow.ui_display_measurement_window.set_selectable_y_coordinates(
            y_vec=self.read_in_measurement_data_buffer['y_vec'])
        self.gui_mainWindow.ui_display_measurement_window.set_selectable_z_coordinates(
            z_vec=self.read_in_measurement_data_buffer['z_vec'])

        self.gui_mainWindow.update_status_bar("Data read. Objects initialized. start plot updating...")
        # update graphs according to gui selection
        cur_parameter = self.gui_mainWindow.ui_display_measurement_window.get_selected_parameter()
        cur_freq = self.gui_mainWindow.ui_display_measurement_window.get_selected_frequency()
        cur_x_coor = self.gui_mainWindow.ui_display_measurement_window.get_selected_x_coordinate() - self.read_in_measurement_data_buffer['measurement_config']['zero_position'][0]
        cur_y_coor = self.gui_mainWindow.ui_display_measurement_window.get_selected_y_coordinate() - self.read_in_measurement_data_buffer['measurement_config']['zero_position'][1]
        cur_z_coor = self.gui_mainWindow.ui_display_measurement_window.get_selected_z_coordinate() - self.read_in_measurement_data_buffer['measurement_config']['zero_position'][2]

        xz_amplitude_plane_data_from_array = self.read_in_measurement_data_buffer['data_array'][0, 0, 0, :, 0, :]
        yz_amplitude_plane_data_from_array = self.read_in_measurement_data_buffer['data_array'][0, 0, 0, 0, :, :]
        xy_amplitude_plane_data_from_array = self.read_in_measurement_data_buffer['data_array'][0, 0, 0, :, :, 0]

        xz_phase_plane_data_from_array = self.read_in_measurement_data_buffer['data_array'][1, 0, 0, :, 0, :]
        yz_phase_plane_data_from_array = self.read_in_measurement_data_buffer['data_array'][1, 0, 0, 0, :, :]
        xy_phase_plane_data_from_array = self.read_in_measurement_data_buffer['data_array'][1, 0, 0, :, :, 0]

        self.gui_mainWindow.ui_display_measurement_window.update_xz_plane_plot(xz_amplitude_plane_data_from_array,
                                                                               xz_phase_plane_data_from_array)
        self.gui_mainWindow.ui_display_measurement_window.update_yz_plane_plot(yz_amplitude_plane_data_from_array,
                                                                               yz_phase_plane_data_from_array)
        self.gui_mainWindow.ui_display_measurement_window.update_xy_plane_plot(xy_amplitude_plane_data_from_array,
                                                                               xy_phase_plane_data_from_array)

        self.gui_mainWindow.ui_display_measurement_window.enable_plot_interactions()

        self.gui_mainWindow.update_status_bar("Data file read successfully! Graphs enabled.")
        return

    def display_measurement_update_xz_plot_callback(self):
        """
        Reads all information from gui and sends new plane-data to xz plot in Gui.
        Must be connected to adequate signals.
        """
        if self.read_in_measurement_data_buffer is None:
            AssertionError("Update requested before data loaded!")
            return
        amplitude_select = 0
        phase_select = 1
        cur_parameter = self.gui_mainWindow.ui_display_measurement_window.get_selected_parameter()
        parameter_idx = self.read_in_measurement_data_buffer['measurement_config']['parameter'].index(cur_parameter)
        cur_freq_idx = self.gui_mainWindow.ui_display_measurement_window.get_selected_frequency_by_idx()
        cur_y_coor_idx = self.gui_mainWindow.ui_display_measurement_window.get_selected_y_coordinate_by_idx()

        plane_amp_data = self.read_in_measurement_data_buffer['data_array'][amplitude_select, parameter_idx,
                         cur_freq_idx, :, cur_y_coor_idx, :]
        plane_phase_data = self.read_in_measurement_data_buffer['data_array'][phase_select, parameter_idx,
                         cur_freq_idx, :, cur_y_coor_idx, :]

        self.gui_mainWindow.ui_display_measurement_window.update_xz_plane_plot(plane_amp_data, plane_phase_data)
        return

    def display_measurement_update_yz_plot_callback(self):
        """
        Reads all information from gui and sends new plane-data to xy plot in Gui.
        Must be connected to adequate signals.
        """
        if self.read_in_measurement_data_buffer is None:
            AssertionError("Update requested before data loaded!")
            return
        amplitude_select = 0
        phase_select = 1
        cur_parameter = self.gui_mainWindow.ui_display_measurement_window.get_selected_parameter()
        parameter_idx = self.read_in_measurement_data_buffer['measurement_config']['parameter'].index(cur_parameter)
        cur_freq_idx = self.gui_mainWindow.ui_display_measurement_window.get_selected_frequency_by_idx()
        cur_x_coor_idx = self.gui_mainWindow.ui_display_measurement_window.get_selected_x_coordinate_by_idx()

        plane_amp_data = self.read_in_measurement_data_buffer['data_array'][amplitude_select, parameter_idx, cur_freq_idx,
                     cur_x_coor_idx, :, :]
        plane_phase_data = self.read_in_measurement_data_buffer['data_array'][phase_select, parameter_idx, cur_freq_idx,
                     cur_x_coor_idx, :, :]

        self.gui_mainWindow.ui_display_measurement_window.update_yz_plane_plot(plane_amp_data, plane_phase_data)
        return

    def display_measurement_update_xy_plot_callback(self):
        """
        Reads all information from gui and sends new plane-data to xy plot in Gui.
        Must be connected to adequate signals.
        """
        if self.read_in_measurement_data_buffer is None:
            AssertionError("Update requested before data loaded!")
            return
        amplitude_select = 0
        phase_select = 1
        cur_parameter = self.gui_mainWindow.ui_display_measurement_window.get_selected_parameter()
        parameter_idx = self.read_in_measurement_data_buffer['measurement_config']['parameter'].index(cur_parameter)
        cur_freq_idx = self.gui_mainWindow.ui_display_measurement_window.get_selected_frequency_by_idx()
        cur_z_coor_idx = self.gui_mainWindow.ui_display_measurement_window.get_selected_z_coordinate_by_idx()

        plane_amp_data = self.read_in_measurement_data_buffer['data_array'][amplitude_select, parameter_idx,
                         cur_freq_idx, :, :, cur_z_coor_idx]
        plane_phase_data = self.read_in_measurement_data_buffer['data_array'][phase_select, parameter_idx,
                         cur_freq_idx, :, :, cur_z_coor_idx]

        self.gui_mainWindow.ui_display_measurement_window.update_xy_plane_plot(plane_amp_data, plane_phase_data)
        return

    def display_measurement_update_coordinate_lineEdits(self):
        """
        Updates all values of lineEdits next to XYZ sliders
        """
        self.gui_mainWindow.ui_display_measurement_window.update_coordinate_lineEdits()
        return


