"""
This script is supposed to visualize the difference of two ore more different calibration-matrices from different files.
The goal is to prove or disprove the validity of calibration of one measurement by the matrix of another measurement
"""
import os
import numpy as np
from DataManagementMethods import read_measurement_data_from_file
import matplotlib.pyplot as plt

filenames = ['PhaseMeasurementOnS11_0002_compensated.json', 'PhaseMeasurementOnS11_0003_compensated.json',
             'PhaseMeasurementOnS11_0004_compensated.json', 'PhaseMeasurementOnS11_S22_0005_compensated.json',
             'PhaseMeasurementOnS11_S22_0006_compensated.json', 'PhaseMeasurementOnS11_S22_0007_compensated.json']
file_data = []
results_dir = os.path.join(os.path.abspath(os.path.join(os.getcwd(), os.pardir)), 'results')
print("results directory should be at: ", results_dir)

for i in range(len(filenames)):
    file_data.append(read_measurement_data_from_file(os.path.join(results_dir, filenames[i])))

# Window Config
main_fig = plt.figure(figsize=(18, 7))
main_axes = []
# fig layout N x 3 Graphs dependend on number of files
rows = int(filenames.__len__()/3)
if filenames.__len__() % 3 != 0:
    rows += 1

if filenames.__len__() >= 3:
    cols = 3
else:
    cols = filenames.__len__()

for idx in range(filenames.__len__()):
    main_axes.append(main_fig.add_subplot(rows, cols, idx+1, projection='3d'))
manager_main_fig = plt.get_current_fig_manager()
manager_main_fig.set_window_title('Phase Calibration Matrix Values [°]')

for i in range(len(filenames)):
    x_vec = np.array(file_data[i]['x_vec'])
    y_vec = np.array(file_data[i]['y_vec'])
    x, y = np.meshgrid(x_vec, y_vec)
    calib_matrix = np.array(file_data[i]['calibration_data'])
    for f in range(file_data[i]['f_vec'].__len__()):
        z = calib_matrix[f, :, :]
        main_axes[i].plot_surface(x, y, z, cmap='viridis',
                        label='Phase Cal @ ' + str(round(file_data[i]['f_vec'][f] * 1e-9, 1)) + 'GHz')
        main_axes[i].set_xlabel('X-Coordinate')
        main_axes[i].set_ylabel('Y-Coordinate')
        main_axes[i].set_zlabel('Phase [°]')
        main_axes[i].legend()
    main_axes[i].set_title(filenames[i])

plt.tight_layout()
plt.show()
