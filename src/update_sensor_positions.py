
import mne
from scipy.spatial.transform import Rotation as R # for conversion from eulers angles to rotation matrix

from pathlib import Path
import pandas as pd
import numpy as np
import sys
import matplotlib.pyplot as plt
from pyvista import Plotter
from mne.viz import plot_alignment, set_3d_backend
set_3d_backend("pyvistaqt")
current_file = Path(__file__).resolve()
parent_directory = current_file.parent.parent 
sys.path.append(str(parent_directory)) 

from OPM_lab.sensor_locations import FL_alpha1_helmet, HelmetTemplate, rot3dfit


print(np.min(FL_alpha1_helmet.chan_ori), np.max(FL_alpha1_helmet.chan_ori))


def add_dig_montage(mne_object, df:pd.DataFrame):
    fiducials = {}

    for label in ["nasion", "lpa", "rpa"]:
        fid = df[df["label"] == label].loc[:, ["x", "y", "z"]]
        fiducials[label] = np.array(fid).squeeze() / 100  # converting to meters!

    head_points = df[df["label"] == "head"].loc[:, ["x", "y", "z"]] / 100

    dig_montage = mne.channels.make_dig_montage(nasion=fiducials["nasion"], lpa=fiducials["lpa"], rpa=fiducials["rpa"], hsp=head_points, coord_frame='head')

    mne_object.info.set_montage(dig_montage)



def plot_pos_ori(pos, ori, ax, label = "", c = "b"):

    # Plot positions
    ax.scatter(pos[:, 0], pos[:, 1], pos[:, 2], color=c, label=f'position {label}')

    # Plot orientations as arrows
    for i in range(len(pos)):
        x, y, z = pos[i]
        u, v, w = ori[i]
        
        ax.quiver(x, y, z, u, v, w, length=0.1, normalize=True, color=c, label=f'Orientation {label}' if i == 0 else "")
        # Simple representation of orientation using arrows (may need adjustments based on actual orientation representation)
        #ax.quiver(x, y, z, np.cos(yaw), np.sin(yaw), 0, length=0.02, color=c, label=f'Orientation {label}' if i == 0 else "")



class OPMSensorLayout:
    def __init__(self, label, depth, helmet_template:HelmetTemplate):
        self.label = label
        self.depth = depth
        self.helmet_template = helmet_template
        self.unit = self.helmet_template.unit
        
        self.make_sensor_layout()

    def make_sensor_layout(self):
        # Update template location given the depth measurement
        self.chan_pos = self.transform_template_depth()
        self.chan_ori = self.helmet_template.get_chs_ori(self.label)
    
    def transform_template_depth(self, len_sleeve:float = 0.0, offset:float = 0.0): #len_sleeve:float = 75/1000, offset:float = 13/1000
        template_ori = self.helmet_template.get_chs_ori(self.label)
        template_pos = self.helmet_template.get_chs_pos(self.label)
        
        # Create a new list to store the updated positions
        transformed_pos = []
        
        # Move template pos by measurement length in template ori direction
        for pos, ori, depth in zip(template_pos, template_ori, self.depth):
            # Update the position by adding the orientation scaled by the measurement
            new_pos = np.array(pos) + np.array(ori) * -(len_sleeve - (depth + offset))
            transformed_pos.append(new_pos)
        
        return np.array(transformed_pos).T

def update_OPM_pos(mne_object, df):    

    channels = df[df["sensor_type"] == "OPM"]
    coordinates = np.array(channels.loc[:, ["x", "y", "z"]]).squeeze()
    labels = channels["label"]

    for coor, label in zip(coordinates, labels):
        coor = coor / 100

        idx = None

        # Find the channel with the label in the info of the mne object
        for idx_tmp, ch in enumerate(mne_object.info["chs"]):
            mne_ch_name = ch["ch_name"]
            if mne_ch_name == label:
                idx = idx_tmp
                break

        # Update the location of that channel
        mne_object.info['chs'][idx]['loc'][:3] = coor

