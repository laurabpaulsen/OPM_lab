import sys 
sys.path.append("OPM_lab")

from OPM_lab.sensor_locations import FL_alpha1_helmet, HelmetTemplate
import pandas as pd
from pathlib import Path
import mne
#from scipy.spatial.transform import Rotation as R # for conversion from eulers angles to rotation matrix
import numpy as np
import matplotlib.pyplot as plt
from pyvista import Plotter
from mne.transforms import Transform, _quat_to_affine, _fit_matched_points

def add_dig_montage(mne_object, df:pd.DataFrame):
    fiducials = {}

    for label in ["nasion", "lpa", "rpa"]:
        fid = df[df["label"] == label].loc[:, ["x", "y", "z"]]
        fiducials[label] = np.array(fid).squeeze() / 100  # converting to meter!

    head_points = df[df["label"] == "head"].loc[:, ["x", "y", "z"]] /100
    
    # DELETE THE TWO FOLLOWING LINES JUST FOR CHECKING
    OPMs = df[df["sensor_type"] == "OPM"].loc[:, ["x", "y", "z"]] /100 
    head_points = pd.concat([head_points, OPMs])

    dig_montage = mne.channels.make_dig_montage(nasion=fiducials["nasion"], lpa=fiducials["lpa"], rpa=fiducials["rpa"], hsp=head_points, coord_frame='head')

    mne_object.info.set_montage(dig_montage)

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



def plot_pos_ori(pos, ori, ax, label = "", c = "b"):

    # Plot positions
    ax.scatter(pos[0, :], pos[1, :], pos[2,:], color=c, label=f'position {label}')

    # Plot orientations as arrows
    for i in range(pos.shape[-1]):
        x, y, z = pos[:, i]
        u, v, w = ori[i]
        
        ax.quiver(x, y, z, u, v, w, length=0.01, normalize=True, color=c, label=f'Orientation {label}' if i == 0 else "")
        # Simple representation of orientation using arrows (may need adjustments based on actual orientation representation)
        #ax.quiver(x, y, z, np.cos(yaw), np.sin(yaw), 0, length=0.02, color=c, label=f'Orientation {label}' if i == 0 else "")

def plot_pos(pos, ax, label, c="yellow"):
    # Plot positions
    ax.scatter(pos[0, :], pos[1, :], pos[2,:], color=c, label=f'position {label}')

def vector_to_rotation_matrix(orientation_vector):
    # Normalize the input orientation vector (which is the normal vector)
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
    

    """rot = R.from_rotvec(orientation_vector, degrees=False)
    orientation_matrix = rot.as_matrix()"""
    
    return orientation_matrix

def add_sensor_layout_to_mne(mne_object, sensor_layout=OPMSensorLayout):
    for pos, ori, label in zip(sensor_layout.chan_pos, sensor_layout.chan_ori, sensor_layout.label):
        idx = None

        # Find the channel with the label in the info of the mne object
        for idx_tmp, ch in enumerate(mne_object.info["chs"]):
            mne_ch_name = ch["ch_name"]
            if mne_ch_name == label:
                idx = idx_tmp
                break

        # Update the location of that channel
        mne_object.info['chs'][idx]['loc'][:3] = pos

        ori_matrix = vector_to_rotation_matrix(ori)
        print(ori_matrix)
        ch['loc'][3:] = ori_matrix.flatten()


def get_device_to_head(mne_object, digitised_points, tol = 10):
    channels = digitised_points[digitised_points["sensor_type"] == "OPM"]
    sensors_head = np.array(channels.loc[:, ["x", "y", "z"]]).squeeze() / 100
    labels = channels["label"]

    sensors_device = []
    
    for label in labels:

        idx = None
        # Find the channel with the label in the info of the mne object
        for idx_tmp, ch in enumerate(mne_object.info["chs"]):
            mne_ch_name = ch["ch_name"]
            if mne_ch_name == label:
                idx = idx_tmp
                break

        sensors_device.append(mne_object.info['chs'][idx]['loc'][:3])

    sensors_device = np.array(sensors_device) 

    trans = _quat_to_affine(_fit_matched_points(sensors_device, sensors_head)[0])
    #trans = fit_matched_points(sensors_device, sensors_head, tol = tol)
    mne_object.info["dev_head_t"] = Transform(fro="meg", to="head", trans=trans)



if __name__ in "__main__":
    path = Path("/Volumes/untitled/opm_cerebell/20221003/SD/")
    opm_path = path / "20221003_151904_SD_opm_cerebell_passive_omission_raw.fif"
    raw = mne.io.read_raw(opm_path, preload=True)

    raw_old = raw.copy()
    points = pd.read_csv("/Users/au661930/Library/CloudStorage/OneDrive-Aarhusuniversitet/Dokumenter/project placement/OPM_lab/output/test1_digitisation.csv")


    raw.pick(["00:01-BZ_CL", '00:02-BZ_CL', "00:03-BZ_CL", "00:04-BZ_CL"])

    mne.rename_channels(raw.info, {"00:01-BZ_CL" : "FL3", 
                                    "00:02-BZ_CL" : "FL10", 
                                    "00:03-BZ_CL" : "FL16", 
                                    "00:04-BZ_CL" : "FL62"})

    depth_meas = [40/1000, 47/1000, 44/1000, 40/1000] # mm converted to meter (order = 3, 10, 16, 62)

    sensor_layout = OPMSensorLayout(
            label=["FL3", "FL10", "FL16", "FL62"], 
            depth=depth_meas,
            helmet_template=FL_alpha1_helmet
            ) 
   

    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')


    plot_pos_ori(FL_alpha1_helmet.chan_pos.T, FL_alpha1_helmet.chan_ori, ax=ax, label = "helmet template",)
    plot_pos_ori(sensor_layout.chan_pos.T, sensor_layout.chan_ori, ax=ax, c="red")

    head_points = points[points["label"] == "head"].loc[:, ["x", "y", "z"]]
    head_points = np.array(head_points).squeeze() / 100
    plot_pos(head_points.T, ax=ax, c="purple", label = "")

    add_dig_montage(raw, points)

    add_sensor_layout_to_mne(raw, sensor_layout)

    get_device_to_head(raw, points)
    print(raw.info["dev_head_t"])
    print("Distance from head origin to MEG origin: " + f'{1000 * np.linalg.norm(raw.info["dev_head_t"]["trans"][:3, 3]):.1f} mm')
    fig = mne.viz.plot_alignment(raw.info, meg=("sensors"), dig = True, coord_frame="head", verbose = True)  
    Plotter().show()