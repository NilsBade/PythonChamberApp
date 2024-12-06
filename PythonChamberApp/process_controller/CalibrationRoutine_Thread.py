"""
The CalibrationRoutine class is meant to implement a routine that moves the probehead over the print-bed in a predefined,
hardcoded fashion, to validate the movement accuracy of the chamber.

The idea is, that a Drawing pen is fixed to the probehead and before starting the routine, the pen is placed on a piece
of paper that is fixed to the print-bed. So the z-coordinate, for which the pen just touches the paper and draws a line,
must be set manually before starting the routine.
The needed z-coordinate is taken from the position at that time.
So the workflow is as follows:
1. home the chamber
2. level the bed
3. replace the BLTouch sensor by the drawing pen (an extra holder-plate is needed)
4. manually move the tip of the pen so that it touches the paper (z important, XY can be anywhere)
5. Go to the chamber-tab in the GUI and start the CalibrationRoutine by button-click
-> current position's z-coordinate is taken as the z-coordinate for drawing

"""

import time
from PyQt6.QtCore import *  # QObject, pyqtSignal, pyqtSlot, QRunnable
from chamber_net_interface import ChamberNetworkCommands
from .multithread_worker import WorkerSignals
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
    Moreover, one can check if 90° angles are drawn correctly and lengths of lines are correct.

    AutoMeasurementSignals are used to send information to the GUI about updated current position and to what percentage the job is done.
    These infos should be displayed in the Log-Window of the chamber-tab in the GUI.
    Therefor the button to start the routine should be positioned in chamber-tab as well.
    """

    chamber: ChamberNetworkCommands = None
    signals: WorkerSignals = None
    center_position: list[float] = None     # [x,y,z] in mm where z is the height at which the tip of the pen touches the bed >> from init
    draw_height: float = None    # z-height at which the pen touches the bed
    safe_height: float = None    # z-height at which the pen is moved up to move to next position
    move_pen_up: float = 5.0  # distance to move the pen up after drawing a square >> hardcoded
    len_square_sides: list[float] = [10.0, 50.0, 100.0, 400.0]    # list of lengths of the sides of the squares to be drawn >> hardcoded
    square_reps: int = 5      # set how many times each square is to be drawn >> hardcoded
    move_speed: float = 100.0  # speed to move the pen in mm/min >> hardcoded

    def __init__(self, chamber: ChamberNetworkCommands, drawing_height: float):
        super().__init__()
        self.chamber = chamber
        self.signals = WorkerSignals()
        self.draw_height = drawing_height
        self.safe_height = drawing_height + self.move_pen_up
        self.center_position = [257.0, 225.5, self.safe_height]   # hardcoded center of all drawings & z-height for drawing


    def run(self):
        self.signals.update.emit("CalibrationRoutine initiated...")
        time.sleep(1)
        self.signals.update.emit("Center position: " + str(self.center_position))
        time.sleep(1)
        self.signals.update.emit("Starting calibration routine...")
        """ Move to center position """
        self.chamber.chamber_jog_abs(x=self.center_position[0], y=self.center_position[1], z=self.center_position[2], speed=self.move_speed)
        self.signals.position_update.emit({'abs_x': self.center_position[0], 'abs_y': self.center_position[1], 'abs_z': self.center_position[2]})
        """ Draw cross on center position """
        self.signals.update.emit("Marking center position...")
        self.chamber.chamber_jog_abs( x=self.center_position[0]-5.0, y=self.center_position[1], z=self.draw_height, speed=self.move_speed)
        self.signals.position_update.emit({'abs_x': self.center_position[0]-5.0, 'abs_y': self.center_position[1], 'abs_z': self.draw_height})
        self.chamber.chamber_jog_abs( x=self.center_position[0]+5.0, y=self.center_position[1], z=self.draw_height, speed=self.move_speed)
        self.signals.position_update.emit({'abs_x': self.center_position[0]+5.0, 'abs_y': self.center_position[1], 'abs_z': self.draw_height})
        self.return_to_center()
        self.chamber.chamber_jog_abs( x=self.center_position[0], y=self.center_position[1]-5.0, z=self.draw_height, speed=self.move_speed)
        self.signals.position_update.emit({'abs_x': self.center_position[0], 'abs_y': self.center_position[1]-5.0, 'abs_z': self.draw_height})
        self.chamber.chamber_jog_abs( x=self.center_position[0], y=self.center_position[1]+5.0, z=self.draw_height, speed=self.move_speed)
        self.signals.position_update.emit({'abs_x': self.center_position[0], 'abs_y': self.center_position[1]+5.0, 'abs_z': self.draw_height})
        self.return_to_center()
        """ Draw squares """
        for count, side in enumerate(self.len_square_sides):
            self.signals.update.emit("Drawing square " + str(count+1) + "/" + str(self.len_square_sides.__len__()) + "  with side length: " + str(side) + "mm")
            for i in range(self.square_reps):
                self.signals.update.emit("Drawing square " + str(i+1) + " of " + str(self.square_reps) + "...")
                self.draw_square(side)
        self.signals.update.emit("CalibrationRoutine finished.")
        self.signals.finished.emit()
        return

    def return_to_center(self):
        """ Moves to center position at safe_height"""
        self.chamber.chamber_jog_rel(z=self.move_pen_up, speed=self.move_speed)
        self.signals.position_update.emit({'rel_z': self.move_pen_up})
        self.chamber.chamber_jog_abs(x=self.center_position[0], y=self.center_position[1], z=self.center_position[2], speed=self.move_speed)
        self.signals.position_update.emit({'abs_x': self.center_position[0], 'abs_y': self.center_position[1], 'abs_z': self.center_position[2]})

    def draw_square(self, side_len: float):
        """ Draws a square with given side length centered at stored center position """
        half_side = side_len / 2
        self.return_to_center()
        # move to corner
        self.chamber.chamber_jog_abs(x=self.center_position[0]-half_side, y=self.center_position[1]-half_side, z=self.safe_height, speed=self.move_speed)
        self.signals.position_update.emit({'abs_x': self.center_position[0]-half_side, 'abs_y': self.center_position[1]-half_side, 'abs_z': self.safe_height})
        # lower pen
        self.chamber.chamber_jog_abs(x=self.center_position[0]-half_side, y=self.center_position[1]-half_side, z=self.draw_height, speed=self.move_speed)
        self.signals.position_update.emit({'abs_x': self.center_position[0]-half_side, 'abs_y': self.center_position[1]-half_side, 'abs_z': self.draw_height})
        # draw first side
        self.chamber.chamber_jog_abs(x=self.center_position[0]+half_side, y=self.center_position[1]-half_side, z=self.draw_height, speed=self.move_speed)
        self.signals.position_update.emit({'abs_x': self.center_position[0]+half_side, 'abs_y': self.center_position[1]-half_side, 'abs_z': self.draw_height})
        # draw second side
        self.chamber.chamber_jog_abs(x=self.center_position[0]+half_side, y=self.center_position[1]+half_side, z=self.draw_height, speed=self.move_speed)
        self.signals.position_update.emit({'abs_x': self.center_position[0]+half_side, 'abs_y': self.center_position[1]+half_side, 'abs_z': self.draw_height})
        # draw third side
        self.chamber.chamber_jog_abs(x=self.center_position[0]-half_side, y=self.center_position[1]+half_side, z=self.draw_height, speed=self.move_speed)
        self.signals.position_update.emit({'abs_x': self.center_position[0]-half_side, 'abs_y': self.center_position[1]+half_side, 'abs_z': self.draw_height})
        # draw fourth side
        self.chamber.chamber_jog_abs(x=self.center_position[0]-half_side, y=self.center_position[1]-half_side, z=self.draw_height, speed=self.move_speed)
        self.signals.position_update.emit({'abs_x': self.center_position[0]-half_side, 'abs_y': self.center_position[1]-half_side, 'abs_z': self.draw_height})
        # move pen up at position
        self.chamber.chamber_jog_rel(z=self.move_pen_up, speed=self.move_speed)
        self.signals.position_update.emit({'rel_z': self.move_pen_up})
        # move to center position
        self.return_to_center()