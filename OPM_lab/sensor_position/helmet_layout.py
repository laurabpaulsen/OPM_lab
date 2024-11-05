import numpy as np
import pickle
from pathlib import Path

class HelmetTemplate:    
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

    def get_chs_pos(self, labels:list[str]):
        """
        Retrieve the positions of the channels specified by the input labels.

        Parameters:
            labels (list): A list of channel labels to retrieve positions for.

        Returns:
            np.array: An array of positions for the specified channels.
        """
        if isinstance(labels, str):
            labels = [labels]

        positions = []

        for label in labels:
            if label in self.label:
                index = self.label.index(label)
                positions.append(self.chan_pos[index])
            else:
                print(f"Label '{label}' not found in the helmet template.")

        return np.array(positions)

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