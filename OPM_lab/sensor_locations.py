import numpy as np
from matplotlib import cm
import matplotlib.pyplot as plt
import pickle
from pathlib import Path


def rot3dfit(A, B, verbose=1):
    """
    TRY NON-linear or affine

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
        raise ValueError("A and B must be 3 x N matrices")

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
        V[2, :] *= -1
        R = V.T @ U.T

    # translation vector
    t = -R @ centroid_A + centroid_B

    # best fit
    Yf = R @ A + t

    dY = B - Yf
    if verbose > 0:
        errors = []
        for point in range(dY.shape[0]):
            err = np.linalg.norm(dY[:, point])
            errors.append(err)

        print("Error: ", errors)

    return R, t, Yf


def transform_points(points: np.array, R: np.array, t: np.array):
    """
    Transforms a set of 3D points given a orthogonal rotation matrix and a translation vector

    Args:
        points (np.array): (3, number of points) matrix
        R (np.array): (3, 3) orthogonal rotation matrix
        t (np.array): (3, 1 translation vector

    Returns:
        transformed_points: The transformed points.
    """

    return R @ points + t


def plot_sensor_locations(info):
    loc = []

    for i, ch in enumerate(info["chs"]):
        tmp_loc = ch["loc"][:3]  # extract x, y, z
        loc.append(tmp_loc)

    loc = np.array(loc)

    x = loc[:, 0]
    y = loc[:, 1]
    z = loc[:, 2]

    # create an array of colors (one color per channel)
    n_channels = loc.shape[0]
    colors = cm.rainbow(np.linspace(0, 1, n_channels))

    # creating a 3D scatter plot
    fig = plt.figure()
    ax = fig.add_subplot(111, projection="3d")
    ax.scatter(x, y, z, c=colors, marker="o")  # Assign the colors to each point

    ax.set_xlabel("X")
    ax.set_ylabel("Y")
    ax.set_zlabel("Z")

    plt.show()


class HelmetTemplate:
    def __init__(self, chan_ori, chan_pos, label, fid_pos, fid_label, unit):
        self.chan_ori = chan_ori
        self.chan_pos = chan_pos
        self.fid_pos = fid_pos
        self.fid_label = fid_label
        self.label = label
        self.unit = unit

    def get_chs_pos(self, labels):
        """
        Retrieve the positions of the channels specified by the input labels.

        Parameters:
            labels (list): A list of channel labels to retrieve positions for.

        Returns:
            list: A list of positions for the specified channels.
        """
        positions = []

        for label in labels:
            if label in self.label:
                index = self.label.index(label)
                positions.append(self.chan_pos[index])
            else:
                print(f"Label '{label}' not found in the helmet template.")

        return positions

    def get_chs_ori(self, labels):
        """
        Retrieve the positions of the channels specified by the input labels.

        Parameters:
            labels (list): A list of channel labels to retrieve positions for.

        Returns:
            list: A list of orientations for the specified channels.
        """
        orientations = []

        for label in labels:
            if label in self.label:
                index = self.label.index(label)
                orientations.append(self.chan_ori[index])
            else:
                print(f"Label '{label}' not found in the helmet template.")

        return orientations


class OPMSensorLayout:
    def __init__(self, OPM_ori, OPM_pos, label):
        self.OPM_ori = OPM_ori
        self.OPM_pos = OPM_pos
        self.label = label


# custom unpickler to ensure the correct class is found
class CustomUnpickler(pickle.Unpickler):
    def find_class(self, module, name):
        if name == "HelmetTemplate":
            return HelmetTemplate
        return super().find_class(module, name)


# Get the absolute path to the current module's directory
module_dir = Path(__file__).parent

# Construct the full path to the template file
template_path = module_dir / "template" / "FL_alpha1_helmet.pkl"

# Open the file and load the pickle object using the custom unpickler
with template_path.open("rb") as file:
    FL_alpha1_helmet = CustomUnpickler(file).load()
