"""
This is the entry point to start the PythonChamberApp.
Executing this script imports all necessary modules, initializes all classes and opens the userinterface.
"""

import sys
import PythonChamberApp.user_interface as ui_pkg
from PyQt6.QtWidgets import QApplication

if __name__ == "__main__":
    app = QApplication([])
    window = ui_pkg.Mainwindow()
    window.show()

    app.exec()

