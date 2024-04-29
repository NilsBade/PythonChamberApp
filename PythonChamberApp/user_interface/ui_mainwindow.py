"""
This file stores the mainwindow class and all necessary PyQt6 classes to construct the app's UI.
"""

import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QPushButton, QWidget, QStatusBar, QToolBar, QTabWidget
from PyQt6.QtGui import QAction
from PyQt6.QtCore import Qt
from PythonChamberApp.user_interface.ui_config_window import UI_config_window
from PythonChamberApp.user_interface.ui_chamber_control_window import UI_chamber_control_window
from PythonChamberApp.user_interface.ui_vna_control_window import UI_vna_control_window


class Mainwindow(QMainWindow):
    """
    This Class sets up the base for the PythonChamberApp.
    It initializes the main-application-window with its tool- and menu-bars,
    stores all sub-windows as QWidgets in its properties and organizes window-switching.

    All sub-windows are organized as QWidgets and stored in separate classes.
    """

    # Properties
    central_widget: QWidget = None

    ui_config_window: QWidget = None
    ui_chamber_control_window: QWidget = None
    ui_vna_control_window: QWidget = None

    main_status_bar: QStatusBar = None
    main_toolbar: QToolBar = None
    toolbar_config_pressed: QAction = None
    toolbar_chamber_pressed: QAction = None
    toolbar_vna_pressed: QAction = None

    def __init__(self):
        super().__init__()
        self.setWindowTitle("PythonChamberApp V1.0")
        self.setGeometry(100, 100, 800, 400)  # Set window dimensions

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
        self.tabs.setTabEnabled(1, True)
        self.tabs.setTabEnabled(2, False)

        self.setCentralWidget(self.tabs)
