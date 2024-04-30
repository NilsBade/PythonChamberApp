import sys
from PyQt6.QtWidgets import QWidget, QLineEdit,QPushButton, QLabel, QVBoxLayout, QHBoxLayout, QMainWindow, QGridLayout
from PyQt6.QtGui import QIcon


class UI_chamber_control_window(QWidget):

    # Properties

    def __init__(self):
        super().__init__()

        self.button_navigation_widget = self.__init_button_navigation_widget()

        main_layout = QHBoxLayout()
        main_layout.addWidget(self.button_navigation_widget)

        self.setLayout(main_layout)

    def __init_button_navigation_widget(self):
        main_widget = QWidget()
        main_layout = QGridLayout()

