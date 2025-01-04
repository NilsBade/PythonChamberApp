"""
This script is meant for testing purposes of loop-methods that can be used in routines like
AutoMeasurement and BodyScan to run through meshes more efficiently.
"""

import numpy as np

#   Define Sample Mesh data
x_vec = np.linspace(0, 10, 3)
y_vec = np.linspace(0, 10, 3)
z_vec = np.linspace(0, 5, 3)

#   Regular approach >> axis by axis
print("#### Regular approach ####")
for z in z_vec:
    for y in y_vec:
        for x in x_vec:
            print(f"({x}, {y}, {z})")

#   Snake approach | AutoMeasurement >> Always smallest move possible
x_move_vec = np.flip(x_vec.copy())  # Copy the x_vec and flip it because first run flips as well
y_move_vec = np.flip(y_vec.copy())  # Copy the y_vec and flip it because first run flips as well

print("\n\n#### Snake approach | AutoMeasurement####")
for z in z_vec:
    y_move_vec = np.flip(y_move_vec)
    for y in y_move_vec:
        x_move_vec = np.flip(x_move_vec)
        for x in x_move_vec:
            print(f"({x}, {y}, {z})")


#   Snake approach | BodyScan >> Always smallest move possible XY wise
x_move_vec = np.flip(x_vec.copy())  # Copy the x_vec and flip it because first run flips as well
y_move_vec = y_vec.copy()  # Copy the y_vec, no flip necessary
z_offset = 0.5  # At least 0.2mm offset >> Z-direction change introduces a lack of 0.2mm!
                # This can be avoided by always moving to a point from below and then moving up.

print("\n\n#### Snake approach | BodyScan ####")
for y in y_move_vec:
    x_move_vec = np.flip(x_move_vec)
    for x in x_move_vec:
        print(f"Z-Off:({x}, {y}, {z_vec[0] - z_offset})")
        for z in z_vec:
            print(f"({x}, {y}, {z})")
