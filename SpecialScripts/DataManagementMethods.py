"""
This script defines methods for fast and flexible reading and display of measurement data without GUI.
Specialized Scripts are supposed to use methods defined here.
"""
import os
import json
import numpy as np
from datetime import datetime


def read_measurement_data_from_file(filepath: str) -> dict:
    """
    Reads measurement data from a PythonChamberApp-Measurement-File and returns it as dictionary.
    The measurement config (header) is defined as dict behind the key 'measurement_config'.
    The keys 'f_vec', 'x_vec', 'y_vec', 'z_vec' hold a 1D numpy.ndarray that stores all coordinates and frequencies
    that were probed.

    The measurement data is defined as 6D numpy.ndarray behind the key 'data_array'.
    The 6D array follows the structure:

    [Amp_Phase, S-Parameter, Frequency, X-coor, Y-coor, Z-coor]

    'Amp_Phase': 0 for amplitude, 1 for phase

    'S-Parameter': [0,3] dependent on which and how many S-Parameters were measured (look into 'measurement_config':'parameter': list)

    'Frequency': Frequency point's index in 'f_vec'

    'X-coor': X-coordinate's index in 'x_vec'

    'Y-coor': Y-coordinate's index in 'y_vec'

    'Z-coor': Z-coordinate's index in 'z_vec'

    :param filepath: Path to measurement file
    :return: dict{'measurement_config': dict, 'measurement_data': numpy.ndarray}
    """

    read_in_measurement_data_buffer = None
    # file_name = filepath
    # # check for valid file type
    # if '.json' not in file_name:
    #     print('Error: File is not of type .json')
    #     return None

    with open(filepath, 'r') as json_file:
        read_in_measurement_data_buffer = json.load(json_file)

    # add additional vector data to dict for coherent dataflow from processcontroller to sub-methods/windows
    read_in_measurement_data_buffer['f_vec'] = np.linspace(
        start=read_in_measurement_data_buffer['measurement_config']['freq_start'],
        stop=read_in_measurement_data_buffer['measurement_config']['freq_stop'],
        num=read_in_measurement_data_buffer['measurement_config']['sweep_num_points'])
    read_in_measurement_data_buffer['x_vec'] = np.linspace(
        start=read_in_measurement_data_buffer['measurement_config']['mesh_x_min'],
        stop=read_in_measurement_data_buffer['measurement_config']['mesh_x_max'],
        num=read_in_measurement_data_buffer['measurement_config']['mesh_x_steps'])
    read_in_measurement_data_buffer['y_vec'] = np.linspace(
        start=read_in_measurement_data_buffer['measurement_config']['mesh_y_min'],
        stop=read_in_measurement_data_buffer['measurement_config']['mesh_y_max'],
        num=read_in_measurement_data_buffer['measurement_config']['mesh_y_steps'])
    read_in_measurement_data_buffer['z_vec'] = np.linspace(
        start=read_in_measurement_data_buffer['measurement_config']['mesh_z_min'],
        stop=read_in_measurement_data_buffer['measurement_config']['mesh_z_max'],
        num=read_in_measurement_data_buffer['measurement_config']['mesh_z_steps'])

    # generate numpy array in data-buffer for faster computation
    #   >> array indexing: [ Value: (1 - amplitude, 2 - phase), Parameter: (1,2,3) , frequency: (num of freq points), x_coor: (num of x steps), y_coor: (num of y steps), z_coor: (num of z steps) ]
    #   e.g. Select phase of S11, @20GHz, X:10, Y:20, Z:30 leads to
    #       >> data_array[1, p, f, x, y, z] with p = find_idx('S11' in measurement_config['parameter']), f = find_idx(20e9 in freq_vector) , ...
    data_array = np.zeros([2, read_in_measurement_data_buffer['measurement_config']['parameter'].__len__(),
                            read_in_measurement_data_buffer['measurement_config']['sweep_num_points'],
                            read_in_measurement_data_buffer['measurement_config']['mesh_x_steps'],
                            read_in_measurement_data_buffer['measurement_config']['mesh_y_steps'],
                            read_in_measurement_data_buffer['measurement_config']['mesh_z_steps']])
    # fill amplitude values
    parameter_idx = 0
    amplitude_idx = 4   # default for first parameter
    phase_idx = 5       # default for first parameter
    s11_idx = None
    s12_idx = None
    s22_idx = None
    # find which parameters were measured and how long list entries are - initialize indexing
    if 'S11' in read_in_measurement_data_buffer['measurement_config']['parameter']:
        s11_idx = [amplitude_idx, phase_idx]
        amplitude_idx += 2
        phase_idx += 2
    if 'S12' in read_in_measurement_data_buffer['measurement_config']['parameter']:
        s12_idx = [amplitude_idx, phase_idx]
        amplitude_idx += 2
        phase_idx += 2
    if 'S22' in read_in_measurement_data_buffer['measurement_config']['parameter']:
        s22_idx = [amplitude_idx, phase_idx]

    value_list = read_in_measurement_data_buffer['data']
    list_idx = 0
    # value_list setup like [ [x0, y0, z0, f0, s11amp0, s11phase0, s12amp0, s12phase0, s22amp0, s22phase0], ...] runs through 1. frequency, 2. x-coor, 3. y-coor, 4. z-coor
    for z_idx in range(read_in_measurement_data_buffer['z_vec'].__len__()):
        for y_idx in range(read_in_measurement_data_buffer['y_vec'].__len__()):
            for x_idx in range(read_in_measurement_data_buffer['x_vec'].__len__()):
                for f_idx in range(read_in_measurement_data_buffer['f_vec'].__len__()):
                    # For each list entry write all S parameter values to array in one go (this inner loop)
                    parameter_idx = 0
                    if s11_idx is not None:
                        data_array[0, parameter_idx, f_idx, x_idx, y_idx, z_idx] = value_list[list_idx][s11_idx[0]]     # amplitude
                        data_array[1, parameter_idx, f_idx, x_idx, y_idx, z_idx] = value_list[list_idx][s11_idx[1]]     # phase
                        parameter_idx += 1
                    if s12_idx is not None:
                        data_array[0, parameter_idx, f_idx, x_idx, y_idx, z_idx] = value_list[list_idx][s12_idx[0]]
                        data_array[1, parameter_idx, f_idx, x_idx, y_idx, z_idx] = value_list[list_idx][s12_idx[1]]
                        parameter_idx += 1
                    if s22_idx is not None:
                        data_array[0, parameter_idx, f_idx, x_idx, y_idx, z_idx] = value_list[list_idx][s22_idx[0]]
                        data_array[1, parameter_idx, f_idx, x_idx, y_idx, z_idx] = value_list[list_idx][s22_idx[1]]
                    list_idx += 1



    read_in_measurement_data_buffer['data_array'] = data_array
    return read_in_measurement_data_buffer

