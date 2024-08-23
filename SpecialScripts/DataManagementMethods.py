"""
This script defines methods for fast and flexible reading and display of measurement data without GUI.
Specialized Scripts are supposed to use methods defined here.
"""
import os
import json
import numpy as np


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