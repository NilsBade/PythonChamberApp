"""
This is the core control-unit that stores all relevant data to reach network devices and
operates as interface between GUI and Network commands.
"""
import os.path

from PythonChamberApp.chamber_net_interface import ChamberNetworkCommands
import PythonChamberApp.user_interface as ui_pkg
from PyQt6.QtWidgets import QApplication, QMessageBox
from PyQt6.QtCore import QThreadPool, QObject, pyqtSignal
from PythonChamberApp.process_controller.AutoMeasurement_Thread import AutoMeasurement
from PythonChamberApp.process_controller.multithread_worker import Worker
from PythonChamberApp.vna_net_interface.vna_net_interface import E8361RemoteGPIB
import numpy as np


class ProcessControllerSignals(QObject):
    """
    This class defines signals related to the ProcessController

    position_changed
        >> signals that callback has updated the live position of the chamber head
    """
    position_changed = pyqtSignal()


class ProcessController:
    # Properties
    chamber: ChamberNetworkCommands = None
    vna: E8361RemoteGPIB = E8361RemoteGPIB()
    gui_mainWindow: ui_pkg.MainWindow = None
    gui_app: QApplication = None

    threadpool: QThreadPool = None
    auto_measurement_process: AutoMeasurement = None  # Automation thread that runs in parallel
    ui_chamber_control_process: Worker = None  # Assure that only one jog command at a time is requested

    # Position logging & validity check
    __x_live: float = None
    __y_live: float = None
    __z_live: float = None
    __x_max_coor: float = 510.0  # Measured with V1 BL Touch sensor mount, 30.05.2024
    __y_max_coor: float = 454.0
    __z_max_coor: float = 908.0
    __z_head_bed_offset = 49.0

    # Auto measurement data
    zero_pos_x: float = None
    zero_pos_y: float = None
    zero_pos_z: float = None

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
        self.gui_mainWindow.ui_config_window.vna_list_ressources_button.pressed.connect(self.vna_list_ressources_button_handler)
        self.gui_mainWindow.ui_config_window.vna_connect_button.pressed.connect(self.vna_connect_button_handler)

        # connect all Slots & Signals Chamber control window
        self.gui_mainWindow.ui_chamber_control_window.home_all_axis_button.pressed.connect(
            self.chamber_control_home_all_button_handler)
        self.gui_mainWindow.ui_chamber_control_window.z_tilt_adjust_button.pressed.connect(
            self.chamber_control_z_tilt_button_handler)
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

        # setup AutoMeasurement
        self.zero_pos_x = self.__x_max_coor / 2
        self.zero_pos_y = self.__y_max_coor / 2
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
        self.gui_mainWindow.ui_auto_measurement_window.auto_measurement_start_button.pressed.connect(
            self.auto_measurement_start_handler)
        self.gui_mainWindow.ui_auto_measurement_window.auto_measurement_stop_button.pressed.connect(
            self.auto_measurement_terminate_thread_handler)

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
        self.gui_mainWindow.tabs.setTabEnabled(1, False)  # disables first tab == Chamber Control

        connect_thread = Worker(self.chamber_connect_routine, ip_address, api_key)
        connect_thread.signals.update.connect(self.gui_mainWindow.ui_config_window.append_message2console)
        connect_thread.signals.update.connect(self.gui_mainWindow.update_status_bar)
        connect_thread.signals.result.connect(self.chamber_connect_finished_handler)

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

    def chamber_connect_finished_handler(self, new_chamber: ChamberNetworkCommands):
        self.chamber = new_chamber
        self.gui_mainWindow.enable_chamber_control_window()
        self.gui_mainWindow.enable_auto_measurement_window()
        self.gui_mainWindow.ui_config_window.set_chamber_connected(True)
        self.gui_mainWindow.ui_config_window.append_message2console(
            "Printer object was generated and saved to app. Chamber control enabled.")
        return

    def vna_list_ressources_button_handler(self):
        """
        Detects all available instruments of pyvisa RessourceManager object and prints them to console
        of config window.
        """
        ressource_string = self.vna.list_resources()
        self.gui_mainWindow.ui_config_window.append_message2console(f"Available Ressources detected: {ressource_string}")
        return

    def vna_connect_button_handler(self):
        """
        Reads input visa address from ui config window and starts vna_connect_routine.
        """
        visa_address = self.gui_mainWindow.ui_config_window.get_vna_visa_address()
        if visa_address == "":
            self.gui_mainWindow.ui_config_window.append_message2console("Please input a visa address first. Available addresses are printed to console when clicking on 'List available resources' on the left.")
            return
        #ToDo start the connect routine and connect signals to update console

    def vna_connect_routine(self, visa_address: str, update_callback, progress_callback, position_update_callback):
        """
        Sends '*IDN?' query to given visa_address-device and pushes the answer or error to update_callback.
        """
        #ToDo implement routine that send '*IDN?* query to given device, send updates via update_callback-signal and handles timeouts etc. by printing error to console(?). Eventually adapt vna interface library to be able to catch exceptions.

    #def vna_connect_finished_handler(self):


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
            update_callback.emit("Requests Movement to Front")
            chamber.chamber_jog_abs(x=258.0, y=0.0, z=100, speed=50.0)
            position_update_callback.emit({'abs_x': 258.0, 'abs_y': 0.0, 'abs_z': 100.0})
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
        update_callback.emit("Adjustment completed. Moving to front...")
        chamber.chamber_jog_abs(x=258.0, y=0.0, z=100, speed=75.0)
        position_update_callback.emit({'abs_x': 258.0, 'abs_y': 0.0, 'abs_z': 100.0})

        return

    # **UI_vna_control_window Callbacks** ################################################

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
        meas_file_name = self.gui_mainWindow.ui_auto_measurement_window.get_new_filename()
        path_workdirectory = os.getcwd()
        if not os.path.exists(os.path.join(path_workdirectory + '/results')):
            os.makedirs(os.path.join(path_workdirectory + '/results'))
        path_results_folder = os.path.join(os.getcwd() + '/results')

        #   Check if filename is valid, avoid override
        new_file_path_substring = "/" + self.gui_mainWindow.ui_auto_measurement_window.get_new_filename() + ".txt"
        new_file_path = os.path.join(path_results_folder + new_file_path_substring)
        if os.path.isfile(new_file_path):
            self.gui_mainWindow.prompt_warning("A measurement file with the given name is already stored. \n"
                                               "Overrride is not permitted. Please change the desired file name.",
                                               "Duplicate Filename")
            return

        #   Checks done. Start auto measurement configuration & process
        self.gui_mainWindow.disable_chamber_control_window()
        self.gui_mainWindow.disable_vna_control_window()

        mesh_info = self.gui_mainWindow.ui_auto_measurement_window.get_mesh_cubic_data()
        jog_speed = self.gui_mainWindow.ui_auto_measurement_window.get_auto_measurement_jogspeed()

        if self.auto_measurement_process is None:
            self.auto_measurement_process = AutoMeasurement(chamber=self.chamber, x_vec=mesh_info['x_vec'],
                                                            y_vec=mesh_info['y_vec'], z_vec=mesh_info['z_vec'],
                                                            mov_speed=jog_speed, file_location=new_file_path)

            self.auto_measurement_process.signals.update.connect(
                self.gui_mainWindow.ui_config_window.append_message2console)
            self.auto_measurement_process.signals.update.connect(self.gui_mainWindow.update_status_bar)

            self.auto_measurement_process.signals.progress.connect(
                self.gui_mainWindow.ui_auto_measurement_window.update_auto_measurement_progress_state)

            self.auto_measurement_process.signals.finished.connect(self.auto_measurement_finished_handler)
            self.auto_measurement_process.signals.error.connect(self.auto_measurement_finished_handler)

            self.threadpool.start(self.auto_measurement_process)
        else:
            self.gui_mainWindow.prompt_warning("An Automated Measurement Process Thread is already running!",
                                               "More than one Measurement Process")
        return

    def auto_measurement_finished_handler(self, finished_info: dict):
        self.auto_measurement_process = None
        self.gui_mainWindow.prompt_info(
            info_msg="Auto Measurement process completed.\nData was saved to " + finished_info['file_location'],
            window_title="Auto Measurement Completed")
        self.gui_mainWindow.ui_config_window.append_message2console("Auto Measurement Instance deleted.")
        self.gui_mainWindow.enable_chamber_control_window()
        self.gui_mainWindow.enable_vna_control_window()

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