def write_meas_dict_to_file(filepath: str, data_dict: dict):
    """
    Writes a measurement data dictionary to a file.
    :param filepath: Path to file
    :param data_dict: Measurement data dictionary that should be stored with compensated phase-data and calibration data
    :return: None
    """
    # setup new dict to write to file - initialize json data storage for measurement
    json_data_storage = {}
    measurement_config = data_dict['measurement_config']
    measurement_config['date'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")   # update timestamp
    json_data_storage['measurement_config'] = measurement_config
    json_data_storage['data'] = []

    # 0. get index values for all S-parameters
    num_of_parameters = data_dict['measurement_config']['parameter'].__len__()
    json_S11 = None
    json_S12 = None
    json_S22 = None
    amp_idx = 4
    phase_idx = 5
    if 'S11' in data_dict['measurement_config']['parameter']:
        json_S11 = {'parameter': 'S11', 'values': [], 'amp_idx': amp_idx, 'phase_idx': phase_idx}
        amp_idx += 2
        phase_idx += 2
    if 'S12' in data_dict['measurement_config']['parameter']:
        json_S12 = {'parameter': 'S12', 'values': [], 'amp_idx': amp_idx, 'phase_idx': phase_idx}
        amp_idx += 2
        phase_idx += 2
    if 'S22' in data_dict['measurement_config']['parameter']:
        json_S22 = {'parameter': 'S22', 'values': [], 'amp_idx': amp_idx, 'phase_idx': phase_idx}

    # 1. generate point_list_entry-buffer with right length to store all parameter measurements
    point_list_entry_buffer = [0.0, 0.0, 0.0, 0.0]
    for i in range(num_of_parameters):
        point_list_entry_buffer.append(0.0)  # amplitude
        point_list_entry_buffer.append(0.0)  # phase
    # 2. find total length of list, each list should be same length //
    # assign base-buffer to read from coor & freq
    num_points_measured = (data_dict['measurement_config']['sweep_num_points']*
                           data_dict['measurement_config']['mesh_x_steps']*
                           data_dict['measurement_config']['mesh_y_steps']*
                           data_dict['measurement_config']['mesh_z_steps'])
    base_buffer = None

    for z_idx in range(data_dict['mesh_z_steps']):
        z_split = data_dict['data_array'][:, :, :, :, :, z_idx]
        for y_idx in range(data_dict['mesh_y_steps']):
            y_split = z_split[:, :, :, :, y_idx]
            for x_idx in range(data_dict['mesh_x_steps']):
                x_split = y_split[:, :, :, x_idx]
                for f_idx in range(data_dict['sweep_num_points']):
                    f_split = x_split[:, :, f_idx]
                    json_data_storage['data'].append([data_dict['x_vec'][x_idx], data_dict['y_vec'][y_idx], data_dict['z_vec'][z_idx], data_dict['f_vec'][f_idx],f_split[0,0],f_split[1,0]])     #todo enable that a variable number of s-parameters is supported. so far only S11 is stored to datalist
    # 3. run through base-buffer list to get all coordinates and frequencies and append the measured
    # amplitudes and phases to the data-list as ONE list-entry for all measured S-parameters in one point
    # at one frequency.
    # for idx in range(num_points_measured):
    #     point_list_entry_buffer[0] = base_buffer['values'][idx][0]  # X-coor
    #     point_list_entry_buffer[1] = base_buffer['values'][idx][1]  # Y-coor
    #     point_list_entry_buffer[2] = base_buffer['values'][idx][2]  # Z-coor
    #     point_list_entry_buffer[3] = base_buffer['values'][idx][3]  # Frequency
    #     for par_dict in [self.json_S11, self.json_S12, self.json_S22]:
    #         if par_dict is not None:
    #             point_list_entry_buffer[par_dict['amp_idx']] = par_dict['values'][idx][4]
    #             point_list_entry_buffer[par_dict['phase_idx']] = par_dict['values'][idx][5]
    #     self.json_data_storage['data'].append(
    #         point_list_entry_buffer.copy())  # Must use copy(), otherwise only reference handed to list!




    with open(filepath, 'w') as file:
        file.write(json.dumps(data_dict, indent=4))
    return None