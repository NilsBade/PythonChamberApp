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
__filename = 'PhaseMeasurementOnS11_0004.json'
file_path = os.path.join(results_dir, __filename)
##############################################################################################
meas_data_dict = read_measurement_data_from_file(file_path)
"""
Reminder 'data_array' structure: [Amp_Phase, S-Parameter, Frequency, X-coor, Y-coor, Z-coor]
Z-Coor gives the revisions of XY-plane probing.
"""

# set filename for compensated data ##########################################################
__store_filename = 'PhaseMeasurementOnS11_0004_compensated.json'
store_path = os.path.join(results_dir, __store_filename)
store_file = open(store_path, 'w')
##############################################################################################
# generate data arrays
phase_xy_data = meas_data_dict['data_array'][1, 0, :, :, :, :]
phase_origin = np.zeros(meas_data_dict['f_vec'].__len__())

for f in range(phase_origin.__len__()): # find all frequency origins for each frequency
    phase_origin_idx = phase_xy_data[f, :, :, :].argmin()
    phase_origin_idx_unrav = np.unravel_index(phase_origin_idx, phase_xy_data[f, :, :, :].shape)
    phase_origin[f] = phase_xy_data[f, phase_origin_idx_unrav[0], phase_origin_idx_unrav[1], phase_origin_idx_unrav[2]]
    print("Phase origin for frequency ", round(meas_data_dict['f_vec'][f]*1e-9,1), "GHz : ", phase_origin[f], "°")

# generate corrected phase data
phase_xy_data_corrected = phase_xy_data - phase_origin[:, np.newaxis, np.newaxis, np.newaxis]
meas_data_dict['data_array'][1, 0, :, :, :, :] = phase_xy_data_corrected
meas_data_dict['data_array'] = meas_data_dict['data_array'].tolist()
data_array_debug = meas_data_dict['data_array']
data_list_debug = meas_data_dict['data_array'].tolist()

store_file.write(json.dumps(meas_data_dict, indent=4))
store_file.close()