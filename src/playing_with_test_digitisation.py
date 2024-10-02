"""
This file is used to determine whether the fieldtrip template accounts for the offset between the outside and the inside of the helmet
This is done by comparing it to a digitisation of the helmet made using the polhemus. See digitise_helmet.py
"""

import sys 
sys.path.append("../OPM_lab")

import OPM_lab.sensor_locations as sens
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import math
from pathlib import Path

template = sens.FL_alpha1_helmet

def calculate_distance(a, b):
    # Ensure both points have the same number of dimensions
    assert a.shape == b.shape, "Points a and b must have the same number of dimensions"

    # Calculate the Euclidean distance
    distance = math.sqrt(sum((a_i - b_i) ** 2 for a_i, b_i in zip(a, b)))
    
    return distance

def transform_template_head_z(template_ori, template_pos, depth_meas, len_sleeve = 75/1000, offset = 13/1000):
    # Ensure the lengths of the inputs are consistent
    assert template_ori.shape[0] == len(depth_meas)
    assert template_pos.shape[0] == len(depth_meas)

    # Create a new list to store the updated positions
    transformed_pos = []
    
    # Move template pos by measurement length in template ori direction
    for i in range(len(template_ori)):
        # Update the position by adding the orientation scaled by the measurement
        new_pos = template_pos[i] + template_ori[i] * -(len_sleeve - (depth_meas[i]+offset))
        transformed_pos.append(new_pos)
    
    return np.array(transformed_pos).T


def get_coordinates_dig_type(data, dig_type = "OPM"):
    subset = data[data["sensor_type"]== dig_type]
    return subset.loc[:, ["x", "y", "z"]].values.T



if __name__ in "__main__":
    filename = "test_digitisation.csv"
    filepath = Path(__file__).parents[1] / "output" / filename

    if "1" in filename or "2" in filename:#FOR TEST1 and TEST2
        measurements = [40/1000, 47/1000, 44/1000, 40/1000] # mm (order = 3, 10, 16, 62)

    else:
        measurements = [47/1000, 47/1000, 51/1000, 43/1000] # mm (order =["FL52", "FL61", "FL92", "FL99"])     


    dig = pd.read_csv(filepath, names = ['sensor_type', 'label', 'x', 'y', 'z'])


    OPMs = dig[dig["sensor_type"]== "OPM"]
    
    digitised_opms = get_coordinates_dig_type(dig, dig_type = "OPM")
    digitised_points_label = list(dig[dig["sensor_type"]== "OPM"]["label"])

    digitised_helmet_fids = get_coordinates_dig_type(dig, dig_type = "helmet_fiducials")

    idx = [template.label.index(label) for label in digitised_points_label if label in template.label]

    template_fid_points = template.fid_pos.T * 100
    template_sensors = template.chan_pos[idx].T * 100
    template_sensors_ori = template.chan_ori[idx].T * 100

    R, t, Yf = sens.rot3dfit(digitised_helmet_fids, template_fid_points)

    digitised_head_points = pd.DataFrame(dig[dig["sensor_type"]== "head_shape"], columns=["x", "y", "z"]).values.T

    # transforming digitised points
    digitised_opm_in_template_space = sens.transform_points(digitised_opms, R = R, t = t)
    digitised_head_in_template_space = sens.transform_points(digitised_head_points, R = R, t = t)
    digitised_fid_in_template_space = sens.transform_points(digitised_helmet_fids, R = R, t = t)


    helmet_sensors_transformed_z = transform_template_head_z(template_sensors_ori.T, template_sensors.T, measurements)
    print(f"error between helmet_sensors_transformed_z points and digitised sensor positions= {[calculate_distance(a,b) for a,b in zip(helmet_sensors_transformed_z.T, digitised_opm_in_template_space.T)]}")


    # plot the results
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')

    # head points -> nose, eyebrows and random points
    ax.scatter(digitised_head_in_template_space[0, :], digitised_head_in_template_space[1, :], digitised_head_in_template_space[2, :], c='lightblue', label='Digitised head points', alpha = 0.5)

    # fiducials
    ax.scatter(digitised_fid_in_template_space[0, :], digitised_fid_in_template_space[1, :], digitised_fid_in_template_space[2, :], c='darkgreen', label='Digitised helmet fiducials')
    ax.scatter(template_fid_points[0, :], template_fid_points[1, :], template_fid_points[2, :], c='lightgreen', label='Template helmet fiducials')

    # sensors
    ax.scatter(digitised_opm_in_template_space[0, :], digitised_opm_in_template_space[1, :], digitised_opm_in_template_space[2, :], c='darkorange', label='Digtised OPM sensors')
    ax.scatter(template_sensors[0, :], template_sensors[1, :], template_sensors[2, :], c='gold', label='Template OPM sensors')
    ax.scatter(helmet_sensors_transformed_z[0, :], helmet_sensors_transformed_z[1, :], helmet_sensors_transformed_z[2, :], c='pink', label='Transformed template OPM sensors based on depth measurement')

    ax.legend()
    plt.show()

