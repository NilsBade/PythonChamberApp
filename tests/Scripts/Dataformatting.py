import os
from datetime import datetime


if __name__ == '__main__':
    parameter = ['S11','S12']
    data_storage = {}
    measurement_config = {
        'type': 'Auto Measurement Data JSON',
        'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        'mesh_x_min': 0,
        'mesh_x_max': 11,
        'parameter': parameter
    }
    data_storage['measurement_config'] = measurement_config
    for par in parameter:
        json_obj = {
            'parameter':    par,
            'values':       []
        }
        data_storage[par] = json_obj

    sample_data = [
        [10, 10, 10, 3000, 5, 6],
        [11, 10, 10, 3000, 5, 6],
        [12, 10, 10, 3000, 5, 6],
        [13, 10, 10, 3000, 5, 6],
        [14, 10, 10, 3000, 5, 6],
        [15, 10, 10, 3000, 5, 6],
        [16, 10, 10, 3000, 5, 6],
        [17, 10, 10, 3000, 5, 6]
    ]
    counter = 0
    for sample in sample_data:
        if counter % 2 == 0:
            data_storage['S11']['values'].append(sample)
        else:
            data_storage['S12']['values'].append(sample)
        counter += 1

    print("done")