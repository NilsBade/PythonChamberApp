"""
This is the entry point to start the PythonChamberApp.
Executing this script imports all necessary modules, initializes all classes and opens the userinterface.
"""

import sys
import process_controller

if __name__ == "__main__":
    measurement_process_controller = process_controller.ProcessController()
    sys.exit(measurement_process_controller.gui_app.exec())


