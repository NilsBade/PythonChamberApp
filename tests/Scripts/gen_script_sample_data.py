import numpy as np
import json

data: dict = {}
vna_info = {
    'parameter': ['S11', 'S12', 'S22'],
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
                'zero_position':    [250.0, 300.0, 0.0],
                'mesh_x_min':       245, #[mm]
                'mesh_x_max':       255, #[mm]
                'mesh_x_steps':     100,
                'mesh_y_min':       295, #[mm]
                'mesh_y_max':       305, #[mm]
                'mesh_y_steps':     100,
                'mesh_z_min':       100, #[mm]
                'mesh_z_max':       110, #[mm]
                'mesh_z_steps':     20,
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

for z in np.linspace(data['measurement_config']['mesh_z_min'], data['measurement_config']['mesh_z_max'], data['measurement_config']['mesh_z_steps']):
    for y in np.linspace(data['measurement_config']['mesh_y_min'], data['measurement_config']['mesh_y_max'],data['measurement_config']['mesh_y_steps']):
        for x in np.linspace(data['measurement_config']['mesh_x_min'], data['measurement_config']['mesh_x_max'],data['measurement_config']['mesh_x_steps']):
            for f in np.linspace(vna_info['freq_start'], vna_info['freq_stop'], vna_info['sweep_num_points']):
                data['S11'].append([x, y, z, f, x**2*y**2*f, 180])
                data['S12'].append([x, y, z, f, x*z*f, x*y])
                data['S22'].append([x, y, z, f, x*y*z, 90])

file = open('../../results/script_sample_data.json', 'w')
file.write(json.dumps(data, indent=4))
file.close()