def vector_to_rotation_matrix(orientation_vector):
    """# Normalize the input orientation vector (which is the normal vector)
    O = orientation_vector / np.linalg.norm(orientation_vector)
    
    # Step 2: Choose an arbitrary vector that is not collinear with O
    # Here we use the x-axis unit vector [1, 0, 0] unless O is close to it.
    if np.allclose(O, [1, 0, 0]):  # If O is along the x-axis, use y-axis as arbitrary vector
        v1 = np.array([0, 1, 0])
    else:
        v1 = np.array([1, 0, 0])
    
    # Step 3: Compute E_X as the orthogonal projection of v1 onto the plane of O
    E_X = v1 - np.dot(v1, O) * O  # Remove the component of v1 in the direction of O
    E_X /= np.linalg.norm(E_X)  # Normalize E_X
    
    # Step 4: Compute E_Y as the cross product of O and E_X (to ensure orthogonality)
    E_Y = np.cross(O, E_X)
    
    # Construct the full 3x3 orientation matrix (each row is E_X, E_Y, O)
    orientation_matrix = np.vstack([E_X, E_Y, O])
    """

    rot = R.from_rotvec(orientation_vector, degrees=False)
    orientation_matrix = rot.as_matrix()
    print(orientation_matrix)
    
    return orientation_matrix

def update_OPM_ori(mne_object, sensor_layout:OPMSensorLayout):
    
    # Change sensor orientations
    ori_template_space = sensor_layout.chan_ori
    loc_template_space = sensor_layout.chan_pos
    labels_template = sensor_layout.label


    loc_digtised_tmp = []
    
    for label in labels_template:

        idx = None
        # Find the channel with the label in the info of the mne object
        for idx_tmp, ch in enumerate(mne_object.info["chs"]):
            mne_ch_name = ch["ch_name"]
            if mne_ch_name == label:
                idx = idx_tmp
                break

        loc_digtised_tmp.append(mne_object.info['chs'][idx]['loc'][:3])
    
    loc_digtised = np.array(loc_digtised_tmp).T

    rot, trans, Yf = rot3dfit(loc_template_space, loc_digtised) # moving from template to head space
    
    for ch in mne_object.info["chs"]:
        idx_template = labels_template.index(ch["ch_name"])
        
        # Get the template orientation (3D vector) for this channel
        template_ori_vector = ori_template_space[idx_template, :]

        # rotate and translate


        # Convert the orientation vector to a 3x3 rotation matrix
        template_ori_matrix = vector_to_rotation_matrix(template_ori_vector)

        # Apply the rotation
        ori_digtised_matrix = template_ori_matrix @ rot.T

        # Flatten and store the matrix in the 'loc' field (positions 3 to 11 for the 3x3 orientation matrix)
        ch['loc'][3:12] = ori_digtised_matrix.flatten()



if __name__ in "__main__":
    path = Path("/Volumes/untitled/opm_cerebell/20221003/SD/")
    opm_path = path / "20221003_151904_SD_opm_cerebell_passive_omission_raw.fif"
    raw = mne.io.read_raw(opm_path, preload=True)

    raw_old = raw.copy()
    points = pd.read_csv("/Users/au661930/Library/CloudStorage/OneDrive-Aarhusuniversitet/Dokumenter/project placement/OPM_lab/output/test1_digitisation.csv")

    depth_meas = [40/1000, 47/1000, 44/1000, 40/1000] # mm converted to meter (order = 3, 10, 16, 62)

    sensor_layout = OPMSensorLayout(
        label=["FL3", "FL10", "FL16", "FL62"], 
        depth=depth_meas,
        helmet_template=FL_alpha1_helmet
        )

    raw.pick(["00:01-BZ_CL", '00:02-BZ_CL', "00:03-BZ_CL", "00:04-BZ_CL"])

    mne.rename_channels(raw.info, {"00:01-BZ_CL" : "FL3", 
                                "00:02-BZ_CL" : "FL10", 
                                "00:03-BZ_CL" : "FL16", 
                                "00:04-BZ_CL" : "FL62"})
    
    
    add_dig_montage(raw, points)
    update_OPM_pos(raw, points)
    update_OPM_ori(raw, sensor_layout)

    
    kwargs = dict(eeg=False, coord_frame="meg", show_axes=True, verbose=True, dig = True)
    fig = plot_alignment(raw.info, meg=("sensors"), **kwargs)

    # For PyVista, you might want to add something like this if using interactive plots
    Plotter().show()

    """
    locations = []
    template_orientations = []

    for ch in raw.info["chs"]:
        locations.append(ch["loc"][:3])
        template_orientations.append(FL_alpha1_helmet.get_chs_ori([ch["ch_name"]])[0])
        
    print(template_orientations)
    # Create a 3D plot
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')


    plot_pos_ori(np.array(locations), template_orientations, ax)


    # Labels and legend
    ax.set_xlabel('X axis')
    ax.set_ylabel('Y axis')
    ax.set_zlabel('Z axis')
    ax.legend()

    plt.title('3D Plot of Template Positions and Orientations')
    plt.show()
        
    """