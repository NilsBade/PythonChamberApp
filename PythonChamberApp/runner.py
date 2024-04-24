"""
This is the entry point to start the PythonChamberApp.
Executing this script imports all necessary modules, initializes all classes and opens the userinterface.
"""

import PythonChamberApp.connection_handler as connection_handler

if __name__ == "__main__":
    connection_handler.class_file.print_hi()
