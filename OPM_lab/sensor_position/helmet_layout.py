import numpy as np
import pickle
from pathlib import Path
import pandas as pd
from .template_base import TemplateBase

class HelmetTemplate(TemplateBase):    
    """
    A class representing the template layout of a helmet with positions and orientations of sensor slots.
    It stores positions, orientations, fiducial positions, and associated labels, 
    allowing retrieval of channel-specific data by label.

    Parameters
    ----------
    chan_ori : list of lists
        A list containing orientation vectors (3D) for each sensor channel.
    chan_pos : list of lists
        A list containing position vectors (3D) for each sensor channel.
    label : list of str
        A list of labels for each sensor channel.
    fid_pos : list of lists
        A list containing position vectors for each fiducial point on the helmet.
    fid_label : list of str
        A list of labels for each fiducial point.
    unit : str
        The unit of measurement for the positions (e.g., "mm" for millimeters).

    Attributes
    ----------
    chan_ori : list of lists
        Orientation vectors of each channel in the helmet template.
    chan_pos : list of lists
        Position vectors of each channel in the helmet template.
    fid_pos : list of lists
        Position vectors for fiducial points on the helmet.
    fid_label : list of str
        Labels associated with fiducial points on the helmet.
    label : list of str
        Labels identifying each sensor channel.
    unit : str
        Unit of measurement for position values.
    """
    def __init__(self, chan_ori, chan_pos, label, fid_pos, fid_label, unit):
        self.chan_ori = chan_ori
        self.chan_pos = chan_pos
        self.fid_pos = fid_pos
        self.fid_label = fid_label
        self.label = label
        self.unit = unit
        super().__init__(label, unit)

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

        return np.array(orientations)

    def get_fid_pos(self, labels):
        """
        Retrieve the positions of the channels specified by the input labels.

        Parameters:
            labels (list): A list of channel labels to retrieve positions for.

        Returns:
            list: A list of orientations for the specified channels.
        """
        pos = []

        for label in labels:
            if label in self.fid_label:
                index = self.label.index(label)
                pos.append(self.fid_pos[index])
            else:
                print(f"Label '{label}' not found as a helmet fiducial label in the helmet template.")

        return np.array(pos)


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



def generate_FL_helmet_template():
    """
    Very important that all the depth measurements in the Alpha 1 Adjustable Helmet Sensor locations.xlsx is set to 52 when loading in.
    Otherwise the remaining functions, e.g. when creating the OPMSensorLayout based on the depth measurements will be wrong
    """

    outpath = Path("OPM_lab") / "sensor_position" / "template"
    df = pd.read_excel("../Alpha 1.2 Helmet Digital File Packet/Alpha 1 Adjustable Helmet Sensor locations.xlsx")

    # Create a list to hold the orientation matrices
    orientation_matrices = []

    # Loop through each row and create a 3x3 matrix
    for index, row in df.iterrows():
        matrix = np.array([
            [row["ex_i"], row["ex_j"], row["ex_k"]],
            [row["ey_i"], row["ey_j"], row["ey_k"]],
            [row["ez_i"], row["ez_j"], row["ez_k"]]
        ])
        orientation_matrices.append(matrix)

    # Convert the list to a numpy array if you want a full 3D array
    orientation_matrices = np.array(orientation_matrices)


    positions = []
    # Loop through each row and create a 3x3 matrix
    for index, row in df.iterrows():
        vector = np.array([
            row["sensor_x"], row["sensor_y"], row["sensor_z"]
            #row["x cell"], row["y cell"], row["z cell"]
        ])
        positions.append(vector)

    positions = np.array(positions)

    helmet_fiducials = {
        "labels": ["A1", "A2", "A3", "A4", "A5", "A6", "A7", "A8", 
                "B1", "B2", "B3", "B4", "B5", "B6", "B7", "B8", "B9"],
        "X": [0.08923, 0.07301, 0.04718, 0.02051, -0.02051, -0.04718, -0.07301, -0.08923,
            0.09968, 0.09881, 0.08515, 0.04198, 0, -0.04198, -0.08515, -0.09881, -0.09968],
        "Y": [0.06384, 0.09659, 0.12448, 0.13806, 0.13806, 0.12448, 0.09659, 0.06384,
            -0.01251, 0.0258, 0.07538, 0.12871, 0.14151, 0.12871, 0.07538, 0.0258, -0.01251],
        "Z": [-0.034, -0.018, -0.009, -0.008, -0.008, -0.009, -0.018, -0.034,
            -0.05268, -0.0139, -0.03885, -0.01391, -0.01391, -0.01391, -0.03885, -0.0139, -0.05268]
    }
    helmet_fiducials = pd.DataFrame.from_dict(helmet_fiducials)

    fiducial_positions = []
    
    # Loop through each row and create a 3x3 matrix
    for index, row in helmet_fiducials.iterrows():
        vector = np.array([
            row["X"], row["Y"], row["Z"]
        ])
        fiducial_positions.append(vector)

    fiducial_positions = np.array(fiducial_positions)

    # Create the DataFrame
    helmet_fiducials = pd.DataFrame(helmet_fiducials)

    FL_template = HelmetTemplate(
        chan_pos=positions,
        chan_ori=orientation_matrices,
        label=[f"FL{i}" for i in range(1, 108)],
        fid_label=helmet_fiducials["labels"],
        fid_pos=fiducial_positions,
        unit="m")

    with open(outpath / "FL_alpha1_helmet.pkl", 'wb') as file:
        pickle.dump(FL_template, file)
    print("new template generated")


def generate_FL_helmet_template_old(): # NOW RELYING ON FILE FROM FIELDLINE INSTEAD!!
    import mat73

    outpath = Path(__file__).parents[1] / "sensor_position" / "template"
    data_dict = mat73.loadmat(outpath / 'fieldlinealpha1.mat')
    data = data_dict["fieldlinealpha1"]

    FL_template = HelmetTemplate(
        chan_pos=data["chanpos"],
        chan_ori=data["chanori"],
        label=[label[0] for label in data["label"]],
        fid_label=[label[0] for label in data["fid"]["label"]],
        fid_pos=data["fid"]["pos"],
        unit=data["unit"])

    with open(outpath / "FL_alpha1_helmet.pkl", 'wb') as file:
        pickle.dump(FL_template, file)


if __name__ in "__main__":
    generate_FL_helmet_template()