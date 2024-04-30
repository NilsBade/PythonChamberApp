"""
This is the core control-unit that stores all relevant data to reach network devices and
operates as interface between GUI and Network commands.
"""

from PythonChamberApp.chamber_net_interface import ChamberNetworkCommands
import PythonChamberApp.user_interface as ui_pkg
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QThreadPool
from PythonChamberApp.process_controller.AutoMeasurement_Thread import AutoMeasurement
from PythonChamberApp.process_controller.multithread_worker import Worker


class ProcessController:
    # Properties
    chamber: ChamberNetworkCommands = None
    # vna: VNA_NetworkCommands = None
    gui_mainWindow: ui_pkg.MainWindow = None
    gui_app: QApplication = None

    threadpool: QThreadPool = None
    auto_measurement_process: AutoMeasurement = None  # Automation thread that runs in parallel

    def __init__(self):
        self.gui_app = QApplication([])
        self.gui_mainWindow = ui_pkg.MainWindow()
        self.gui_mainWindow.show()

        # input default values into GUI
        self.gui_mainWindow.ui_config_window.chamber_ip_line_edit.setText("134.28.25.201")
        self.gui_mainWindow.ui_config_window.chamber_api_line_edit.setText("03DEBAA8A11941879C08AE1C224A6E2C")

        # Connect all Slots & Signals - **CHAMBER**
        self.gui_mainWindow.ui_config_window.chamber_connect_button.pressed.connect(self.chamber_connect_button_handler_threaded)

        # Connect all Slots & Signals - **VNA**
        self.gui_mainWindow.ui_config_window.vna_connect_button.pressed.connect(self.auto_measurement_start_handler)
        # ...nothing so far...

        # setup AutoMeasurement Thread
        self.threadpool = QThreadPool()
        print("Multithreading with maximum %d threads" % self.threadpool.maxThreadCount())


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
        self.chamber = None
        self.gui_mainWindow.ui_config_window.set_chamber_connected(False)
        self.gui_mainWindow.tabs.setTabEnabled(1, False)  # disables first tab == Chamber Control

        connect_thread = Worker(self.chamber_connect_routine, ip_address, api_key)
        connect_thread.signals.update.connect(self.gui_mainWindow.ui_config_window.append_message2console)
        connect_thread.signals.result.connect(self.chamber_connect_finished_handler)

        self.threadpool.start(connect_thread)

    def chamber_connect_routine(self, ip_address: str, api_key: str, update_callback, progress_callback):
        """
        This routine can be run by a worker thread and pushes intermediate updates as string via signals.update
        """
        # initialize ChamberNetworkCommands Object and store in 'chamber' property if valid
        update_callback.emit(f"Trying to connect to chamber\n ip: {ip_address}, Api-key: {api_key}")
        new_chamber = ChamberNetworkCommands(ip_address=ip_address, api_key=api_key)

        update_callback.emit("Requesting to connect serial port to driver board...")
        response_connect = new_chamber.chamber_connect_serial()

        if response_connect['status_code'] == 204:
            update_callback.emit("Requesting a zero movement to check API-key")
            response_jog = new_chamber.chamber_jog_rel(x=0, y=0, z=0, speed=50)
            update_callback.emit(str(response_jog))
        else:
            update_callback.emit("Connect request failed! No chamber saved.")
            raise Exception("Connection request failed")

        if response_jog['status_code'] == 204:
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

    def auto_measurement_start_handler(self):
        if self.auto_measurement_process is None:
            self.auto_measurement_process = AutoMeasurement(chamber=self.chamber, x_vec=(1.0, 2.0, 3.0),
                                                            y_vec=(1.0, 2.0, 3.0), z_vec=(1.0, 2.0, 3.0), mov_speed=10.0)

            self.auto_measurement_process.signals.update.connect(self.gui_mainWindow.ui_config_window.append_message2console)
            self.auto_measurement_process.signals.finished.connect(self.auto_measurement_finished_handler)
            self.auto_measurement_process.signals.error.connect(self.auto_measurement_finished_handler)

            self.threadpool.start(self.auto_measurement_process)
        else:
            self.gui_mainWindow.prompt_warning("An Automated Measurement Process Thread is already running!", "More than one Measurement Process")
        return

    def auto_measurement_finished_handler(self):
        self.auto_measurement_process = None
        self.gui_mainWindow.ui_config_window.append_message2console("Auto Measurement Instance deleted.")
