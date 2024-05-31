import random

from PyQt6.QtCore import * # QObject, pyqtSignal, pyqtSlot, QRunnable
from PythonChamberApp.chamber_net_interface.chamber_net_interface import ChamberNetworkCommands
# from PythonChamberApp.vna_net_interface
import time
from datetime import datetime


class AutoMeasurementSignals(QObject):
    '''
    Defines the signals available from a running AutoMeasurementSignals thread.

    Supported signals are:

    finished
        >> dict {'file_location': str}

    error
        >> dict {'error_code': int, 'error_msg': str}

    result
        >> ? - ´´To be implemented´´

    progress
        >> dict {'total_points_in_measurement': int,
                 'total_current_point_number': int,
                 'num_of_layers_in_measurement': int,
                 'current_layer_number': int,
                 'num_of_points_in_current_layer': int,
                 'current_point_number_in_layer': int,
                 'status_flag': string}

    update
        >> string with update message -> can be used for console output or similar

    '''
    finished = pyqtSignal(dict)
    error = pyqtSignal(dict)
    result = pyqtSignal()
    progress = pyqtSignal(dict)
    update = pyqtSignal(str)


class AutoMeasurement(QRunnable):
    """
    The AutoMeasurement class is a runnable routine that can be fed to the PyQt QThreadpool object.
    It gets handed the chamber object and the VNA object to reach them via network and the
    desired measurement-mesh configuration and VNA configuration.

     It emits signals to enable monitoring and display in the GUI.
     Those are defined in 'AutoMeasurementSignals' class.
    """

    # Properties
    chamber: ChamberNetworkCommands = None
    _is_running: bool = None
    # vna: VNANetworkCommands = None

    mesh_x_vector: tuple[float, ...] = None
    mesh_y_vector: tuple[float, ...] = None
    mesh_z_vector: tuple[float, ...] = None
    chamber_mov_speed = 0   # unit [mm/s], see jog command doc-string!

    # vna_meas_config: ? = ?

    def __init__(self, chamber: ChamberNetworkCommands, x_vec: tuple[float, ...], y_vec: tuple[float, ...], z_vec: tuple[float, ...], mov_speed: float, file_location: str):
        super(AutoMeasurement, self).__init__()

        self.chamber = chamber
        # self.vna = vna

        self.mesh_x_vector = x_vec
        self.mesh_y_vector = y_vec
        self.mesh_z_vector = z_vec
        self.chamber_mov_speed = mov_speed

        self.signals = AutoMeasurementSignals()

        self.measurement_file = open(file_location, "w")
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.measurement_file.write("Auto Measurement Data File\n")
        self.measurement_file.write(f"Timestamp: {timestamp}\n")
        self.measurement_file.write("Mesh configuration:\n"
                                    f"x direction - min:{x_vec[0]}[mm]; max:{x_vec[-1]}[mm]; steps:{len(x_vec)}\n"
                                    f"y direction - min:{y_vec[0]}[mm]; max:{y_vec[-1]}[mm]; steps:{len(y_vec)}\n"
                                    f"x direction - min:{z_vec[0]}[mm]; max:{z_vec[-1]}[mm]; steps:{len(z_vec)}\n")
        self.measurement_file.write(f"Movementspeed: {mov_speed} [mm/s]\n")
        self.measurement_file.write("#####\n")
        self.measurement_file.write("X[mm]\tY[mm]\tZ[mm]\tamplitude[?]\tphase[deg]\n")
        self.measurement_file.write("#####\n")


    def run(self):
        self.signals.update.emit("Started the AutoMeasurementThread")

        num_of_points_per_layer = len(self.mesh_x_vector)*len(self.mesh_y_vector)
        num_of_layers = len(self.mesh_z_vector)
        total_num_of_points = num_of_points_per_layer * num_of_layers

        progress_dict = {
            'total_points_in_measurement': total_num_of_points,
            'num_of_layers_in_measurement': num_of_layers,
            'num_of_points_in_current_layer': num_of_points_per_layer,
            'status_flag': "Measurement running ...",
        }

        layer_count = 0
        point_in_layer_count = 0
        total_point_count = 0
        for z_coor in self.mesh_z_vector:
            layer_count += 1
            # measure one layer
            for y_coor in self.mesh_y_vector:
                for x_coor in self.mesh_x_vector:
                    point_in_layer_count += 1
                    total_point_count += 1

                    # check for interruption
                    if self._is_running is False:
                        self.signals.error.emit({'error_code': 0, 'error_msg': "Thread was interrupted by process controller"})
                        self.signals.update.emit("Auto Measurement was interrupted")
                        progress_dict['status_flag'] = "Measurement stopped"
                        self.signals.progress.emit(progress_dict)
                        self.measurement_file.close()
                        return

                    self.signals.update.emit('Request movement to X: ' + str(x_coor) + ' Y: ' + str(y_coor) + ' Z: ' + str(z_coor))
                    self.chamber.chamber_jog_abs(x=x_coor, y=y_coor, z=z_coor, speed=self.chamber_mov_speed)
                    self.signals.update.emit("Movement done!")

                    # Routine to do vna measurement and store data somewhere put here...
                    self.signals.update.emit("Requesting measurement...")
                    time.sleep(0.2)
                    amplitude = round(random.uniform(0,10), 1)  # ToDo implement VNA measurement and decide on units to be stored
                    phase = round(random.uniform(0,90), 2)

                    # write measured data to file
                    self.measurement_file.write(f"{x_coor};{y_coor};{z_coor};{amplitude};{phase}\n")
                    self.signals.update.emit("Measurement done! Data written to file!")

                    # give progression update
                    progress_dict['total_current_point_number'] = total_point_count
                    progress_dict['current_layer_number'] = layer_count
                    progress_dict['current_point_number_in_layer'] = point_in_layer_count
                    self.signals.progress.emit(progress_dict)

            point_in_layer_count = 0

        self.signals.update.emit("AutoMeasurement is completed!")
        progress_dict['status_flag'] = "Measurement finished"
        self.signals.progress.emit(progress_dict)
        self.measurement_file.close()
        self.signals.result.emit()
        self.signals.finished.emit({'file_location': self.measurement_file.name})
        return

    def stop(self):
        """
        Method to interrupt the thread in the next possible moment (thread checks for interruption regularly)
        """
        self._is_running = False




