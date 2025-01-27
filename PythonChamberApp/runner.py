"""
This is the entry point to start the PythonChamberApp.
Executing this script imports all necessary modules, initializes all classes and opens the userinterface.
"""
import importlib
import sys
import process_controller
import os


# def take_screenshot(widget, filename):
#     # Holen des Screenshots des gesamten Widgets
#     screenshot = widget.grab()
#
#     # Speichern des Screenshots als Bilddatei
#     screenshot.save(filename, 'png')

if __name__ == "__main__":
    # add extra dll paths before import pyvisa to be able to use keysight pyvisa implementation
    os.add_dll_directory('C:\\Program Files\\Keysight\\IO Libraries Suite\\bin')
    os.add_dll_directory('C:\\Program Files (x86)\\Keysight\\IO Libraries Suite\\bin')

    measurement_process_controller = process_controller.ProcessController()

    # """ Save Screenshots for Master-thesis """
    # for i in range(0,6):
    #     measurement_process_controller.gui_mainWindow.tabs.setCurrentIndex(i)
    #     take_screenshot(measurement_process_controller.gui_mainWindow, 'mainWindow'+str(i)+'.png')

    sys.exit(measurement_process_controller.gui_app.exec())


