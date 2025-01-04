import os
from datetime import datetime
import json
import numpy as np

""" JSON data tests """
# if __name__ == '__main__':
#     parameter = ['S11','S12']
#     data_storage = {}
#     measurement_config = {
#         'type': 'Auto Measurement Data JSON',
#         'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
#         'mesh_x_min': 0,
#         'mesh_x_max': 11,
#         'parameter': parameter
#     }
#     data_storage['measurement_config'] = measurement_config
#     for par in parameter:
#         json_obj = {
#             'parameter':    par,
#             'values':       []
#         }
#         data_storage[par] = json_obj
#
#     sample_data = [
#         [10, 10, 10, 3000, 5, 6],
#         [11, 10, 10, 3000, 5, 6],
#         [12, 10, 10, 3000, 5, 6],
#         [13, 10, 10, 3000, 5, 6],
#         [14, 10, 10, 3000, 5, 6],
#         [15, 10, 10, 3000, 5, 6],
#         [16, 10, 10, 3000, 5, 6],
#         [17, 10, 10, 3000, 5, 6]
#     ]
#     counter = 0
#     for sample in sample_data:
#         if counter % 2 == 0:
#             data_storage['S11']['values'].append(sample)
#         else:
#             data_storage['S12']['values'].append(sample)
#         counter += 1
#
#     file = open('datafile.json', "w")
#     jso = json.dumps(data_storage, indent=4)
#     file.write(jso)
#     file.close()
#
#     print("done")

""" List sort tests with key lambda """
def gen_snake_list_bodyscan(x_vec, y_vec, z_vec):
    x_move_vec = np.flip(x_vec.copy())  # Copy the x_vec and flip it because first run flips as well
    y_move_vec = y_vec.copy()  # Copy the y_vec
    z_offset = 0.5  # At least 0.2mm offset >> Z-direction change introduces a lack of 0.2mm!
                    # This can be avoided by always moving to a point from below and then moving up.
    snake_list = []
    for y in y_move_vec:
        x_move_vec = np.flip(x_move_vec)
        for x in x_move_vec:
            for z in z_vec:
                snake_list.append((float(x), float(y), float(z)))
    return snake_list

def gen_snake_list_automeasurement(x_vec, y_vec, z_vec):
    x_move_vec = np.flip(x_vec.copy())  # Copy the x_vec and flip it because first run flips as well
    y_move_vec = np.flip(y_vec.copy())  # Copy the y_vec and flip it because first run flips as well
    snake_list = []
    for z in z_vec:
        y_move_vec = np.flip(y_move_vec)
        for y in y_move_vec:
            x_move_vec = np.flip(x_move_vec)
            for x in x_move_vec:
                snake_list.append((float(x), float(y), float(z)))
    return snake_list


if __name__ == '__main__':
    x_vec = np.linspace(0, 10, 3)
    y_vec = np.linspace(0, 10, 3)
    z_vec = np.linspace(0, 5, 2)
    f_vec = np.linspace(1000, 3000, 3)

    point_list = gen_snake_list_bodyscan(x_vec, y_vec, z_vec)

    print("#### Snake approach | AutoMeasurement####")
    print("Original list:")
    for point in point_list:
        print(point)

    """ Append Meas data """
    meas_list = []
    s11 = 100
    s12 = 101
    for point in point_list:
        for f in f_vec:
            meas_list.append([point[0], point[1], point[2], f, s11, s12])
            s11 += 2
            s12 += 2

    print("\n#### Meas Data List ####")
    for meas in meas_list:
        print(meas)

    """ Sort the list """
    # Sort the list by f > x > y > z
    sorted_data = sorted(meas_list, key=lambda sublist: (sublist[2], sublist[1], sublist[0], sublist[4]))

    print("\n#### Sorted Meas Data List ####")
    for meas in sorted_data:
        print(meas)

    #   Successfully tested 04.01.2025 for AutoMeasurement snake --
    #   meas list looks like one runs along x positive direction, then y positive direction, then z positive direction


"""
sorted AutoMeasurement snake list:
[0.0, 0.0, 0.0, 1, 100, 101]
[5.0, 0.0, 0.0, 2, 102, 103]
[10.0, 0.0, 0.0, 3, 104, 105]
[0.0, 5.0, 0.0, 6, 110, 111]
[5.0, 5.0, 0.0, 5, 108, 109]
[10.0, 5.0, 0.0, 4, 106, 107]
[0.0, 10.0, 0.0, 7, 112, 113]
[5.0, 10.0, 0.0, 8, 114, 115]
[10.0, 10.0, 0.0, 9, 116, 117]
[0.0, 0.0, 5.0, 18, 134, 135]
[5.0, 0.0, 5.0, 17, 132, 133]
[10.0, 0.0, 5.0, 16, 130, 131]
[0.0, 5.0, 5.0, 13, 124, 125]
[5.0, 5.0, 5.0, 14, 126, 127]
[10.0, 5.0, 5.0, 15, 128, 129]
[0.0, 10.0, 5.0, 12, 122, 123]
[5.0, 10.0, 5.0, 11, 120, 121]
[10.0, 10.0, 5.0, 10, 118, 119]

sorted BodyScan snake list:
[0.0, 0.0, 0.0, 1, 100, 101]
[5.0, 0.0, 0.0, 3, 104, 105]
[10.0, 0.0, 0.0, 5, 108, 109]
[0.0, 5.0, 0.0, 11, 120, 121]
[5.0, 5.0, 0.0, 9, 116, 117]
[10.0, 5.0, 0.0, 7, 112, 113]
[0.0, 10.0, 0.0, 13, 124, 125]
[5.0, 10.0, 0.0, 15, 128, 129]
[10.0, 10.0, 0.0, 17, 132, 133]
[0.0, 0.0, 5.0, 2, 102, 103]
[5.0, 0.0, 5.0, 4, 106, 107]
[10.0, 0.0, 5.0, 6, 110, 111]
[0.0, 5.0, 5.0, 12, 122, 123]
[5.0, 5.0, 5.0, 10, 118, 119]
[10.0, 5.0, 5.0, 8, 114, 115]
[0.0, 10.0, 5.0, 14, 126, 127]
[5.0, 10.0, 5.0, 16, 130, 131]
[10.0, 10.0, 5.0, 18, 134, 135]


"""