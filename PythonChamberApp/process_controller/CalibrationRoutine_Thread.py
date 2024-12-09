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
4. manually move the tip of the pen so that it touches the paper at the point around whch squares should be drawn
5. Go to the chamber-tab in the GUI and start the CalibrationRoutine by button-click
-> current position is taken as the z-coordinate for drawing and XY for center of drawing

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

    AutoMeasurementSignals are used to send information to the GUI about updated current position and to what step is currently in progress.
    These infos should be displayed in the Log-Window of the chamber-tab in the GUI.
    Therefor the button to start the routine should be positioned in chamber-tab as well.
    """

    """ Octoprint GCodes to use in Custom Assembly """
    g_code_start_prompt = 'M105'  # get temperature first, so that octoprint reacts to next commands
    g_code_use_abs_coords = 'G90'  # use absolute coordinates
    g_code_use_rel_coords = 'G91'  # use relative coordinates
    """ End of GCodes """

    chamber: ChamberNetworkCommands = None
    signals: WorkerSignals = None
    center_position: list[float] = None     # [x,y,z] in mm where z is the height at which the tip of the pen touches the bed >> from init
    draw_height: float = None    # z-height at which the pen touches the bed
    safe_height: float = None    # z-height at which the pen is moved up to move to next position
    move_pen_up: float = 5.0  # distance to move the pen up after drawing a square >> hardcoded
    len_square_sides: list[float] = [10.0, 50.0] #[10.0, 50.0, 100.0, 400.0]    # list of lengths of the sides of the squares to be drawn >> hardcoded
    square_reps: int = 1      # set how many times each square is to be drawn >> hardcoded
    move_speed: float = 100.0  # speed to move the pen in mm/min >> hardcoded

    def __init__(self, chamber: ChamberNetworkCommands, current_position: list[float]):
        super().__init__()
        self.chamber = chamber
        self.signals = WorkerSignals()
        self.draw_height = current_position[2]
        self.safe_height = current_position[2] + self.move_pen_up
        self.center_position = [current_position[0], current_position[1], self.safe_height]   # hardcoded center of all drawings & z-height for drawing


    def run(self):
        self.signals.update.emit("CalibrationRoutine initiated...")
        time.sleep(1)
        self.signals.update.emit("Center position: " + str(self.center_position))
        time.sleep(1)
        self.signals.update.emit("Starting calibration routine...")
        """ Move to center position """
        self.return_to_center()
        """ Draw cross at center position """
        self.signals.update.emit("Marking center position...")
        self.draw_cross(10.0)
        """ Draw squares """
        for count, side in enumerate(self.len_square_sides):
            self.signals.update.emit("Drawing square " + str(count+1) + "/" + str(self.len_square_sides.__len__()) + "  with side length: " + str(side) + "mm")
            for i in range(self.square_reps):
                self.signals.update.emit("Drawing square " + str(i+1) + " of " + str(self.square_reps) + "...")
                self.draw_square(side)

        self.signals.update.emit("CalibrationRoutine finished.")
        """ return to center, update position in app """
        self.return_to_center()
        self.signals.finished.emit()
        return

    def return_to_center(self):
        """ Moves to center position at safe_height"""
        self.chamber.chamber_jog_abs(x=self.center_position[0], y=self.center_position[1], z=self.center_position[2], speed=self.move_speed)
        self.signals.position_update.emit({'abs_x': self.center_position[0], 'abs_y': self.center_position[1], 'abs_z': self.center_position[2]})

    def draw_cross(self, side_len: float):
        """ Draws a cross with given side length centered at stored center position """
        half_side = side_len / 2
        gcode_list = [self.g_code_start_prompt]
        gcode_list.extend(self.gcode_return_to_center())
        # move to corner
        gcode_list.extend(self.gcode_mov_abs(x=self.center_position[0]-half_side, y=self.center_position[1], z=self.safe_height, speed=self.move_speed))
        # lower pen
        gcode_list.extend(self.gcode_mov_abs(x=self.center_position[0]-half_side, y=self.center_position[1], z=self.draw_height, speed=self.move_speed))
        # draw first side
        gcode_list.extend(self.gcode_mov_abs(x=self.center_position[0]+half_side, y=self.center_position[1], z=self.draw_height, speed=self.move_speed))
        # move pen up at position
        gcode_list.extend(self.gcode_mov_rel(z=self.move_pen_up, speed=self.move_speed))
        # move to center position
        gcode_list.extend(self.gcode_return_to_center())
        # move to start of second side
        gcode_list.extend(self.gcode_mov_abs(x=self.center_position[0], y=self.center_position[1]-half_side, z=self.safe_height, speed=self.move_speed))
        # lower pen
        gcode_list.extend(self.gcode_mov_abs(x=self.center_position[0], y=self.center_position[1]-half_side, z=self.draw_height, speed=self.move_speed))
        # draw second side
        gcode_list.extend(self.gcode_mov_abs(x=self.center_position[0], y=self.center_position[1]+half_side, z=self.draw_height, speed=self.move_speed))
        # move pen up at position
        gcode_list.extend(self.gcode_mov_rel(z=self.move_pen_up, speed=self.move_speed))
        # move to center position
        gcode_list.extend(self.gcode_return_to_center())

        self.chamber.chamber_send_custom_GCode_with_flag(gcode_list)
        return
    def draw_square(self, side_len: float):
        """ Draws a square with given side length centered at stored center position """
        half_side = side_len / 2
        gcode_list = [self.g_code_start_prompt]
        gcode_list.extend(self.gcode_return_to_center())
        # move to corner
        gcode_list.extend(self.gcode_mov_abs(x=self.center_position[0]-half_side, y=self.center_position[1]-half_side, z=self.safe_height, speed=self.move_speed))
        # lower pen
        gcode_list.extend(self.gcode_mov_abs(x=self.center_position[0]-half_side, y=self.center_position[1]-half_side, z=self.draw_height, speed=self.move_speed))
        # draw first side
        gcode_list.extend(self.gcode_mov_abs(x=self.center_position[0]+half_side, y=self.center_position[1]-half_side, z=self.draw_height, speed=self.move_speed))
        # draw second side
        gcode_list.extend(self.gcode_mov_abs(x=self.center_position[0]+half_side, y=self.center_position[1]+half_side, z=self.draw_height, speed=self.move_speed))
        # draw third side
        gcode_list.extend(self.gcode_mov_abs(x=self.center_position[0]-half_side, y=self.center_position[1]+half_side, z=self.draw_height, speed=self.move_speed))
        # draw fourth side
        gcode_list.extend(self.gcode_mov_abs(x=self.center_position[0]-half_side, y=self.center_position[1]-half_side, z=self.draw_height, speed=self.move_speed))
        # move pen up at position
        gcode_list.extend(self.gcode_mov_rel(z=self.move_pen_up, speed=self.move_speed))
        # move to center position
        gcode_list.extend(self.gcode_return_to_center())

        self.chamber.chamber_send_custom_GCode_with_flag(gcode_list)
        return

    def gcode_mov_rel(self, x: float = 0.0, y: float = 0.0, z: float = 0.0, speed: float = 100.0):
        """ returns gcode list of strings to move the probehead in relative coordinates """
        gcode_list = [self.g_code_use_rel_coords]   # set using relative coordinates
        x_code = ' X' + str(round(x, 2))
        y_code = ' Y' + str(round(y, 2))
        z_code = ' Z' + str(round(z, 2))
        speed_code = ' F' + str(round(speed, 2))
        cmd = 'G1' + x_code + y_code + z_code + speed_code
        gcode_list.append(cmd)
        gcode_list.append(self.g_code_use_abs_coords)   # reset to use absolute coordinates
        return gcode_list

    def gcode_mov_abs(self, x: float = 0.0, y: float = 0.0, z: float = 0.0, speed: float = 100.0):
        """ Moves the probehead in absolute coordinates """
        gcode_list = [self.g_code_use_abs_coords]   # assure use of right coords
        x_code = ' X' + str(round(x, 2))
        y_code = ' Y' + str(round(y, 2))
        z_code = ' Z' + str(round(z, 2))
        speed_code = ' F' + str(round(speed, 2))
        cmd = 'G1' + x_code + y_code + z_code + speed_code
        gcode_list.append(cmd)
        return gcode_list

    def gcode_return_to_center(self):
        """ returns gcode list to move to center position at safe_height"""
        gcode_list = [self.g_code_use_abs_coords]
        gcode_list.extend(self.gcode_mov_abs(x=self.center_position[0], y=self.center_position[1], z=self.safe_height, speed=self.move_speed))
        return gcode_list