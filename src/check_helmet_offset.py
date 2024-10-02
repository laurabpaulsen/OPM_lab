"""
This file is used to determine whether the fieldtrip template accounts for the offset between the outside and the inside of the helmet
This is done by comparing it to a digitisation of the helmet made using the polhemus. See digitise_helmet.py
"""

import sys 
sys.path.append("../OPM_lab")


import OPM_lab.sensor_locations as sens
import matplotlib.pyplot as plt
import pandas as pd
import mat73
import numpy as np


data_dict = mat73.loadmat('/Users/au661930/Library/CloudStorage/OneDrive-Aarhusuniversitet/Dokumenter/OPM_lab/OPM_lab/template/fieldlinealpha1.mat')
data = data_dict["fieldlinealpha1"]

template = {
    "chanori": data["chanori"],
    "chanpos": data["chanpos"],
    "label": [lab[0] for lab in data["label"]],
    "fidlabel": [lab[0] for lab in data["fid"]["label"]],
    "fidpos": data["fid"]["pos"]
}


helmet = pd.read_csv("//Users/au661930/Library/CloudStorage/OneDrive-Aarhusuniversitet/Dokumenter/OPM_lab/output/helmet_digitisation.csv", names = ['sensor_type', 'label', 'x', 'y', 'z'])

digitised_points = pd.DataFrame(helmet[helmet["sensor_type"]== "fiducials"], columns=["x", "y", "z"]).values.T
template_points = template["fidpos"].T * 100
template_sensors = template["chanpos"].T * 100

R, t, Yf = sens.rot3dfit(digitised_points, template_points)

digitised_head_points = pd.DataFrame(helmet[helmet["sensor_type"]== "helmet"], columns=["x", "y", "z"]).values.T


# transforming digitised points
digitised_in_template_space = R @ digitised_points + t
digitised_head_in_template_space = R @ digitised_head_points + t


# plot the results
fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')

ax.scatter(digitised_in_template_space[0, :], digitised_in_template_space[1, :], digitised_in_template_space[2, :], c='blue', label='Digtised fiducials')
ax.scatter(digitised_head_in_template_space[0, :], digitised_head_in_template_space[1, :], digitised_head_in_template_space[2, :], c='lightblue', label='Digitised helmet points', alpha = 0.5)
ax.scatter(template_points[0, :], template_points[1, :], template_points[2, :], c='red', label='Template fiducials')
ax.scatter(template_sensors[0, :], template_sensors[1, :], template_sensors[2, :], c='orange', label='Template sensors')

ax.legend()
plt.show()

