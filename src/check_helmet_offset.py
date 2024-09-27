"""
This file is used to determine whether the fieldtrip template accounts for the offset between the outside and the inside of the helmet
This is done by comparing it to a digitisation of the helmet made using the polhemus. See digitise_helmet.py
"""

import sys 
sys.path.append("../OPM_lab")
import matplotlib.pyplot as plt
import pandas as pd
import mat73
import numpy as np

def rot3dfit(A, B):
    """
    Permforms a least-square fit for the linear form 
    Y = X*R + T

    where R is a 3 x 3 orthogonal rotation matrix, t is a 1 x 3
    translation vector, and A and B are sets of 3D points defined as
    3 x N matrices, where N is the number of points.

    Implementation of the rigid 3D transform algorithm from:
    Least-Squares Fitting of Two 3-D Point Sets,
    Arun, K. S. and Huang, T. S. and Blostein, S. D (1987)
    """
    assert A.shape == B.shape

    if A.shape[0] != 3 or B.shape[0] != 3:
        raise ValueError('A and B must be 3 x N matrices')

    # compute centroids (average points over each dimension (x, y, z))
    centroid_A = np.mean(A, axis=1) 
    centroid_B = np.mean(B, axis=1)
    
    centroid_A = centroid_A.reshape(-1, 1)
    centroid_B = centroid_B.reshape(-1, 1)

    # to find the optimal rotation we first re-centre both dataset 
    # so that both centroids are at the origin (subtract mean)
    Ac = A - centroid_A
    Bc = B - centroid_B

    # rotation matrix
    H = Ac @ Bc.T
    U, S, V = np.linalg.svd(H)
    R = V.T @ U.T
    
    if np.linalg.det(R) < 0:
        print("det(R) < R, reflection detected!, correcting for it ...")
        V[2,:] *= -1
        R = V.T @ U.T

    # translation vector
    t = -R @ centroid_A + centroid_B 

    # best fit 
    Yf = R @ A + t

    dY = B - Yf
    errors = []
    for point in range(dY.shape[0]):
        err = np.linalg.norm(dY[:, point])
        errors.append(err)

    print('Error: ', errors)
    return R, t, Yf


import numpy as np
import matplotlib.pyplot as plt



data_dict = mat73.loadmat('/Users/laurapaulsen/Desktop/project placement/OPM_lab/OPM_lab/template/fieldlinealpha1.mat')
data = data_dict["fieldlinealpha1"]

template = {
    "chanori": data["chanori"],
    "chanpos": data["chanpos"],
    "label": [lab[0] for lab in data["label"]],
    "fidlabel": [lab[0] for lab in data["fid"]["label"]],
    "fidpos": data["fid"]["pos"]
}


helmet = pd.read_csv("/Users/laurapaulsen/Desktop/project placement/OPM_lab/output/helmet_digitisation.csv", names = ['sensor_type', 'label', 'x', 'y', 'z'])

digitised_points = pd.DataFrame(helmet[helmet["sensor_type"]== "fiducials"], columns=["x", "y", "z"]).values.T
template_points = template["fidpos"].T * 100
template_sensors = template["chanpos"].T * 100

R, t, Yf = rot3dfit(digitised_points, template_points)


digitised_head_points = pd.DataFrame(helmet[helmet["sensor_type"]== "helmet"], columns=["x", "y", "z"]).values.T


# transforming digitised points
digitised_in_template_space = R @ digitised_points + t
digitised_head_in_template_space = R @ digitised_head_points + t


# plot the results
fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')

ax.scatter(digitised_in_template_space[0, :], digitised_in_template_space[1, :], digitised_in_template_space[2, :], c='blue', label='Digtised fiducials')
ax.scatter(digitised_head_in_template_space[0, :], digitised_head_in_template_space[1, :], digitised_head_in_template_space[2, :], c='lightblue', label='Digitised helmet points', alpha = 0.3)
ax.scatter(template_points[0, :], template_points[1, :], template_points[2, :], c='red', label='Template fiducials')
ax.scatter(template_sensors[0, :], template_sensors[1, :], template_sensors[2, :], c='yellow', label='Template sensors')

ax.legend()
plt.show()

