"""
This Script gives the first version of the calibration matrix generator.
Goal is to find a zero phase location (by max amplitude) store a "calibration_data" key-value into the dict structure
and write the dict back to a txt file.
** Store the modified data in an extra txt file so that the results can be displayed with the
XYPhaseOffsetVariation.py-script.
"""

import os
import numpy as np
import json
from DataManagementMethods import read_measurement_data_from_file
from DataManagementMethods import write_meas_dict_to_file
import matplotlib.pyplot as plt

# Path to current working directory
print("current working directory: ", os.getcwd())
current_dir = os.getcwd()
# Construct the path to the parent directory
parent_dir = os.path.abspath(os.path.join(current_dir, os.pardir))
results_dir = os.path.join(parent_dir, 'results')

# switch to resultsdirectory and list available files
print("results directory: ", results_dir)
print("contents: ", os.listdir(results_dir))

# set path to desired measurement file #######################################################
__filename = 'PhaseMeasurementOnS11_S22_0005.json'
file_path = os.path.join(results_dir, __filename)
##############################################################################################
meas_data_dict = read_measurement_data_from_file(file_path)
"""
Reminder 'data_array' structure: [Amp_Phase, S-Parameter, Frequency, X-coor, Y-coor, Z-coor]
Z-Coor gives the revisions of XY-plane probing.
"""

# set filename for compensated data ##########################################################
__store_filename = 'PhaseMeasurementOnS11_S22_0005_compensated.json'
store_path = os.path.join(results_dir, __store_filename)
meas_data_dict['measurement_config']['type'] += ' (compensated)'
##############################################################################################
# generate data arrays
phase_xy_data = meas_data_dict['data_array'][1, 0, :, :, :, :]  # "0" Selects S11 Parameter for calibration
phase_origin = np.zeros(meas_data_dict['f_vec'].__len__())
phase_xy_calib_matrix = np.zeros([meas_data_dict['f_vec'].__len__(), meas_data_dict['x_vec'].__len__(), meas_data_dict['y_vec'].__len__()])
phase_xy_data_calibrated = np.zeros([meas_data_dict['f_vec'].__len__(), meas_data_dict['x_vec'].__len__(), meas_data_dict['y_vec'].__len__(), meas_data_dict['z_vec'].__len__()])

for f in range(phase_origin.__len__()): # find all frequency origins for each frequency
    phase_origin_idx = phase_xy_data[f, :, :, :].argmin()
    phase_origin_idx_unrav = np.unravel_index(phase_origin_idx, phase_xy_data[f, :, :, :].shape)
    phase_origin[f] = phase_xy_data[f, phase_origin_idx_unrav[0], phase_origin_idx_unrav[1], phase_origin_idx_unrav[2]]
    print("Phase origin for frequency ", round(meas_data_dict['f_vec'][f]*1e-9,1), "GHz : ", phase_origin[f], "°")

# set "normalized" phase data (ref to origin-phase 0°)
phase_xy_data_referenced = phase_xy_data - phase_origin[:, np.newaxis, np.newaxis, np.newaxis]

for f in range(meas_data_dict['f_vec'].__len__()):
    for x in range(meas_data_dict['x_vec'].__len__()):
        for y in range(meas_data_dict['y_vec'].__len__()):
            phase_xy_calib_matrix[f, x, y] = np.mean(phase_xy_data_referenced[f, x, y, :])  # mean phase value at each XY-point
            # subtract mean-phase-value at each XY-point (through z-axis) to bring them around 0°
            phase_xy_data_calibrated[f, x, y, :] = phase_xy_data_referenced[f,x,y,:] - phase_xy_calib_matrix[f, x, y]

# stores a 3D list addressable to [f_idx][x_idx][y_idx]
meas_data_dict['calibration_data'] = phase_xy_calib_matrix.copy().tolist()

meas_data_dict['data_array'][1, 0, :, :, :, :] = phase_xy_data_calibrated.copy()
write_meas_dict_to_file(store_path, meas_data_dict)
