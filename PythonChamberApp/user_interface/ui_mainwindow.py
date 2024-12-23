"""
This file stores the mainwindow class and all necessary PyQt6 classes to construct the app's UI.
"""

import sys
from PyQt6.QtWidgets import QMainWindow, QWidget, QStatusBar, QTabWidget, QMessageBox
from .ui_config_window import UI_config_window
from .ui_chamber_control_window import UI_chamber_control_window
from .ui_vna_control_window import UI_vna_control_window
from .ui_auto_measurement import UI_auto_measurement_window
from .ui_display_measurement_window import UI_display_measurement_window


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
    ui_auto_measurement_window: UI_auto_measurement_window = None
    ui_display_measurement_window: UI_display_measurement_window = None

    main_status_bar: QStatusBar = None

    def __init__(self, chamber_x_max_coor: float, chamber_y_max_coor: float, chamber_z_max_coor: float, chamber_z_head_bed_offset: float):
        super().__init__()
        self.setWindowTitle("PythonChamberApp V1.3 - dev")    ### APP VERSION NUMBERING ###
        self.setGeometry(100, 100, 1550, 800)  # Set window dimensions

        self.__setup_center_widgets(chamber_x_max_coor, chamber_y_max_coor, chamber_z_max_coor, chamber_z_head_bed_offset)
        self.__setup_statusbar()

    def __setup_statusbar(self):
        self.main_status_bar = self.statusBar()
        self.main_status_bar.showMessage("I have been initialized!")
        return

    def __setup_center_widgets(self, chamber_x_max_coor: float, chamber_y_max_coor: float, chamber_z_max_coor: float, chamber_z_head_bed_offset: float):
        self.tabs = QTabWidget()
        self.tabs.setTabPosition(QTabWidget.TabPosition.North)

        self.ui_config_window = UI_config_window()
        self.ui_chamber_control_window = UI_chamber_control_window(chamber_x_max_coor, chamber_y_max_coor, chamber_z_max_coor, chamber_z_head_bed_offset)
        self.ui_vna_control_window = UI_vna_control_window()
        self.ui_auto_measurement_window = UI_auto_measurement_window(chamber_x_max_coor, chamber_y_max_coor, chamber_z_max_coor, chamber_z_head_bed_offset)
        self.ui_display_measurement_window = UI_display_measurement_window()

        self.tabs.addTab(self.ui_config_window, 'Config')  # Tab 0
        self.tabs.addTab(self.ui_chamber_control_window, 'Chamber control')  # Tab 1
        self.tabs.addTab(self.ui_vna_control_window, 'VNA control')  # Tab 2
        self.tabs.addTab(self.ui_auto_measurement_window, 'Auto Measurement')   # Tab 3
        self.tabs.addTab(self.ui_display_measurement_window, 'Display Measurements')
        self.tabs.setTabEnabled(0, True)
        self.tabs.setTabEnabled(1, False)       # Modify here when testing GUI elements without valid app config
        self.tabs.setTabEnabled(2, False)
        self.tabs.setTabEnabled(3, False)
        self.tabs.setTabEnabled(4, True)        # always enable!

        self.setCentralWidget(self.tabs)
        return

    def prompt_info(self, info_msg: str, window_title: str):
        """
        Opens a Dialog Window with Info mark in front of the main window.
        Displays given info_msg and blocks rest of the application until accepted.
        """
        dlg = QMessageBox(self)
        dlg.setWindowTitle(window_title)
        dlg.setText(info_msg)
        dlg.setStandardButtons(QMessageBox.StandardButton.Ok)
        dlg.setIcon(QMessageBox.Icon.Question)
        dlg.exec()
        return

    def prompt_warning(self, warn_msg: str, window_title: str):
        """
        Opens a Warning Window with Warning mark in front of the main window.
        Displays given warn_msg and blocks rest of the application until accepted.
        """
        dlg = QMessageBox(self)
        dlg.setWindowTitle(window_title)
        dlg.setText(warn_msg)
        dlg.setStandardButtons(QMessageBox.StandardButton.Ok)
        dlg.setIcon(QMessageBox.Icon.Warning)
        dlg.exec()
        return

    def prompt_question(self, question_msg: str, window_title: str):
        """
        Opens a Question Window with Question mark in front of the main window.
        Displays given question_msg and blocks rest of the application until accepted.
        Returns True if 'Yes' was clicked, False if 'No' was clicked.
        """
        button = QMessageBox.question(self, window_title, question_msg, QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if button == QMessageBox.StandardButton.Yes:
            return True
        else:
            return False

    def update_status_bar(self, status_msg: str):
        self.main_status_bar.showMessage(status_msg)
        return

    def enable_chamber_control_window(self):
        self.tabs.setTabEnabled(1, True)

    def disable_chamber_control_window(self):
        self.tabs.setTabEnabled(1, False)

    def enable_vna_control_window(self):
        self.tabs.setTabEnabled(2, True)

    def disable_vna_control_window(self):
        self.tabs.setTabEnabled(2, False)

    def enable_auto_measurement_window(self):
        self.tabs.setTabEnabled(3, True)

    def disable_auto_measurement_window(self):
        self.tabs.setTabEnabled(3, False)

