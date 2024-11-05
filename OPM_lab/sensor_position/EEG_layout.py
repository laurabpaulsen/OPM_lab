import mne
import numpy as np

class EEGcapTemplate:
    def __init__(self, montage:str):
        self.montage = montage
        self.chan_pos, self.label, self.unit = self.get_montage_information()
    
    def get_montage_information(self):

        mne_montage = mne.channels.make_standard_montage(self.montage)

        positions = []

        for digpoint in mne_montage.dig:
            if digpoint["kind"]==3: # if it is EEG 
                positions.append(digpoint["r"])        

        return np.array(positions), mne_montage.ch_names, "mm"

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
                print(f"Label '{label}' not found in the template.")

        return np.array(positions)