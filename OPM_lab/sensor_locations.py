import numpy as np
from matplotlib import cm
import matplotlib.pyplot as plt
from .helmet_template import HelmetTemplate
from mne.utils._bunch import NamedInt


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


class OPMSensorLayout:
    def __init__(self, label, depth, helmet_template:HelmetTemplate, coil_type:NamedInt = NamedInt("FieldLine OPM sensor Gen1 size = 2.00   mm", 8101)):
        self.label = label
        self.depth = depth
        self.helmet_template = helmet_template
        self.unit = self.helmet_template.unit
        self.coil_type = coil_type
        
        self.make_sensor_layout()

    def make_sensor_layout(self):
        # Update template location given the depth measurement
        self.chan_pos = self.transform_template_depth()
        self.chan_ori = self.helmet_template.get_chs_ori(self.label)
    
    def transform_template_depth(self, len_sleeve:float = 0.075, offset:float = 40/1000): #len_sleeve:float = 75/1000, offset:float = 13/1000
        template_ori = self.helmet_template.get_chs_ori(self.label)
        template_pos = self.helmet_template.get_chs_pos(self.label)
        
        # Create a new list to store the updated positions
        transformed_pos = []
        
        # Move template pos by measurement length in template ori direction
        for pos, ori, depth in zip(template_pos, template_ori, self.depth):
            # Normalize the orientation vector
            ori = np.array(ori)
            norm = np.linalg.norm(ori)
            if norm != 0: # they are all very close to 1 so maybe omit this
                ori = ori / norm
                print(f"not norm ={norm}")
            
            # Update the position by adding the normalized orientation scaled by the measurement
            new_pos = np.array(pos) + ori * -(len_sleeve - (depth + offset))
            transformed_pos.append(new_pos)
        
        return np.array(transformed_pos)
