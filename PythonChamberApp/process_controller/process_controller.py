"""
This is the core control-unit that stores all relevant data to reach network devices and
operates as interface between GUI and Network commands.
"""

from PythonChamberApp.chamber_net_interface import ChamberNetworkCommands
import PythonChamberApp.user_interface as ui_pkg
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QThreadPool, QObject, pyqtSignal
from PythonChamberApp.process_controller.AutoMeasurement_Thread import AutoMeasurement
from PythonChamberApp.process_controller.multithread_worker import Worker

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
    # vna: VNA_NetworkCommands = None
    gui_mainWindow: ui_pkg.MainWindow = None
    gui_app: QApplication = None

    threadpool: QThreadPool = None
    auto_measurement_process: AutoMeasurement = None  # Automation thread that runs in parallel
    ui_chamber_control_process: Worker = None  # Assure that only one jog command at a time is requested

    # Position logging
    __x_live: float = None
    __y_live: float = None
    __z_live: float = None

    def __init__(self):
        self.gui_app = QApplication([])
        self.gui_mainWindow = ui_pkg.MainWindow()
        self.gui_mainWindow.show()

        # input default values into config GUI
        self.gui_mainWindow.ui_config_window.chamber_ip_line_edit.setText("134.28.25.201")
        self.gui_mainWindow.ui_config_window.chamber_api_line_edit.setText("03DEBAA8A11941879C08AE1C224A6E2C")

        # Connect all Slots & Signals config_window - **CHAMBER**
        self.gui_mainWindow.ui_config_window.chamber_connect_button.pressed.connect(
            self.chamber_connect_button_handler_threaded)

        # Connect all Slots & Signals config_window - **VNA**
        self.gui_mainWindow.ui_config_window.vna_connect_button.pressed.connect(self.auto_measurement_start_handler)
        # ...nothing so far...

        # connect all Slots & Signals Chamber control window
        self.gui_mainWindow.ui_chamber_control_window.home_all_axis_button.pressed.connect(self.chamber_control_home_all_button_handler)
        self.gui_mainWindow.ui_chamber_control_window.button_move_home_xy.pressed.connect(self.chamber_control_home_xy_button_handler)
        self.gui_mainWindow.ui_chamber_control_window.button_move_home_z.pressed.connect(self.chamber_control_home_z_button_handler)
        self.gui_mainWindow.ui_chamber_control_window.button_move_x_inc.pressed.connect(self.chamber_control_x_inc_button_handler)
        self.gui_mainWindow.ui_chamber_control_window.button_move_x_dec.pressed.connect(self.chamber_control_x_dec_button_handler)
        self.gui_mainWindow.ui_chamber_control_window.button_move_y_inc.pressed.connect(self.chamber_control_y_inc_button_handler)
        self.gui_mainWindow.ui_chamber_control_window.button_move_y_dec.pressed.connect(self.chamber_control_y_dec_button_handler)
        self.gui_mainWindow.ui_chamber_control_window.button_move_z_inc.pressed.connect(self.chamber_control_z_inc_button_handler)
        self.gui_mainWindow.ui_chamber_control_window.button_move_z_dec.pressed.connect(self.chamber_control_z_dec_button_handler)

        # setup AutoMeasurement Thread
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

        self.gui_mainWindow.ui_chamber_control_window.update_live_coor_display(self.__x_live, self.__y_live, self.__z_live)

        return

    # **UI_config_window Callbacks**
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

    def chamber_connect_routine(self, ip_address: str, api_key: str, update_callback, progress_callback, position_update_callback):
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
        self.gui_mainWindow.tabs.setTabEnabled(1, True)  # enables first tab == Chamber Control
        self.gui_mainWindow.ui_config_window.set_chamber_connected(True)
        self.gui_mainWindow.ui_config_window.append_message2console(
            "Printer object was generated and saved to app. Chamber control enabled.")
        return

    # **UI_chamber_control_window Callbacks**
    def chamber_control_thread_finished_handler(self):
        if self.ui_chamber_control_process is None:
            raise Exception("chamber control finished handler was called but no thread was running!")
        else:
            self.ui_chamber_control_process = None
        return

    def chamber_control_home_all_button_handler(self):
        if self.ui_chamber_control_process is None:
            self.ui_chamber_control_process = Worker(self.chamber_control_home_all_routine, self.chamber)

            self.ui_chamber_control_process.signals.update.connect(self.gui_mainWindow.ui_chamber_control_window.append_message2console)
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
            self.gui_mainWindow.prompt_info("Homing seems to be finished.\nCoordinates will be logged from now on and manual control is enabled.", "Check chamber state manually")
        return

    def chamber_control_home_all_routine(self, chamber: ChamberNetworkCommands, update_callback, progress_callback, position_update_callback):
        """
        This routine can be given to a worker to request all-axis-homing in separate thread
        """
        update_callback.emit("Request to home all axis")
        response = chamber.chamber_home_with_flag(axis='xyz')
        if response['status_code'] == 204:
            update_callback.emit("Manual chamber control enabled")
            position_update_callback.emit({'abs_x': 0.0, 'abs_y': 0.0, 'abs_z': 0.0})
            progress_callback.emit(response)
        else:
            update_callback.emit("Something went wrong! HTTP response status code: " + response['status_code'] + ' ' + response['content'])
        return

    def chamber_control_home_xy_button_handler(self):
        if self.ui_chamber_control_process is None:
            self.ui_chamber_control_process = Worker(self.chamber_control_home_xy_routine, self.chamber)

            self.ui_chamber_control_process.signals.update.connect(self.gui_mainWindow.ui_chamber_control_window.append_message2console)
            self.ui_chamber_control_process.signals.update.connect(self.gui_mainWindow.update_status_bar)

            self.ui_chamber_control_process.signals.position_update.connect(self.chamber_control_update_live_position)

            self.ui_chamber_control_process.signals.finished.connect(self.chamber_control_thread_finished_handler)

            self.threadpool.start(self.ui_chamber_control_process)
        else:
            self.gui_mainWindow.prompt_warning(
                "Another chamber control request is processing at the moment!\nPlease wait until it is finished.",
                "Too many Requests")
        return
    def chamber_control_home_xy_routine(self, chamber: ChamberNetworkCommands, update_callback, progress_callback, position_update_callback):
        """
        This routine can be given to a worker to request xy-axis-homing in separate thread
        """
        update_callback.emit("Request to home xy-axis")
        response = chamber.chamber_home_with_flag(axis='xy')
        if response['status_code'] == 204:
            update_callback.emit("OK")
            position_update_callback.emit({'abs_x': 0.0, 'abs_y': 0.0})
        else:
            update_callback.emit("Something went wrong! HTTP response status code: " + response['status_code'] + ' ' + response['content'])
        return

    def chamber_control_home_z_button_handler(self):
        if self.ui_chamber_control_process is None:
            self.ui_chamber_control_process = Worker(self.chamber_control_home_z_routine, self.chamber)

            self.ui_chamber_control_process.signals.update.connect(self.gui_mainWindow.ui_chamber_control_window.append_message2console)
            self.ui_chamber_control_process.signals.update.connect(self.gui_mainWindow.update_status_bar)

            self.ui_chamber_control_process.signals.position_update.connect(self.chamber_control_update_live_position)

            self.ui_chamber_control_process.signals.finished.connect(self.chamber_control_thread_finished_handler)

            self.threadpool.start(self.ui_chamber_control_process)
        else:
            self.gui_mainWindow.prompt_warning(
                "Another chamber control request is processing at the moment!\nPlease wait until it is finished.",
                "Too many Requests")
        return

    def chamber_control_home_z_routine(self, chamber: ChamberNetworkCommands, update_callback, progress_callback, position_update_callback):
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
            self.ui_chamber_control_process = Worker(self.chamber_control_jog_one_axis_rel_routine, self.chamber, 'x', jogspeed, stepsize)

            self.ui_chamber_control_process.signals.update.connect(self.gui_mainWindow.ui_chamber_control_window.append_message2console)
            self.ui_chamber_control_process.signals.update.connect(self.gui_mainWindow.update_status_bar)

            self.ui_chamber_control_process.signals.position_update.connect(self.chamber_control_update_live_position)

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
            self.ui_chamber_control_process = Worker(self.chamber_control_jog_one_axis_rel_routine, self.chamber, 'x', jogspeed, stepsize)

            self.ui_chamber_control_process.signals.update.connect(self.gui_mainWindow.ui_chamber_control_window.append_message2console)
            self.ui_chamber_control_process.signals.update.connect(self.gui_mainWindow.update_status_bar)

            self.ui_chamber_control_process.signals.position_update.connect(self.chamber_control_update_live_position)

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
            self.ui_chamber_control_process = Worker(self.chamber_control_jog_one_axis_rel_routine, self.chamber, 'y', jogspeed, stepsize)

            self.ui_chamber_control_process.signals.update.connect(self.gui_mainWindow.ui_chamber_control_window.append_message2console)
            self.ui_chamber_control_process.signals.update.connect(self.gui_mainWindow.update_status_bar)

            self.ui_chamber_control_process.signals.position_update.connect(self.chamber_control_update_live_position)

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
            self.ui_chamber_control_process = Worker(self.chamber_control_jog_one_axis_rel_routine, self.chamber, 'y', jogspeed, stepsize)

            self.ui_chamber_control_process.signals.update.connect(self.gui_mainWindow.ui_chamber_control_window.append_message2console)
            self.ui_chamber_control_process.signals.update.connect(self.gui_mainWindow.update_status_bar)

            self.ui_chamber_control_process.signals.position_update.connect(self.chamber_control_update_live_position)

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
            self.ui_chamber_control_process = Worker(self.chamber_control_jog_one_axis_rel_routine, self.chamber, 'z', jogspeed, stepsize)

            self.ui_chamber_control_process.signals.update.connect(self.gui_mainWindow.ui_chamber_control_window.append_message2console)
            self.ui_chamber_control_process.signals.update.connect(self.gui_mainWindow.update_status_bar)

            self.ui_chamber_control_process.signals.position_update.connect(self.chamber_control_update_live_position)

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
            self.ui_chamber_control_process = Worker(self.chamber_control_jog_one_axis_rel_routine, self.chamber, 'z', jogspeed, stepsize)

            self.ui_chamber_control_process.signals.update.connect(self.gui_mainWindow.ui_chamber_control_window.append_message2console)
            self.ui_chamber_control_process.signals.update.connect(self.gui_mainWindow.update_status_bar)

            self.ui_chamber_control_process.signals.position_update.connect(self.chamber_control_update_live_position)

            self.ui_chamber_control_process.signals.finished.connect(self.chamber_control_thread_finished_handler)

            self.threadpool.start(self.ui_chamber_control_process)
        else:
            self.gui_mainWindow.prompt_warning(
                "Another chamber control request is processing at the moment!\nPlease wait until it is finished.",
                "Too many Requests")
        return
    def chamber_control_jog_one_axis_rel_routine(self, chamber: ChamberNetworkCommands, axis: str, jogspeed: float, rel_coor: float, update_callback, progress_callback, position_update_callback):
        """
        This routine receives chamber object and desired new absolute coordinate on given axis.
        It should be used in combination with arrow-button menu.

        :param chamber: stored network chamber of process controller providing (network) interface to chamber
        :param axis: the axis that should be jogged - either 'x' or 'y' or 'z'
        :param jogspeed: speed to move in [mm/s]
        :param rel_coor: new desired absolute coordinate calculated from live coordinate beforehand!
        """
        update_callback.emit("Request Jog " + axis + " by " + str(rel_coor) + " mm with " + str(jogspeed) + " mm/s")
        if axis == 'x':
            response = chamber.chamber_jog_rel(x= rel_coor, speed = jogspeed)
            position_update_callback.emit({'rel_x': rel_coor})
        elif axis == 'y':
            response = chamber.chamber_jog_rel(y= rel_coor, speed = jogspeed)
            position_update_callback.emit({'rel_y': rel_coor})
        elif axis == 'z':
            response = chamber.chamber_jog_rel(z= rel_coor, speed = jogspeed)
            position_update_callback.emit({'rel_z': rel_coor})
        else:
            update_callback("jog_one_axis routine got invalid axis parameter!")
            raise Exception("jog_one_axis routine got invalid axis parameter!")

        return



    # **UI_vna_control_window Callbacks**

    # **UI_automeasurement_window Callbacks**
    def auto_measurement_start_handler(self):
        if self.auto_measurement_process is None:
            self.auto_measurement_process = AutoMeasurement(chamber=self.chamber, x_vec=(1.0, 2.0, 3.0),
                                                            y_vec=(1.0, 2.0, 3.0), z_vec=(1.0, 2.0, 3.0),
                                                            mov_speed=10.0)

            self.auto_measurement_process.signals.update.connect(
                self.gui_mainWindow.ui_config_window.append_message2console)
            self.auto_measurement_process.signals.update.connect(self.gui_mainWindow.update_status_bar)
            self.auto_measurement_process.signals.finished.connect(self.auto_measurement_finished_handler)
            self.auto_measurement_process.signals.error.connect(self.auto_measurement_finished_handler)

            self.threadpool.start(self.auto_measurement_process)
        else:
            self.gui_mainWindow.prompt_warning("An Automated Measurement Process Thread is already running!",
                                               "More than one Measurement Process")
        return

    def auto_measurement_finished_handler(self):
        self.auto_measurement_process = None
        self.gui_mainWindow.ui_config_window.append_message2console("Auto Measurement Instance deleted.")
