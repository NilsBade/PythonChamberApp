"""
This file stores the mainwindow class and all necessary PyQt6 classes to construct the app's UI.
"""

import sys
from PyQt6.QtWidgets import QMainWindow, QWidget, QStatusBar, QTabWidget
from PythonChamberApp.user_interface.ui_config_window import UI_config_window
from PythonChamberApp.user_interface.ui_chamber_control_window import UI_chamber_control_window
from PythonChamberApp.user_interface.ui_vna_control_window import UI_vna_control_window


class MainWindow(QMainWindow):
    """
    This Class initializes the main-application-window with its tabs and sub windows.
    It organizes window-switching and stores input data when switching.

    All sub-windows are organized as QWidgets and stored/defined in separate classes.
    """

    # Properties
    ui_config_window: UI_config_window = None
    ui_chamber_control_window: UI_chamber_control_window = None
    ui_vna_control_window: UI_vna_control_window = None

    main_status_bar: QStatusBar = None

    def __init__(self):
        super().__init__()
        self.setWindowTitle("PythonChamberApp V1.0")
        self.setGeometry(100, 100, 900, 500)  # Set window dimensions

        self.__setup_center_widgets()
        self.__setup_statusbar()

    def __setup_statusbar(self):
        main_status_bar = self.statusBar()
        main_status_bar.showMessage("I have been initialized!")
        return

    def __setup_center_widgets(self):
        self.tabs = QTabWidget()
        self.tabs.setTabPosition(QTabWidget.TabPosition.North)

        self.ui_config_window = UI_config_window()
        self.ui_chamber_control_window = UI_chamber_control_window()
        self.ui_vna_control_window = UI_vna_control_window()

        self.tabs.addTab(self.ui_config_window, 'Config')  # Tab 0
        self.tabs.addTab(self.ui_chamber_control_window, 'Chamber control')  # Tab 1
        self.tabs.addTab(self.ui_vna_control_window, 'VNA control')  # Tab 2
        self.tabs.setTabEnabled(0, True)
        self.tabs.setTabEnabled(1, False)
        self.tabs.setTabEnabled(2, False)

        self.setCentralWidget(self.tabs)
