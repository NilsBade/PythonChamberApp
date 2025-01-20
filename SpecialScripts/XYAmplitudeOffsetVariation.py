"""
This Script is supposed to plot the amplitude offset variation of a measurement data set.
"""

import os
import numpy as np
import json
from DataManagementMethods import read_measurement_data_from_file
import matplotlib.pyplot as plt
from tkinter import filedialog

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
__filename = filedialog.askopenfilename(initialdir=results_dir, title="Select a measurement file", filetypes=(("JSON files", "*.json"), ("All files", "*.*")))
file_path = os.path.join(results_dir, __filename)
##############################################################################################
meas_data_dict = read_measurement_data_from_file(file_path)
"""
Reminder 'data_array' structure: [Amp_Phase, S-Parameter, Frequency, X-coor, Y-coor, Z-coor]
Z-Coor gives the revisions of XY-plane probing.
"""

# Offset-Variation calculation at each XY-point
x_val = range(meas_data_dict['x_vec'].__len__()*meas_data_dict['y_vec'].__len__())
y_val = []
num_freq_points = meas_data_dict['f_vec'].__len__()

for f in range(num_freq_points):
    y_val.append([])
    for y in range(meas_data_dict['y_vec'].__len__()):
        for x in range(meas_data_dict['x_vec'].__len__()):
            # min/max val of phase offset at each XY-point
            phase_offset_min = meas_data_dict['data_array'][0, 0, f, x, y, :].min()
            phase_offset_max = meas_data_dict['data_array'][0, 0, f, x, y, :].max()

            freq_offset_variation = phase_offset_max - phase_offset_min
            y_val[f].append(freq_offset_variation)
            print("Amplitude offset variation (linear): ", freq_offset_variation)


# # Window Config
# main_fig, main_axes = plt.subplots(nrows=1, ncols=num_freq_points)
# manager_main_fig = plt.get_current_fig_manager()
# manager_main_fig.set_window_title('Maximum Amplitude Offset Difference (linear) in XY-Plane')
# main_fig.text(0.5, 0.975, str('Amplitude Offset Variation in XY-Plane // Data drawn from ' + __filename), ha='center', fontsize=12)
# info_string = "Maximum/Minimum measured amplitude difference [?] at "
# for i in range(num_freq_points):
#     x = x_val
#     y = y_val[i]
#     xmax = x[np.argmax(y)]
#     ymax = max(y)
#     xmin = x[np.argmin(y)]
#     ymin = min(y)
#     info_string = info_string + '@' + str(round(meas_data_dict['f_vec'][i]*1e-9,1)) + 'GHz: ' + str(round(ymax,5)) + '/' + str(round(ymin,5)) + ' '
#
#     main_axes[i].plot(x, y, marker='o', linestyle='', color='b')
#     main_axes[i].grid(True)
#     main_axes[i].set_ylabel('Amplitude difference []')
#     main_axes[i].set_xlabel('XY-point number')
#     main_axes[i].set_title('Frequency: ' + str(round(meas_data_dict['f_vec'][i]*1e-9,1)) + 'GHz')
#
# main_fig.text(0.5, 0.04, info_string, ha='center', fontsize=12, bbox=dict(facecolor='yellow', alpha=0.5))
# plt.tight_layout()
#
#
#
# Plot phase offset as line over repetitions for each point in XY plane
amplitude_offsets = np.zeros([num_freq_points, meas_data_dict['x_vec'].__len__()*meas_data_dict['y_vec'].__len__(), meas_data_dict['z_vec'].__len__()])
for f in range(num_freq_points):
    plane_counter = 0
    for y in range(meas_data_dict['y_vec'].__len__()):
        for x in range(meas_data_dict['x_vec'].__len__()):
            # min/max val of phase offset at each XY-point
            amplitude_offsets[f, plane_counter, :] = meas_data_dict['data_array'][0, 0, f, x, y, :]
            plane_counter += 1

x_val = range(meas_data_dict['z_vec'].__len__())
for i in range(num_freq_points):
    new_fig, new_axes = plt.subplots(nrows=1, ncols=1)
    manager_second_fig = plt.get_current_fig_manager()
    manager_second_fig.set_window_title('Amplitude measured for each XY-Point ' + str(round(meas_data_dict['f_vec'][i]*1e-9,1)) + ' GHz')
    y_val = np.transpose(amplitude_offsets[i, :, :])
    new_axes.plot(x_val, y_val, marker='o', markersize=2, linestyle='-')
    new_axes.grid(True)
    new_axes.set_ylabel('Amplitude []')
    new_axes.set_xlabel('Number of Probe Revisions')
    new_axes.set_title('Frequency: ' + str(round(meas_data_dict['f_vec'][i] * 1e-9, 1)) + 'GHz')
    new_fig.text(0.5, 0.975, str('Amplitude measured at each point in XY-Plane // Data drawn from ' + __filename),
                  ha='center', fontsize=12)
    new_fig.text(0.5, 0.04, 'Each line corresponds to one point in XY-Plane. Each point was probed ' + str(meas_data_dict['z_vec'].__len__()) + ' times.', ha='center', fontsize=12)

# ### Plot calibration matrix in 3D plot if data available >> NOT POSSIBLE since calibration matrix only holds phase values
# if 'calibration_data' in meas_data_dict:
#     calib_matrix = np.array(meas_data_dict['calibration_data'])
#     fig = plt.figure()
#     ax = fig.add_subplot(111, projection='3d')
#     # x = np.arange(calib_matrix.shape[1])
#     x = np.array(meas_data_dict['x_vec'])
#     # y = np.arange(calib_matrix.shape[2])
#     y = np.array(meas_data_dict['y_vec'])
#     x, y = np.meshgrid(x, y)
#     f_string = ''
#     for f in range(calib_matrix.shape[0]):
#         z = calib_matrix[f, :, :]
#         ax.plot_surface(x, y, z, cmap='viridis', label='Phase Cal @ ' + str(round(meas_data_dict['f_vec'][f] * 1e-9, 1)) + 'GHz')
#         ax.set_xlabel('X-Coordinate')
#         ax.set_ylabel('Y-Coordinate')
#         ax.set_zlabel('Phase [°]')
#         f_string += str(round(meas_data_dict['f_vec'][f] * 1e-9, 1)) + 'GHz '
#     ax.set_title('Calibration Matrix for ' + f_string)
#     plt.legend()

plt.tight_layout()
plt.show()

print("Done")