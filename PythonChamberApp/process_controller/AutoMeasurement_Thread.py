import random

from PyQt6.QtCore import *  # QObject, pyqtSignal, pyqtSlot, QRunnable
from PythonChamberApp.chamber_net_interface.chamber_net_interface import ChamberNetworkCommands
from PythonChamberApp.vna_net_interface.vna_net_interface import E8361RemoteGPIB
import cmath
import math
from datetime import datetime
import json


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
    vna: E8361RemoteGPIB = None
    measurement_file_S11 = None
    measurement_file_S12 = None
    measurement_file_S22 = None

    mesh_x_vector: tuple[float, ...] = None
    mesh_y_vector: tuple[float, ...] = None
    mesh_z_vector: tuple[float, ...] = None
    chamber_mov_speed = 0  # unit [mm/s], see jog command doc-string!

    store_as_json: bool = True
    measurement_file_json = None
    json_data_storage: dict = None
    json_S11: dict = None
    json_S12: dict = None
    json_S22: dict = None

    def __init__(self, chamber: ChamberNetworkCommands, vna: E8361RemoteGPIB, vna_info: dict, x_vec: tuple[float, ...],
                 y_vec: tuple[float, ...], z_vec: tuple[float, ...], mov_speed: float, file_location: str):
        super(AutoMeasurement, self).__init__()

        self.signals = AutoMeasurementSignals()
        #self.chamber = chamber  # toDo reenable after test
        self.vna = vna
        self.vna.pna_preset()
        self.vna.pna_add_measurement_detailed(meas_name='AutoMeasurement', parameter=vna_info['parameter'],
                                              freq_start=vna_info['freq_start'], freq_stop=vna_info['freq_stop'],
                                              if_bw=vna_info['if_bw'], sweep_num_points=vna_info['sweep_num_points'],
                                              output_power=vna_info['output_power'], trigger_manual=True,
                                              average_number=vna_info['average_number'])

        self.mesh_x_vector = x_vec
        self.mesh_y_vector = y_vec
        self.mesh_z_vector = z_vec
        self.chamber_mov_speed = mov_speed

        # redundant None initialization to be sure
        self.measurement_file_S11 = None
        self.measurement_file_S12 = None
        self.measurement_file_S22 = None
        self.json_S11 = None
        self.json_S12 = None
        self.json_S22 = None

        if self.store_as_json:
            # open ONE measurement file
            json_file_location = file_location + '.json'
            self.measurement_file_json = open(json_file_location, "w")

            # initialize json data storage for measurement
            self.json_data_storage = {}
            measurement_config = {
                'type':             'Auto Measurement Data JSON',
                'timestamp':        datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                'mesh_x_min':       x_vec[0], #[mm]
                'mesh_x_max':       x_vec[-1], #[mm]
                'mesh_x_steps':     len(x_vec),
                'mesh_y_min':       y_vec[0], #[mm]
                'mesh_y_max':       y_vec[-1], #[mm]
                'mesh_y_steps':     len(y_vec),
                'mesh_z_min':       z_vec[0], #[mm]
                'mesh_z_max':       z_vec[-1], #[mm]
                'mesh_z_steps':     len(z_vec),
                'movespeed':        mov_speed, #[mm/s]
                'parameter':        vna_info['parameter'],
                'freq_start':       vna_info['freq_start'], #[Hz]
                'freq_stop':        vna_info['freq_stop'], #[Hz]
                'if_bw':            vna_info['if_bw'], #[Hz]
                'sweep_num_points': vna_info['sweep_num_points'],
                'output_power':     vna_info['output_power'], #[dBm]
                'average_number':   vna_info['average_number'],
            }
            self.json_data_storage['measurement_config'] = measurement_config

            # setup dictionaries for separate parameter measurements
            if 'S11' in vna_info['parameter']:
                self.json_S11 = {'parameter': 'S11', 'values': []}
            if 'S12' in vna_info['parameter']:
                self.json_S12 = {'parameter': 'S12', 'values': []}
            if 'S22' in vna_info['parameter']:
                self.json_S22 = {'parameter': 'S22', 'values': []}

        # open separate measurement file for each parameter configured
        if 'S11' in vna_info['parameter']:
            new_file_location = file_location + '_S11.txt'
            self.measurement_file_S11 = open(new_file_location, "w")
        if 'S12' in vna_info['parameter']:
            new_file_location = file_location + '_S12.txt'
            self.measurement_file_S12 = open(new_file_location, "w")
        if 'S22' in vna_info['parameter']:
            new_file_location = file_location + '_S22.txt'
            self.measurement_file_S22 = open(new_file_location, "w")

        # print header info to each measurement file
        for file in [self.measurement_file_S11, self.measurement_file_S12, self.measurement_file_S22]:
            if file is not None:
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                file.write("Auto Measurement Data File\n")
                file.write(f"Timestamp: {timestamp}\n")
                file.write("Mesh configuration:\n"
                           f"x direction - min:{x_vec[0]}[mm]; max:{x_vec[-1]}[mm]; steps:{len(x_vec)}\n"
                           f"y direction - min:{y_vec[0]}[mm]; max:{y_vec[-1]}[mm]; steps:{len(y_vec)}\n"
                           f"x direction - min:{z_vec[0]}[mm]; max:{z_vec[-1]}[mm]; steps:{len(z_vec)}\n")
                file.write(f"Movementspeed: {mov_speed} [mm/s]\n")
                file.write("#####\n")
                file.write("X[mm]\tY[mm]\tZ[mm]\tfrequency[Hz]\tamplitude[dB]\tphase[deg]\n")
                file.write("#####\n")

    def run(self):
        self.signals.update.emit("Started the AutoMeasurementThread")

        # assemble string that names all generated files.
        file_locations_string = "\n< "
        if self.measurement_file_S11 is not None:
            file_locations_string += self.measurement_file_S11.name + ';\n'
        if self.measurement_file_S12 is not None:
            file_locations_string += self.measurement_file_S12.name + ';\n'
        if self.measurement_file_S22 is not None:
            file_locations_string += self.measurement_file_S22.name + ';\n'
        if self.measurement_file_json is not None:
            file_locations_string += self.measurement_file_json.name + ';\n'
        file_locations_string += ">\n"

        # calculate num of points and layers for progress monitoring
        num_of_points_per_layer = len(self.mesh_x_vector) * len(self.mesh_y_vector)
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
                        self.signals.error.emit(
                            {'error_code': 0, 'error_msg': "Thread was interrupted by process controller"})
                        self.signals.update.emit("Auto Measurement was interrupted")
                        progress_dict['status_flag'] = "Measurement stopped"
                        self.signals.progress.emit(progress_dict)
                        self.close_all_files()
                        self.signals.finished.emit({'file_location': file_locations_string})
                        return

                    self.signals.update.emit(
                        'Request movement to X: ' + str(x_coor) + ' Y: ' + str(y_coor) + ' Z: ' + str(z_coor))
                    #self.chamber.chamber_jog_abs(x=x_coor, y=y_coor, z=z_coor, speed=self.chamber_mov_speed) # toDo reenable after test
                    self.signals.update.emit("Movement done!")

                    # Routine to do vna measurement and store data somewhere put here...
                    self.signals.update.emit("Trigger measurement...")
                    self.vna.pna_trigger_measurement('AutoMeasurement')
                    self.signals.update.emit("Measurement done! Read data from VNA and write to file...")

                    # Routine to read all configured parameters from VNA and write each result to each file.txt
                    possible_parameters = ['S11', 'S12', 'S22']
                    counter = 0
                    for file in [self.measurement_file_S11, self.measurement_file_S12, self.measurement_file_S22]:
                        if file is not None:  # not None for all parameters that were introduced by __init__ function
                            self.signals.update.emit(f"Reading {possible_parameters[counter]}-Parameter Values...")
                            data = self.vna.pna_read_meas_data('AutoMeasurement', possible_parameters[counter])
                            for freq_point in data:
                                pointer = complex(real=freq_point[1], imag=freq_point[2])
                                # write measured data to file
                                file.write(
                                    f"{x_coor};{y_coor};{z_coor};{freq_point[0]};{pointer.__abs__()};{math.degrees(cmath.phase(pointer))}\n")
                            self.signals.update.emit(f"Written {possible_parameters[counter]} values to file.")
                        counter += 1
                    if self.store_as_json:
                        for json_dic in [self.json_S11, self.json_S12, self.json_S22]:
                            if json_dic is not None:
                                self.signals.update.emit(f"JSON-routine reads {json_dic['parameter']}-Parameter Values...")
                                data = self.vna.pna_read_meas_data('AutoMeasurement', json_dic['parameter'])
                                for freq_point in data:
                                    pointer = complex(real=freq_point[1], imag=freq_point[2])
                                    json_dic['values'].append([x_coor, y_coor, z_coor, freq_point[0], pointer.__abs__(), math.degrees(cmath.phase(pointer))])
                                self.signals.update.emit(f"{json_dic['parameter']} data appended.")

                    self.signals.update.emit("All data written to file(s)!")

                    # give progression update
                    progress_dict['total_current_point_number'] = total_point_count
                    progress_dict['current_layer_number'] = layer_count
                    progress_dict['current_point_number_in_layer'] = point_in_layer_count
                    self.signals.progress.emit(progress_dict)

            point_in_layer_count = 0

        self.signals.update.emit("AutoMeasurement is completed!")
        progress_dict['status_flag'] = "Measurement finished"
        self.signals.progress.emit(progress_dict)
        self.signals.result.emit()
        self.signals.finished.emit({'file_location': file_locations_string})
        self.close_all_files()
        return

    def stop(self):
        """
        Method to interrupt the thread in the next possible moment (thread checks for interruption regularly)
        """
        self._is_running = False

    def close_all_files(self):
        """
        Detects all open files, writes data to them if necessary and closes all files.
        This function must be called before Thread finishes.
        """
        # close text files - data already written
        if self.measurement_file_S11 is not None:
            self.measurement_file_S11.close()
        if self.measurement_file_S12 is not None:
            self.measurement_file_S12.close()
        if self.measurement_file_S22 is not None:
            self.measurement_file_S22.close()

        # close json file - dicts must be assembled and data written to file before close()
        if self.measurement_file_json is not None:
            for par_dict in [self.json_S11, self.json_S12, self.json_S22]:
                if par_dict is not None:
                    self.json_data_storage[par_dict['parameter']] = par_dict['values']
        self.measurement_file_json.write(json.dumps(self.json_data_storage))
        self.measurement_file_json.close()

        return
