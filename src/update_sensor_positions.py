
import mne
import time
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

from OPM_lab.sensor_locations import FL_alpha1_helmet
from scipy.spatial.transform import Rotation as R # for conversion from eulers angles to rotation matrix


print(np.min(FL_alpha1_helmet.chan_ori), np.max(FL_alpha1_helmet.chan_ori))


def add_dig_montage(df, mne_object):
    fiducials = {}

    for label in ["nasion", "lpa", "rpa"]:
        fid = df[df["label"] == label].loc[:, ["x", "y", "z"]]
        fiducials[label] = np.array(fid).squeeze() / 100  # converting to meters!

    head_points = df[df["label"] == "head"].loc[:, ["x", "y", "z"]] / 100

    dig_montage = mne.channels.make_dig_montage(nasion=fiducials["nasion"], lpa=fiducials["lpa"], rpa=fiducials["rpa"], hsp=head_points, coord_frame='head')

    mne_object.info.set_montage(dig_montage)


def update_OPM_pos_ori(df, mne_object, fieldline_template=FL_alpha1_helmet):    

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

        # Change sensor orientations
        channel_orientation = fieldline_template.get_chs_ori([label])[0]

        # Assuming the orientation is provided as Euler angles, convert to a rotation matrix
        # Specify the order of Euler angles according to how they are represented (e.g., 'xyz')
        rotation = R.from_rotvec(channel_orientation) 
        rotation_matrix = rotation.as_matrix()


        # Flatten the rotation matrix and update the location field in the MNE object
        mne_object.info['chs'][idx]['loc'][3:12] = rotation_matrix.flatten()



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
    

    add_dig_montage(points, raw)
    update_OPM_pos_ori(points, raw)

    
    


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