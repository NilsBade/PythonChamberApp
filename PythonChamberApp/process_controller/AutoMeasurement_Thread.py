import random
import time

from PyQt6.QtCore import *  # QObject, pyqtSignal, pyqtSlot, QRunnable
from chamber_net_interface import ChamberNetworkCommands
from vna_net_interface import E8361RemoteGPIB
import cmath
import math
from datetime import datetime, timedelta
import json
import os


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
    position_update = pyqtSignal(dict)


class AutoMeasurement(QRunnable):
    """
    The AutoMeasurement class is a runnable routine that can be fed to the PyQt QThreadpool object.
    It gets handed the chamber object and the VNA object to reach them via network and GPIB adapter.
    The defined measurement-mesh configuration and VNA configuration are stored in the saved results
    (json-) file of the routine.

    The routine assumes that the VNA is already set up and the chamber is connected and ready to move!
    Making this sure is task of the method that starts the AutoMeasurement.

    It emits signals to enable monitoring and display in the GUI.
    Those are defined in 'AutoMeasurementSignals' class.

    It is interruptable at specific points by calling the AutoMeasurement.stop() method of the object.
    """

    # Properties
    chamber: ChamberNetworkCommands = None
    signals: AutoMeasurementSignals = None
    _is_running: bool = None
    vna: E8361RemoteGPIB = None
    vna_info_buffer: dict = None
    vna_meas_name: str = None

    mesh_x_vector: tuple[float, ...] = None
    mesh_y_vector: tuple[float, ...] = None
    mesh_z_vector: tuple[float, ...] = None
    chamber_mov_speed: float = 0  # unit [mm/s], see jog command doc-string!
    zero_position: tuple[float, ...] = [0, 0, 0]  # zero position must be known to write relative antenna coordinates to meas file

    store_as_json: bool = None
    measurement_file_json = None
    json_format_readable: bool = None
    json_data_storage: dict = None
    json_S11: dict = None
    json_S12: dict = None
    json_S22: dict = None

    average_time_per_point: float = 0  # unit [s], calculated from all points that were measured so far
    measurement_iteration_success: bool = False     # flag to indicate if measurement done and to redo measurement if error occured (in Try-block)
    error_log_path: str = None

    def __init__(self, chamber: ChamberNetworkCommands, vna: E8361RemoteGPIB, vna_info: dict, x_vec: tuple[float, ...],
                 y_vec: tuple[float, ...], z_vec: tuple[float, ...], mov_speed: float, zero_position: tuple[float, ...],
                 file_location: str, file_type_json: bool = True, file_type_json_readable: bool = True):
        super(AutoMeasurement, self).__init__()

        self.signals = AutoMeasurementSignals()
        self.chamber = chamber  # Comment here when testing without chamber
        self.vna = vna
        self.vna_info_buffer = vna_info     # to enable re-configuration of PNA in exception handling
        self.vna_meas_name = vna_info['meas_name']

        # Note: AutoMeasurement Thread assumes that the start-method already set up the PNA / VNA successfully and uses
        # vna_info just for docu in json file. If the PNA / VNA is not set up correctly, the thread will fail.

        self.mesh_x_vector = x_vec
        self.mesh_y_vector = y_vec
        self.mesh_z_vector = z_vec
        self.chamber_mov_speed = mov_speed
        self.zero_position = zero_position
        self.store_as_json = file_type_json
        self.json_format_readable = file_type_json_readable

        # redundant None initialization to be sure
        self.json_S11 = None
        self.json_S12 = None
        self.json_S22 = None

        # setup path to error log
        self.error_log_path = os.path.join(os.path.dirname(os.path.dirname(file_location)), "error_log.txt")
        with open(self.error_log_path, "a") as file:
            file.write(f"\n\n#### Started new AutoMeasurement - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ####\n")

        if self.store_as_json:
            # open ONE measurement file
            json_file_location = file_location + '.json'
            self.measurement_file_json = open(json_file_location, "w")

            # initialize json data storage for measurement
            self.json_data_storage = {}
            measurement_config = {
                'type':             'Auto Measurement Data JSON',
                'timestamp':        datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                'zero_position':    zero_position,
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
                'sweep_num_points': vna_info['sweep_num_points'],
                'if_bw':            vna_info['if_bw'], #[Hz]
                'output_power':     vna_info['output_power'], #[dBm]
                'average_number':   vna_info['avg_num'],
            }
            self.json_data_storage['measurement_config'] = measurement_config
            self.json_data_storage['data'] = []

            # setup dictionaries for separate parameter measurements and assign index in reduced list
            amp_idx = 4
            phase_idx = 5
            if 'S11' in vna_info['parameter']:
                self.json_S11 = {'parameter': 'S11', 'values': [], 'amp_idx': amp_idx, 'phase_idx': phase_idx}
                amp_idx += 2
                phase_idx += 2
            if 'S12' in vna_info['parameter']:
                self.json_S12 = {'parameter': 'S12', 'values': [], 'amp_idx': amp_idx, 'phase_idx': phase_idx}
                amp_idx += 2
                phase_idx += 2
            if 'S22' in vna_info['parameter']:
                self.json_S22 = {'parameter': 'S22', 'values': [], 'amp_idx': amp_idx, 'phase_idx': phase_idx}
        else:
            assert False, "AutoMeasurement_Thread: Only JSON file type is supported at the moment!"

    def run(self):
        self.signals.update.emit("Started the AutoMeasurementThread")

        # assemble string that names all generated files.
        file_locations_string = "\n< "
        if self.measurement_file_json is not None:
            file_locations_string += self.measurement_file_json.name
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
            'time_to_go': 'N/A',    # time to go in [seconds] as float
        }

        layer_count = 0
        point_in_layer_count = 0
        total_point_count = 0
        visa_timeout_error_counter = 0
        VISA_TIMEOUTS_BEFORE_RESET = 3

        for z_coor in self.mesh_z_vector:
            layer_count += 1
            # measure one layer
            for y_coor in self.mesh_y_vector:
                for x_coor in self.mesh_x_vector:
                    point_in_layer_count += 1
                    total_point_count += 1

                    # START TRY BLOCK & WHILE LOOP HERE
                    self.measurement_iteration_success = False
                    while not self.measurement_iteration_success:

                        # check for interruption
                        if self._is_running is False:
                            self.signals.error.emit(
                                {'error_code': 0, 'error_msg': "Thread was interrupted by process controller"})
                            self.signals.update.emit("Auto Measurement was interrupted")
                            progress_dict['status_flag'] = "Measurement stopped"
                            self.__append_to_error_log(
                                f"AutoMeasurement was stopped at [{x_coor}, {y_coor}, {z_coor}] by User (ProcessController).")
                            self.signals.progress.emit(progress_dict)
                            self.close_all_files(meas_start_timestamp)
                            self.signals.finished.emit({'file_location': file_locations_string,
                                                        'duration': str(timedelta(seconds=(round((datetime.now() - meas_start_timestamp).total_seconds()))))})
                            return
                        try:
                            self.signals.update.emit(
                                'Request movement to X: ' + str(x_coor) + ' Y: ' + str(y_coor) + ' Z: ' + str(z_coor))
                            self.chamber.chamber_jog_abs(x=x_coor, y=y_coor, z=z_coor, speed=self.chamber_mov_speed) # Comment here when testing without chamber
                            self.signals.position_update.emit({'abs_x': x_coor, 'abs_y': y_coor, 'abs_z': z_coor})
                            self.signals.update.emit("Movement done!")

                            # Routine to do vna measurement and store data somewhere put here...
                            self.signals.update.emit("Trigger measurement...")
                            self.vna.pna_trigger_measurement(self.vna_meas_name)
                            self.signals.update.emit("Measurement done! Read data from VNA and write to file...")

                            x_coor_antennas = x_coor - self.zero_position[0]
                            y_coor_antennas = y_coor - self.zero_position[1]
                            z_coor_antennas = z_coor - self.zero_position[2]

                            for json_dic in [self.json_S11, self.json_S12, self.json_S22]:
                                if json_dic is not None:
                                    # read data to buffer property
                                    self.signals.update.emit(f"JSON-routine reads {json_dic['parameter']}-Parameter Values...")
                                    data = self.vna.pna_read_meas_data(self.vna_meas_name, json_dic['parameter'])
                                    for freq_point in data:
                                        pointer = complex(real=freq_point[1], imag=freq_point[2])
                                        json_dic['values'].append([x_coor_antennas, y_coor_antennas, z_coor_antennas, freq_point[0], pointer.__abs__(), math.degrees(cmath.phase(pointer))])
                                    self.signals.update.emit(f"{json_dic['parameter']} data appended.")

                            # flag success of measurement
                            self.measurement_iteration_success = True

                        except Exception as e:
                            self.signals.update.emit(f"Error occurred at [{x_coor}, {y_coor}, {z_coor}]")
                            self.__append_to_error_log(f"Error occurred at [{x_coor}, {y_coor}, {z_coor}]: {e}")
                            self.signals.update.emit(f"Error Log updated. Restarting measurement at [{x_coor}, {y_coor}, {z_coor}]...")
                            time.sleep(1) # sleeptime to slow down for PNA

                            if "-1073807264" in str(e):  # 'VI_ERROR_NCIC (-1073807264): The interface associated with this session is not currently the controller in charge.'
                                print("AutoMeasurement thrown controller error -1073807264 - Resetting the PNA...")
                                vna_resource_name = self.vna.pna_device.resource_name
                                interface_str = vna_resource_name.split('::')[0]
                                self.vna.disconnect_pna()   #close GPIBx interface
                                interface = self.vna.resource_manager.open_resource(interface_str + '::INTFC')
                                interface.send_ifc()    #Set GPIBx as controller in charge
                                interface.close()       #close GPIBx again
                                self.vna.connect_pna(vna_resource_name)     #Reopen pna connection on GPIBx (now in charge!)
                                self.__reconfigure_pna()    # reset whole pna and reconfigure measurement as before



                            if "-1073807339" in str(e):  # 'VI_ERROR_TMO (-1073807339): Timeout expired before operation completed.'
                                print("AutoMeasurement thrown Visa Timeout error -1073807339")
                                visa_timeout_error_counter += 1
                                if visa_timeout_error_counter >= VISA_TIMEOUTS_BEFORE_RESET:
                                    print(f"Reset VNA because too many timeouts (>{VISA_TIMEOUTS_BEFORE_RESET})")
                                    self.__reconfigure_pna()

                    # END TRY BLOCK & WHILE LOOP HERE

                    # Timekeeping for average time per point
                    if total_point_count == 1:
                        meas_start_timestamp = datetime.now()
                        progress_dict['time_to_go'] = 0
                    else:
                        self.average_time_per_point = (datetime.now() - meas_start_timestamp).total_seconds() / (total_point_count - 1)
                        progress_dict['time_to_go'] = round(self.average_time_per_point * (total_num_of_points - total_point_count))


                    # give progression update
                    progress_dict['total_current_point_number'] = total_point_count
                    progress_dict['current_layer_number'] = layer_count
                    progress_dict['current_point_number_in_layer'] = point_in_layer_count
                    self.signals.progress.emit(progress_dict)

            point_in_layer_count = 0

        self.signals.update.emit("AutoMeasurement is completed!")
        progress_dict['status_flag'] = "Measurement finished"
        self.signals.progress.emit(progress_dict)
        self.signals.finished.emit({'file_location': file_locations_string,
                                    'duration': str(timedelta(seconds=(round((datetime.now() - meas_start_timestamp).total_seconds()))))})
        self.close_all_files(meas_start_timestamp)
        return

    def stop(self):
        """
        Method to interrupt the thread in the next possible moment (thread checks for interruption regularly)
        """
        self._is_running = False

    def close_all_files(self, meas_start_timestamp: datetime = None):
        """
        Detects all open files, writes data to them if necessary and closes all files.
        This function must be called before Thread finishes.
        """
        # update measurement duration in measurement_config
        if meas_start_timestamp is not None:
            time_taken_sec = (datetime.now() - meas_start_timestamp).total_seconds()
            self.json_data_storage['measurement_config']['duration'] = str(timedelta(seconds=time_taken_sec))

        # close json file - dicts must be assembled and data written to file before close()
        if self.measurement_file_json is not None:
            self.signals.update.emit("Reading data from dicts and print to json file...")
            # Assembly large data-list with syntax:
            #   [ [x, y, z, f, S11-amp, S11-ph, S12-amp, S12-ph, S22-amp, S22-ph], ... ]
            #   Dependent on the parameters that are supposed to be measured, each point-list in the overall list
            #   has length of 6 (one S-param), 8 (two S-param) or 10 (three S-param). The order in which they are
            #   stored, if present, is S11 > S12 > S22. Their indexing shifts so that point-lists are as short as
            #   possible. Indexes are stored in property buffer-dicts as 'amp_idx' and 'phase_idx'.
            # 1. generate point_list_entry-buffer with right length to store all parameter measurements
            num_of_parameters = self.json_data_storage['measurement_config']['parameter'].__len__()
            point_list_entry_buffer = [0.0, 0.0, 0.0, 0.0]
            for i in range(num_of_parameters):
                point_list_entry_buffer.append(0.0)  # amplitude
                point_list_entry_buffer.append(0.0)  # phase
            # 2. find total length of list, each list should be same length //
            # assign base-buffer to read from coor & freq
            num_points_measured = 0
            base_buffer = None
            for par_dict in [self.json_S11, self.json_S12, self.json_S22]:
                if par_dict is not None:
                    num_points_measured = par_dict['values'].__len__()
                    base_buffer = par_dict      # base_buffer always overridden since same XYZ and Freq for all S-params
            # 3. run through base-buffer list to get all coordinates and frequencies and append the measured
            # amplitudes and phases to the data-list as ONE list-entry for all measured S-parameters in one point
            # at one frequency.
            for idx in range(num_points_measured):
                point_list_entry_buffer[0] = base_buffer['values'][idx][0]  # X-coor
                point_list_entry_buffer[1] = base_buffer['values'][idx][1]  # Y-coor
                point_list_entry_buffer[2] = base_buffer['values'][idx][2]  # Z-coor
                point_list_entry_buffer[3] = base_buffer['values'][idx][3]  # Frequency
                for par_dict in [self.json_S11, self.json_S12, self.json_S22]:
                    if par_dict is not None:
                        point_list_entry_buffer[par_dict['amp_idx']] = par_dict['values'][idx][4]
                        point_list_entry_buffer[par_dict['phase_idx']] = par_dict['values'][idx][5]
                self.json_data_storage['data'].append(point_list_entry_buffer.copy())  # Must use copy(), otherwise only reference handed to list!

            # decide if formatting readable
            indent = None
            if self.json_format_readable:
                indent = 4

            self.measurement_file_json.write(json.dumps(self.json_data_storage, indent=indent))
            self.signals.update.emit(f"Data written to {self.measurement_file_json.name}")
            self.measurement_file_json.close()

        return

    def __append_to_error_log(self, error_msg: str):
        """
        Appends an error message to the error log file with timestamp.
        """
        with open(self.error_log_path, 'a') as file:
            file.write(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - {error_msg}\n")
        return

    def __reconfigure_pna(self):
        """
        Presets PNA and reconfigures measurement as throughout init-routine.
        """
        self.vna.pna_preset()
        # reconfigure PNA by file setup
        if 'vna_preset_from_file' in self.vna_info_buffer:
            self.vna.pna_preset_from_file(self.vna_info_buffer['vna_preset_from_file'], self.vna_meas_name)
        else:   # reconfigure PNA by manual setup
            self.vna.pna_add_measurement_detailed(meas_name=self.vna_meas_name,
                                                  parameter=self.vna_info_buffer['parameter'],
                                                  freq_start=self.vna_info_buffer['freq_start'],
                                                  freq_stop=self.vna_info_buffer['freq_stop'],
                                                  if_bw=self.vna_info_buffer['if_bw'],
                                                  sweep_num_points=self.vna_info_buffer['sweep_num_points'],
                                                  output_power=self.vna_info_buffer['output_power'],
                                                  trigger_manual=True,
                                                  average_number=self.vna_info_buffer['avg_num'])
