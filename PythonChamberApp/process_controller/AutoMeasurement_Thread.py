from PyQt6.QtCore import * # QObject, pyqtSignal, pyqtSlot, QRunnable
from PythonChamberApp.chamber_net_interface.chamber_net_interface import ChamberNetworkCommands
# from PythonChamberApp.vna_net_interface
import time


class AutoMeasurementSignals(QObject):
    '''
    Defines the signals available from a running AutoMeasurementSignals thread.

    Supported signals are:

    finished
        >> ? - ´´To be implemented´´

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
    finished = pyqtSignal()
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
    # vna: VNANetworkCommands = None

    mesh_x_vector: tuple[float, ...] = None
    mesh_y_vector: tuple[float, ...] = None
    mesh_z_vector: tuple[float, ...] = None
    chamber_mov_speed = 0   # unit [mm/s], see jog command doc-string!

    # vna_meas_config: ? = ?

    def __init__(self, chamber: ChamberNetworkCommands, x_vec: tuple[float, ...], y_vec: tuple[float, ...], z_vec: tuple[float, ...], mov_speed: float):
        super(AutoMeasurement, self).__init__()

        self.chamber = chamber
        # self.vna = vna

        self.mesh_x_vector = x_vec
        self.mesh_y_vector = y_vec
        self.mesh_z_vector = z_vec
        self.chamber_mov_speed = mov_speed

        self.signals = AutoMeasurementSignals()


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

                    self.signals.update.emit('Request movement to X: ' + str(x_coor) + ' Y: ' + str(y_coor) + ' Z: ' + str(z_coor))
                    # self.chamber.chamber_jog_abs(x=x_coor, y=y_coor, z=z_coor, speed=self.chamber_mov_speed)
                    self.signals.update.emit("Movement done!")

                    # Routine to do vna measurement and store data somewhere put here...
                    self.signals.update.emit("Requesting measurement...")
                    time.sleep(0.5)
                    self.signals.update.emit("Measurement done! Data stored!")

                    progress_dict['total_current_point_number'] = total_point_count
                    progress_dict['current_layer_number'] = layer_count
                    progress_dict['current_point_number_in_layer'] = point_in_layer_count
                    self.signals.progress.emit(progress_dict)

            point_in_layer_count = 0

        self.signals.update.emit("AutoMeasurement is completed!")
        self.signals.result.emit()
        self.signals.finished.emit()
        return




