"""
The CalibrationRoutine class is meant to implement a routine that moves the probehead over the print-bed in a predefined,
hardcoded fashion, to validate the movement accuracy of the chamber.

The idea is, that a Drawing pen is fixed to the probehead and before starting the routine, the pen is placed on a piece
of paper that is fixed to the print-bed. So the z-coordinate, for which the pen just touches the paper and draws a line,
must be set manually before starting the routine.
The needed z-coordinate is taken from the saved 'zero-position' at that time.
So the workflow is as follows:
1. home the chamber
2. level the bed
3. replace the BLTouch sensor by the drawing pen (an extra holder-plate is needed)
4. manually move the tip of the pen so that it touches the paper
5. save the z-coordinate as 'zero-position'
6. Go to the chamber-tab in the GUI and start the CalibrationRoutine

"""

import time
from PyQt6.QtCore import *  # QObject, pyqtSignal, pyqtSlot, QRunnable
from chamber_net_interface import ChamberNetworkCommands
from AutoMeasurement_Thread import AutoMeasurementSignals
import cmath
import math
from datetime import datetime, timedelta
import json
import os

class CalibrationRoutine(QRunnable):
    """
    This class is a QRunnable that implements a calibration routine for the chamber.
    The routine is hardcoded and moves the probehead in a plane fixed at z-height of current zero position (value must be given).
    It draws multiple squares of different sizes multiple times so one can monitor if the same line is drawn correctly multiple times.
    Moreover one can check if 90° angles are drwan correctly and lengths of lines are correct.

    AutoMeasurementSignals are used to send information to the GUI about updated current position and to what percentage the job is done.
    These infos should be displayed in the Log-Window of the chamber-tab in the GUI.
    Therefor the button to start the routine should be positioned in chamber-tab as well.
    """

    chamber: ChamberNetworkCommands = None
    signals: AutoMeasurementSignals = None
    center_position: list[float] = None     # [x,y,z] in mm where z is the height at which the tip of the pen touches the bed >> from init
    len_square_sides: list[float] = [10.0, 50.0, 100.0, 400.0]    # list of lengths of the sides of the squares to be drawn >> hardcoded
    square_reps: int = 5      # set how many times each square is to be drawn >> hardcoded
    move_pen_up: float = 5.0  # distance to move the pen up after drawing a square >> hardcoded

    def __init__(self, chamber: ChamberNetworkCommands, center_position: list[float]):
        super().__init__()
        self.chamber = chamber
        self.signals = AutoMeasurementSignals()
        self.center_position = center_position

    def run(self):
        # todo implement init with zero position etc, add button to chamber tab and connect to calibration routine instance, connect routine signals to log window etc.