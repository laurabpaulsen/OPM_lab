from .sensor_position import OPMSensorLayout
import pandas as pd
from mne.transforms import Transform, _quat_to_affine, _fit_matched_points
from mne.channels import make_dig_montage
from scipy.spatial.transform import (
    Rotation as R,
)  # for conversion from eulers angles to rotation matrix
import numpy as np


def add_dig_montage(mne_object, df: pd.DataFrame):
    """
    Adds a digitised montage to the MNE object based on fiducial points and head shape.
    Args:
        mne_object: MNE raw or epochs object.
        df (pd.DataFrame): DataFrame with columns ["label", "x", "y", "z"].
    """
    required_labels = ["nasion", "lpa", "rpa"]
    if not set(required_labels).issubset(df["label"].unique()):
        raise ValueError(f"DataFrame must contain labels {required_labels}")

    fiducials = {
        label: df.loc[df["label"] == label, ["x", "y", "z"]].values.squeeze() / 100
        for label in required_labels
    }
    head_points = df[df["label"] == "head"].loc[:, ["x", "y", "z"]].values / 100

    dig_montage = make_dig_montage(
        nasion=fiducials["nasion"],
        lpa=fiducials["lpa"],
        rpa=fiducials["rpa"],
        hsp=head_points,
        coord_frame="head",
    )

    mne_object.info.set_montage(dig_montage)


def add_sensor_layout(mne_object, sensor_layout: OPMSensorLayout):
    """
    Updates channel positions and orientations for MNE object based on a sensor layout.
    Args:
        mne_object: MNE object, for example Raw.
        sensor_layout: A layout object containing channel positions, orientations, labels and coil type.
    """

    def vector_to_rotation_matrix(orientation_vector):
        """
        Converts a rotation vector to a rotation matrix. Current implementation is tentative.
        """
        
        """
        CHATGPT SOLUTION....
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

        OTHER IDEAS

        rot = R.from_rotvec(orientation_vector, degrees=False) # not sure if the fieldline template orientation is a eulers
        #rot = R.from_euler("xyz", orientation_vector, degrees=False) # not sure if the fieldline template orientation is a rotvec
        orientation_matrix = rot.as_matrix() # not sure this converts it to the correct type of matrix
        """
        
        raise NotImplementedError("Vector-to-matrix conversion needs validation")

    for pos, ori, label in zip(
        sensor_layout.chan_pos, sensor_layout.chan_ori, sensor_layout.label
    ):
        idx = next(
            (
                idx
                for idx, ch in enumerate(mne_object.info["chs"])
                if ch["ch_name"] == label
            ),
            None,
        )
        if idx is None:
            print(f"Warning: Channel {label} not found in MNE object")
            continue

        mne_object.info["chs"][idx]["loc"][:3] = pos
        ori_matrix = vector_to_rotation_matrix(ori)
        mne_object.info["chs"][idx]["loc"][3:] = ori_matrix.flatten()
        mne_object.info["chs"][idx]["coil_type"] = sensor_layout.coil_type


def add_device_to_head(mne_object, digitised_points):
    """
    Adds a device-to-head transformation to the MNE object.
    Args:
        mne_object: MNE object, such as raw.
        digitised_points (pd.DataFrame): DataFrame with device sensor positions and labels.
    """
    channels = digitised_points[digitised_points["sensor_type"] == "OPM"]
    sensors_head = channels.loc[:, ["x", "y", "z"]].values / 100
    labels = channels["label"]

    sensors_device = []
    for label in labels:
        idx = next(
            (
                idx
                for idx, ch in enumerate(mne_object.info["chs"])
                if ch["ch_name"] == label
            ),
            None,
        )
        if idx is None:
            print(f"Warning: Channel {label} not found in MNE object")
            continue
        sensors_device.append(mne_object.info["chs"][idx]["loc"][:3])

    trans = _quat_to_affine(
        _fit_matched_points(np.array(sensors_device), sensors_head)[0]
    )
    mne_object.info["dev_head_t"] = Transform(fro="meg", to="head", trans=trans)
