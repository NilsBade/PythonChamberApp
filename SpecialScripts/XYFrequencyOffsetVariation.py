"""
This Script is supposed to plot the frequency offset variation of a measurement data set.
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

# set path to desired measurement file
__filename = 'PhaseMeasurementOnS11_0004.json'
file_path = os.path.join(results_dir, __filename)

meas_data_dict = read_measurement_data_from_file(file_path)
"""
Reminder 'data_array' structure: [Amp_Phase, S-Parameter, Frequency, X-coor, Y-coor, Z-coor]
Z-Coor gives the revisions of XY-plane probing.
"""

# Variation calculation at each XY-point
x_val = range(meas_data_dict['x_vec'].__len__()*meas_data_dict['y_vec'].__len__())
y_val = []
num_freq_points = meas_data_dict['f_vec'].__len__()

for f in range(num_freq_points):
    y_val.append([])
    for y in range(meas_data_dict['y_vec'].__len__()):
        for x in range(meas_data_dict['x_vec'].__len__()):
            # min/max val of phase offset at each XY-point
            phase_offset_min = meas_data_dict['data_array'][1, 0, f, x, y, :].min()
            phase_offset_max = meas_data_dict['data_array'][1, 0, f, x, y, :].max()

            freq_offset_variation = phase_offset_max - phase_offset_min
            y_val[f].append(freq_offset_variation)
            print("Frequency offset variation: ", freq_offset_variation)


# Window Config
main_fig, main_axes = plt.subplots(nrows=1, ncols=num_freq_points)
main_fig.text(0.5, 0.975, str('Frequency Offset Variation in XY-Plane // Data drawn from ' + __filename), ha='center', fontsize=12)
info_string = "Maximum/Minimum Frequency Offset Variation [°] at "
for i in range(num_freq_points):
    x = x_val
    y = y_val[i]
    xmax = x[np.argmax(y)]
    ymax = max(y)
    xmin = x[np.argmin(y)]
    ymin = min(y)
    info_string = info_string + '@' + str(round(meas_data_dict['f_vec'][i]*1e-9,1)) + 'GHz: ' + str(round(ymax,3)) + '/' + str(round(ymin,3)) + ' '

    main_axes[i].plot(x, y, marker='o', linestyle='', color='b')
    main_axes[i].grid(True)
    main_axes[i].set_ylabel('Phase offset difference [°]')
    main_axes[i].set_xlabel('XY-point number')
    main_axes[i].legend('Phase offset [°]')
    main_axes[i].set_title('Frequency: ' + str(round(meas_data_dict['f_vec'][i]*1e-9,1)) + 'GHz')

main_fig.text(0.5, 0.04, info_string, ha='center', fontsize=12)
plt.tight_layout()
plt.show()

print("Done")