import numpy as np
import pickle
from pathlib import Path

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
            np.array: An array of positions for the specified channels.
        """
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

    outpath = Path(__file__).parents[1] / "OPM_lab" / "template"
    data_dict = mat73.loadmat(outpath / 'fieldlinealpha1.mat')
    data = data_dict["fieldlinealpha1"]

    FL_template = HelmetTemplate(
        chan_pos=data["chanpos"],
        chan_ori=data["chanori"],
        label=[label[0] for label in data["label"]],
        fid_label=[label[0] for label in data["fid"]["label"]],
        fid_pos=data["fid"]["pos"],
        unit=data["unit"])

    outpath = Path(__file__).parents[1] / "OPM_lab" / "template"
    with open(outpath / "FL_alpha1_helmet.pkl", 'wb') as file:
        pickle.dump(FL_template, file)