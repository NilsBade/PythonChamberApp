"""
This is the core control-unit that stores all relevant data to reach network devices and
operates as interface between GUI and Network commands.
"""


from PythonChamberApp.chamber_net_interface import ChamberNetworkCommands
import PythonChamberApp.user_interface as ui_pkg
from PyQt6.QtWidgets import QApplication


class ProcessController:

    # Properties
    chamber: ChamberNetworkCommands = None
    # vna: VNA_NetworkCommands = None
    gui_mainWindow: ui_pkg.MainWindow = None
    gui_app: QApplication = None

    def __init__(self):
        self.gui_app = QApplication([])
        self.gui_mainWindow = ui_pkg.MainWindow()
        self.gui_mainWindow.show()

        # input default values into GUI
        self.gui_mainWindow.ui_config_window.chamber_ip_line_edit.setText("134.28.25.201")
        self.gui_mainWindow.ui_config_window.chamber_api_line_edit.setText("03DEBAA8A11941879C08AE1C224A6E2C")
        # Connect all Slots & Signals
        self.gui_mainWindow.ui_config_window.chamber_connect_button.pressed.connect(self.chamber_connect_button_handler)

    # Following methods represent Slots that are connected to the GUI buttons
    def chamber_connect_button_handler(self):
        """
        Reads ip and api-key from user interface and initializes a ChamberNetworkCommands object that is stored
        in the ProcessController's properties.

        Also checks if ip-api_key-combination is valid by requesting a zero movement and checking the response.
        Output can be seen in status label of GUI and in the console of config window.
        """
        # read data from GUI
        connect_data = self.gui_mainWindow.ui_config_window.get_chamber_connect_data()
        ip_address = connect_data['ip_address']
        api_key = connect_data['api_key']

        # initialize ChamberNetworkCommands Object and store in 'chamber' property if valid
        self.gui_mainWindow.ui_config_window.append_message2console(f"Trying to connect to chamber\n ip: {ip_address}, Api-key: {api_key}...")
        new_chamber = ChamberNetworkCommands(ip_address=ip_address, api_key=api_key)

        self.gui_mainWindow.ui_config_window.append_message2console("Requesting to connect serial port to driver board...")
        response_connect = new_chamber.chamber_connect_serial()
        self.gui_mainWindow.ui_config_window.append_message2console(str(response_connect))

        if response_connect['status_code'] == 204:
            self.gui_mainWindow.ui_config_window.append_message2console("Requesting a zero movement to check API-key")
            response_jog = new_chamber.chamber_jog_rel(x=0, y=0, z=0, speed=50)
            self.gui_mainWindow.ui_config_window.append_message2console(str(response_jog))
        else:
            self.gui_mainWindow.ui_config_window.append_message2console("Connect request failed! No chamber saved.")
            return

        if response_jog['status_code'] == 204:
            self.chamber = new_chamber
            self.gui_mainWindow.tabs.setTabEnabled(1, True)     # enables first tab == Chamber Control
            self.gui_mainWindow.ui_config_window.append_message2console("Jog Request was accepted! Printer was saved in ProcessController and manual printer control enabled.")
        else:
            self.gui_mainWindow.ui_config_window.append_message2console("Jog Request failed! No chamber saved.")

        return



