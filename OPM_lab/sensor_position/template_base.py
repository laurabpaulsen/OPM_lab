import numpy as np

class TemplateBase:
    def __init__(self, label, unit):
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