from .sensor_position import OPMSensorLayout
from .utils import determine_conversion_factor
import pandas as pd
from mne.transforms import Transform, _quat_to_affine, _fit_matched_points
from mne.channels import make_dig_montage
import numpy as np


def add_dig_montage(mne_object, df: pd.DataFrame, unit:str = "m"):
    """
    Adds a digitised montage to the MNE object based on fiducial points and head shape.
    Args:
        mne_object: MNE raw or epochs object.
        df (pd.DataFrame): DataFrame with columns ["label", "x", "y", "z"].
        unit (str): Unit of the digitised points, can be "m", "cm" or "mm".
    """
    unit_coversion = determine_conversion_factor(unit, "m")
 
    required_labels = ["nasion", "lpa", "rpa"]
    if not set(required_labels).issubset(df["label"].unique()):
        raise ValueError(f"DataFrame must contain labels {required_labels}")

    fiducials = {
        label: df.loc[df["label"] == label, ["x", "y", "z"]].values.squeeze() / unit_coversion
        for label in required_labels
    }
    head_points = df[df["label"] == "head"].loc[:, ["x", "y", "z"]].values / unit_coversion

    # check if eeg channels are present in the digitised points
    eeg_channels = df[df["category"] == "EEG"]

    if eeg_channels.empty:
        print("No channels with category EEG found in the digitised points. Only fiducials and head shape will be used.")
        eeg_channel_pos = None
    else:
        eeg_channel_pos = {
            ch["label"]: ch[["x", "y", "z"]].values / unit_coversion
            for _, ch in eeg_channels.iterrows()
        }

    dig_montage = make_dig_montage(
        ch_pos=eeg_channel_pos,
        nasion=fiducials["nasion"],
        lpa=fiducials["lpa"],
        rpa=fiducials["rpa"],
        hsp=head_points,
        coord_frame="head"
    )

    mne_object.info.set_montage(dig_montage)


def add_sensor_layout(mne_object, sensor_layout: OPMSensorLayout):
    """
    Updates channel positions and orientations for MNE object based on a sensor layout.
    Args:
        mne_object: MNE object, for example Raw.
        sensor_layout: A layout object containing channel positions, orientations, labels and coil type.
    """

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
        mne_object.info["chs"][idx]["loc"][3:] = ori.flatten()
        mne_object.info["chs"][idx]["coil_type"] = sensor_layout.coil_type


def add_device_to_head(mne_object, digitised_points, unit="m"):
    """
    Adds a device-to-head transformation to the MNE object.
    Args:
        mne_object: MNE object, such as raw.
        digitised_points (pd.DataFrame): DataFrame with device sensor positions and labels.
        unit (str): Unit of the digitised points, can be "m", "cm" or "mm".
    """
    # get the unit of the sensor positions in the mne_object
    unit_coversion = determine_conversion_factor(unit, "m")

    channels = digitised_points[digitised_points["sensor_type"] == "OPM"]
    sensors_head = channels.loc[:, ["x", "y", "z"]].values / unit_coversion
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
