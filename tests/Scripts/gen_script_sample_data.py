import numpy as np
import json
from datetime import datetime

data: dict = {}
vna_info = {
    'parameter': ['S11', 'S22'],
    'freq_start': 10,
    'freq_stop': 50,
    'sweep_num_points': 5,
    'if_bw': 33,
    'output_power': 22,
    'average_number': 1,

}
data['measurement_config'] = {
                'type':             'Auto Measurement Data JSON',
                'timestamp':        "Uhrzeit und Datum",
                'zero_position':    [250.0, 300.0, 40.0],
                'mesh_x_min':       245, #[mm]
                'mesh_x_max':       255, #[mm]
                'mesh_x_steps':     10,
                'mesh_y_min':       295, #[mm]
                'mesh_y_max':       305, #[mm]
                'mesh_y_steps':     10,
                'mesh_z_min':       100, #[mm]
                'mesh_z_max':       110, #[mm]
                'mesh_z_steps':     50,
                'movespeed':        10, #[mm/s]
                'parameter':        vna_info['parameter'],
                'freq_start':       vna_info['freq_start'], #[Hz]
                'freq_stop':        vna_info['freq_stop'], #[Hz]
                'sweep_num_points': vna_info['sweep_num_points'],
                'if_bw':            vna_info['if_bw'], #[Hz]
                'output_power':     vna_info['output_power'], #[dBm]
                'average_number':   vna_info['average_number'],
            }

data['S11'] = []
data['S12'] = []
data['S22'] = []

# print(f"Starting first loop for large data sample... {datetime.now().strftime('%H:%M:%S')}")
# for z in np.linspace(data['measurement_config']['mesh_z_min'], data['measurement_config']['mesh_z_max'], data['measurement_config']['mesh_z_steps']):
#     for y in np.linspace(data['measurement_config']['mesh_y_min'], data['measurement_config']['mesh_y_max'],data['measurement_config']['mesh_y_steps']):
#         for x in np.linspace(data['measurement_config']['mesh_x_min'], data['measurement_config']['mesh_x_max'],data['measurement_config']['mesh_x_steps']):
#             for f in np.linspace(vna_info['freq_start'], vna_info['freq_stop'], vna_info['sweep_num_points']):
#                 data['S11'].append([x, y, z, f, x**2*y**2*f, 180])
#                 data['S12'].append([x, y, z, f, x*z*f, x*y])
#                 data['S22'].append([x, y, z, f, x*y*z, 90])
# print(f"Write large data sample to file... {datetime.now().strftime('%H:%M:%S')}")
# file = open('../../results/script_sample_data.json', 'w')
# file.write(json.dumps(data, indent=2))
# print(f"Writing done {datetime.now().strftime('%H:%M:%S')}")
# file.close()

red_data = {
    'measurement_config': data['measurement_config'],
    'data': [],
}
print(f"Starting second loop for reduced data sample... {datetime.now().strftime('%H:%M:%S')}")
for z in np.linspace(data['measurement_config']['mesh_z_min'], data['measurement_config']['mesh_z_max'], data['measurement_config']['mesh_z_steps']):
    for y in np.linspace(data['measurement_config']['mesh_y_min'], data['measurement_config']['mesh_y_max'],data['measurement_config']['mesh_y_steps']):
        for x in np.linspace(data['measurement_config']['mesh_x_min'], data['measurement_config']['mesh_x_max'],data['measurement_config']['mesh_x_steps']):
            for f in np.linspace(vna_info['freq_start'], vna_info['freq_stop'], vna_info['sweep_num_points']):
                red_data['data'].append([x, y, z, f, (x-240)*(y-290)*(z-90)*f, 180, x**2*y**2*f, x*y, (x%100)*(y%100)*(z%100), 90])
                #red_data_syntax = [ (0)[(0)x, (1)y, (2)z, (3)frequency, (4)S11-amplitude, (5)S11-phase, (6)S12-amplitude, (7)S12-phase, (8)S22-amplitude, (9)S22-phase], (1)[..], .. ]

print(f"Write reduced data sample to file... {datetime.now().strftime('%H:%M:%S')}")
red_file = open('../../results/reduced_script_sample_data.json', 'w')
red_file.write(json.dumps(red_data, indent=2))
print(f"Writing done {datetime.now().strftime('%H:%M:%S')}")

red_file.close()

