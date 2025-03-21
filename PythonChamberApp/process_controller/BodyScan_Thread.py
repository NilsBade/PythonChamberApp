import time
from PyQt6.QtCore import *  # QObject, pyqtSignal, pyqtSlot, QRunnable
from chamber_net_interface import ChamberNetworkCommands
from vna_net_interface import E8361RemoteGPIB
import cmath
import math
from datetime import datetime, timedelta
import json
import os
from .AutoMeasurement_Thread import AutoMeasurementSignals
import numpy as np


class BodyScan(QRunnable):
    """
    The BodyScan class defines a runnable routine that can be fed to the PyQt QThreadPool to run in a separate thread.
    It gets handed the chamber object and the VNA object to reach them via network and GPIB adapter.

    Specified for the usecase of scanning upper bodies fixed in the measurement chamber,
    the class works with .cst-config files on the VNA (PNA) only. Manual measurement configuration is not supported.
    The routine stores the results in a .json file at a specified filepath given via init().

    The routine assumes that the VNA is already set up and the chamber is connected and ready to move!
    Making this sure is task of the method that starts the BodyScan.

    It emits signals to enable monitoring and display in the GUI.
    Those are defined in 'AutoMeasurementSignals' class.

    It is interruptable at specific points by calling the BodyScan.stop() method of the object.

    The overall structure of this class is very similar to the AutoMeasurement_Thread!
    """

    # Properties
    # Properties
    chamber: ChamberNetworkCommands = None
    signals: AutoMeasurementSignals = None
    _is_running: bool = None
    vna: E8361RemoteGPIB = None
    vna_info_buffer: dict = None
    vna_meas_name: str = None

    move_pattern: str = None
    mesh_x_vector: np.ndarray = None
    mesh_y_vector: np.ndarray = None
    mesh_z_vector: np.ndarray = None
    chamber_mov_speed: float = 0  # unit [mm/s], see jog command doc-string!
    z_move_sleep_time: float = 0.0  # unit [s], sleep time after z-movement to let chamber/body settle
    origin: tuple[float, ...] = None
    z_move_below: float = 0.5  # unit [mm], offset to move below next XY-point before measurement to avoid z-direction lack ~0.2mm when chamber changes direction

    measurement_file_json = None
    json_data_storage: dict = None
    json_S11: dict = None
    json_S12: dict = None
    json_S22: dict = None

    average_time_per_point: float = 0  # unit [s], calculated from all points that were measured so far
    measurement_iteration_success: bool = False  # flag to indicate if measurement done and to redo measurement if error occured (in Try-block)
    error_log_path: str = None

    def __init__(self, chamber: ChamberNetworkCommands, vna: E8361RemoteGPIB, vna_info: dict, x_vec: tuple[float, ...],
                 y_vec: tuple[float, ...], z_vec: tuple[float, ...], mov_speed: float, origin: tuple[float, ...],
                 file_location: str, move_pattern: str, z_move_sleep_time: float = 0.0):
        super(BodyScan, self).__init__()

        self.signals = AutoMeasurementSignals()
        self.chamber = chamber  # Comment here when testing without chamber
        self.vna = vna
        self.vna_info_buffer = vna_info  # to enable re-configuration of PNA in exception handling
        self.vna_meas_name = vna_info['meas_name']
        # Note: Same as for AutoMeasurement Thread, BodyScan assumes that the start-method already set up the PNA / VNA
        # successfully and uses vna_info just for docu in json file.
        # If the PNA / VNA is not set up correctly, the thread will fail.

        self.move_pattern = move_pattern
        self.mesh_x_vector = np.array(x_vec, dtype=float)
        self.mesh_y_vector = np.array(y_vec, dtype=float)
        self.mesh_z_vector = np.array(z_vec, dtype=float)
        self.chamber_mov_speed = mov_speed
        self.z_move_sleep_time = z_move_sleep_time
        self.origin = origin

        # redundant None initialization to be sure
        self.json_S11 = None
        self.json_S12 = None
        self.json_S22 = None

        # setup path to error log
        self.error_log_path = os.path.join(os.path.dirname(os.path.dirname(file_location)), "error_log.txt")
        with open(self.error_log_path, "a") as file:
            file.write(f"\n\n#### Started new BodyScan - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ####\n")

        # open ONE measurement file
        json_file_location = file_location + '.json'
        self.measurement_file_json = open(json_file_location, "w")

        # initialize json data storage for measurement
        self.json_data_storage = {}
        measurement_config = {
            'type': 'Body Scan Data JSON',
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'zero_position': origin,    # redundant information, but for better readability with automeasurement methods
            'origin_position': origin,
            'move_pattern': move_pattern,
            'mesh_x_min': x_vec[0],  # [mm]
            'mesh_x_max': x_vec[-1],  # [mm]
            'mesh_x_steps': len(x_vec),
            'mesh_y_min': y_vec[0],  # [mm]
            'mesh_y_max': y_vec[-1],  # [mm]
            'mesh_y_steps': len(y_vec),
            'mesh_z_min': z_vec[0],  # [mm]
            'mesh_z_max': z_vec[-1],  # [mm]
            'mesh_z_steps': len(z_vec),
            'movespeed': mov_speed,  # [mm/s]
            'parameter': vna_info['parameter'],
            'freq_start': vna_info['freq_start'],  # [Hz]
            'freq_stop': vna_info['freq_stop'],  # [Hz]
            'sweep_num_points': vna_info['sweep_num_points'],
            'if_bw': vna_info['if_bw'],  # [Hz]
            'output_power': vna_info['output_power'],  # [dBm]
            'average_number': vna_info['avg_num'],
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

    def run(self):
        self.signals.update.emit("Started BodyScan Thread")

        # assemble string to display file location
        file_location_string = "\n< " + self.measurement_file_json.name + " >\n"

        # calculate num of points and layers for progress monitoring
        num_of_points_per_layer = len(self.mesh_x_vector) * len(self.mesh_y_vector)
        num_of_layers = len(self.mesh_z_vector)
        total_num_of_points = num_of_points_per_layer * num_of_layers

        # initialize progress dict and send first update
        progress_dict = {
            'total_points_in_measurement': total_num_of_points,
            'num_of_layers_in_measurement': num_of_layers,
            'num_of_points_in_current_layer': num_of_points_per_layer,
            'status_flag': "Measurement running ...",
            'time_to_go': 'N/A',  # time to go in [seconds] as float
        }

        layer_count = 0
        point_in_layer_count = 0
        total_point_count = 0
        visa_timeout_error_counter = 0
        VISA_TIMEOUTS_BEFORE_RESET = 3

        # START MEASUREMENT LOOP #todo: implement that movement pattern can be selected in app!
        if self.move_pattern == "snake":
            x_move_vec = np.flip(self.mesh_x_vector.copy())  # Copy the x_vec and flip it because first run flips as well
        else:
            x_move_vec = self.mesh_x_vector.copy()

        for y_coor in self.mesh_y_vector:
            if self.move_pattern == "snake":    # flip in case of snake movement
                x_move_vec = np.flip(x_move_vec)
            for x_coor in x_move_vec:
                layer_count = 0             # reset layer count at each new point
                point_in_layer_count += 1   # increment point in layer count for each new XY point addressed
                # Move below point, avoid chamber z-direction lack
                self.signals.update.emit(f"Move below next XY-point: ({x_coor}, {y_coor})")
                self.chamber.chamber_jog_abs(x=x_coor, y=y_coor, z=float(self.mesh_z_vector[0]) - self.z_move_below,
                                             speed=self.chamber_mov_speed)  # Comment here when testing without chamber
                for z_coor in self.mesh_z_vector:
                    layer_count += 1
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
                            self.signals.finished.emit({'file_location': file_location_string,
                                                        'duration': str(timedelta(seconds=(round((datetime.now() - meas_start_timestamp).total_seconds()))))})
                            return
                        try:
                            self.signals.update.emit(
                                'Request movement to X: ' + str(x_coor) + ' Y: ' + str(y_coor) + ' Z: ' + str(z_coor))
                            self.chamber.chamber_jog_abs(x=x_coor, y=y_coor, z=z_coor, speed=self.chamber_mov_speed) # Comment here when testing without chamber
                            self.signals.position_update.emit({'abs_x': x_coor, 'abs_y': y_coor, 'abs_z': z_coor})
                            self.signals.update.emit("Movement done!")

                            # sleep to let chamber/body settle #
                            time.sleep(self.z_move_sleep_time)

                            # Routine to do vna measurement and store data somewhere put here...
                            self.signals.update.emit("Trigger measurement...")
                            self.vna.pna_trigger_measurement(self.vna_meas_name)    # Comment here when testing without VNA
                            self.signals.update.emit("Measurement done! Read data from VNA and write to file...")

                            x_coor_antennas = x_coor - self.origin[0]
                            y_coor_antennas = y_coor - self.origin[1]
                            z_coor_antennas = z_coor - self.origin[2]

                            # read data from VNA
                            for json_dic in [self.json_S11, self.json_S12, self.json_S22]:
                                if json_dic is not None:
                                    # read data to buffer property
                                    self.signals.update.emit(
                                        f"JSON-routine reads {json_dic['parameter']}-Parameter Values...")
                                    data = self.vna.pna_read_meas_data(self.vna_meas_name, json_dic['parameter'])   # comment here when testing without VNA
                                    for freq_point in data:
                                        pointer = complex(real=freq_point[1], imag=freq_point[2])
                                        json_dic['values'].append(
                                            [x_coor_antennas, y_coor_antennas, z_coor_antennas, freq_point[0],
                                             pointer.__abs__(), math.degrees(cmath.phase(pointer))])
                                    self.signals.update.emit(f"{json_dic['parameter']} data appended.")

                            # flag success of measurement
                            self.measurement_iteration_success = True

                        except Exception as e:
                            self.signals.update.emit(f"Error occurred at [{x_coor}, {y_coor}, {z_coor}]")
                            self.__append_to_error_log(f"Error occurred at [{x_coor}, {y_coor}, {z_coor}]: {e}")
                            self.signals.update.emit(
                                f"Error Log updated. Restarting measurement at [{x_coor}, {y_coor}, {z_coor}]...")
                            time.sleep(1)  # sleeptime to slow down for PNA

                            if "-1073807264" in str(
                                    e):  # 'VI_ERROR_NCIC (-1073807264): The interface associated with this session is not currently the controller in charge.'
                                print("AutoMeasurement thrown controller error -1073807264 - Resetting the PNA...")
                                vna_resource_name = self.vna.pna_device.resource_name
                                interface_str = vna_resource_name.split('::')[0]
                                self.vna.disconnect_pna()  # close GPIBx interface
                                interface = self.vna.resource_manager.open_resource(interface_str + '::INTFC')
                                interface.send_ifc()  # Set GPIBx as controller in charge
                                interface.close()  # close GPIBx again
                                self.vna.connect_pna(
                                    vna_resource_name)  # Reopen pna connection on GPIBx (now in charge!)
                                self.__reconfigure_pna()  # reset whole pna and reconfigure measurement as before

                            if "-1073807339" in str(
                                    e):  # 'VI_ERROR_TMO (-1073807339): Timeout expired before operation completed.'
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
        # END MEASUREMENT LOOP

        self.signals.update.emit("AutoMeasurement is completed!")
        progress_dict['status_flag'] = "Measurement finished"
        self.signals.progress.emit(progress_dict)
        self.signals.finished.emit({'file_location': file_location_string,
                                    'duration': str(timedelta(
                                        seconds=(round((datetime.now() - meas_start_timestamp).total_seconds()))))})
        self.close_all_files(meas_start_timestamp)
        return

    def stop(self):
        """
        Method to interrupt the thread in the next possible moment (thread checks for interruption regularly)
        """
        self._is_running = False

    def close_all_files(self, meas_start_timestamp: datetime = None):
        """
        SAME AS AutoMeasurement_Thread.close_all_files(), only little simplification

        Detects all open files, writes data to them if necessary and closes all files.
        This function must be called before Thread finishes.
        """
        # update measurement duration in measurement_config
        if meas_start_timestamp is not None:
            time_taken_sec = (datetime.now() - meas_start_timestamp).total_seconds()
            self.json_data_storage['measurement_config']['duration'] = str(timedelta(seconds=time_taken_sec))

        # close json file - dicts must be assembled and data written to file before close()
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
                base_buffer = par_dict  # base_buffer always overridden since same XYZ and Freq for all S-params
        # 3. run through base-buffer list to get all coordinates and frequencies and append the measured
        # amplitudes and phases to the data-list as ONE list-entry for all measured S-parameters in one point
        # at one frequency.
        for idx in range(num_points_measured):
            point_list_entry_buffer[0] = float(base_buffer['values'][idx][0])  # X-coor, typecast to regular float for json library
            point_list_entry_buffer[1] = float(base_buffer['values'][idx][1])  # Y-coor, typecast to regular float for json library
            point_list_entry_buffer[2] = float(base_buffer['values'][idx][2])  # Z-coor, typecast to regular float for json library
            point_list_entry_buffer[3] = float(base_buffer['values'][idx][3])  # Frequency, typecast to regular float for json library
            for par_dict in [self.json_S11, self.json_S12, self.json_S22]:
                if par_dict is not None:
                    point_list_entry_buffer[par_dict['amp_idx']] = par_dict['values'][idx][4]
                    point_list_entry_buffer[par_dict['phase_idx']] = par_dict['values'][idx][5]
            self.json_data_storage['data'].append(
                point_list_entry_buffer.copy())  # Must use copy(), otherwise only reference handed to list!

        # Sort list to be independent of movement pattern // comply with read-method of processController
        self.json_data_storage['data'] = sorted(self.json_data_storage['data'],
                                                key=lambda sublist: (sublist[2],  # z
                                                                     sublist[1],  # y
                                                                     sublist[0],  # x
                                                                     sublist[3]))  # f

        # decide if formatting readable
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
        Reconfigures the PNA with the stored configuration in self.vna_info_buffer >> only .cst file configuration!
        """
        self.vna.pna_preset()
        self.vna.pna_preset_from_file(self.vna_info_buffer['preset_file'], self.vna_meas_name)
        return