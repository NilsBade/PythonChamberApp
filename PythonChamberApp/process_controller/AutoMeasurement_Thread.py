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
        >> dict {'num_cur_measurement_total': int, 'num_cur_layer_z': int, 'num_cur_measurement_in_layer': int}

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

        for z_coor in self.mesh_z_vector:
            for y_coor in self.mesh_y_vector:
                for x_coor in self.mesh_x_vector:
                    self.signals.update.emit('Request movement to X: ' + str(x_coor) + ' Y: ' + str(y_coor) + ' Z: ' + str(z_coor))
                    # self.chamber.chamber_jog_abs(x=x_coor, y=y_coor, z=z_coor, speed=self.chamber_mov_speed)
                    self.signals.update.emit("Movement done!")

                    # Routine to do vna measurement and store data somewhere put here...
                    self.signals.update.emit("Requesting measurement...")
                    time.sleep(0.3)
                    self.signals.update.emit("Measurement done! Data stored!")

        self.signals.update.emit("AutoMeasurement is completed!")
        self.signals.result.emit()
        self.signals.finished.emit()
        return




