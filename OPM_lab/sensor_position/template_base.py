import numpy as np

class TemplateBase:
    def __init__(self, label, unit):
        self.label = label
        self.unit = unit
        self.chan_pos = np.array([])

    def get_attributes_by_labels(self, labels, attribute):
        """
        General method to retrieve values of a specified attribute based on labels.

        Parameters:
            labels (list[str] or str): A list of labels or a single label to retrieve data for.
            attribute (str): The name of the attribute to retrieve (e.g., 'chan_pos', 'chan_ori').

        Returns:
            np.array: An array of values for the specified attribute based on the input labels.
        """
        # if one label is supplied rather than a list, make sure to put it in a list
        if isinstance(labels, str):
            labels = [labels]

        # Get the attribute (e.g., self.chan_pos, self.chan_ori)
        attr_values = getattr(self, attribute, None)
        if attr_values is None:
            raise AttributeError(f"Attribute '{attribute}' not found in the template.")

        # Retrieve values based on labels
        values = []
        for label in labels:
            if label in self.label:
                index = self.label.index(label)
                values.append(attr_values[index])
            else:
                print(f"Label '{label}' not found in the template.")

        return np.array(values)
    
    
    def get_chs_pos(self, labels:list[str]):
        """
        Retrieve the positions of the channels specified by the input labels.
        
        Parameters:
            labels (list[str] or str): A list of channel label or a channel label to retrieve positions for.
        
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

        return self.get_attributes_by_labels(labels, 'chan_pos')