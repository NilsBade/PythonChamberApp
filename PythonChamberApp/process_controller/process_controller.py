"""
This is the core control-unit that stores all relevant data to reach network devices and
operates as interface between GUI and Network commands.
"""

import sys
from PythonChamberApp.chamber_net_interface import ChamberNetworkCommands
import PythonChamberApp.user_interface as ui_pkg
from PyQt6.QtWidgets import QApplication

class ProcessController:

    # Properties
    chamber: ChamberNetworkCommands = None
    # vna: VNA_NetworkCommands = None
    gui_mainwindow: ui_pkg.Mainwindow = None
    gui_app: QApplication = None

    def __init__(self):
        self.gui_app = QApplication([])
        self.gui_mainwindow = ui_pkg.Mainwindow()
        self.gui_mainwindow.show()

