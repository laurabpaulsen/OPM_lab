# for local imports
import sys
from pathlib import Path
from pyvista import Plotter
current_file = Path(__file__).resolve()
parent_directory = current_file.parents[1]
sys.path.append(str(parent_directory)) 
from OPM_lab.mne_integration import add_dig_montage, add_device_to_head, add_sensor_layout
from OPM_lab.sensor_position import OPMSensorLayout, FL_alpha1_helmet

from mne.viz import plot_alignment
from mne.utils._bunch import NamedInt
import mne
import pandas as pd

if __name__ in "__main__":
    data_path = Path("/Volumes/untitled/opm_cerebell/20221003/001/")
    opm_path = data_path / "20221003_151904_SD_opm_cerebell_passive_omission_raw.fif"
    raw = mne.io.read_raw(opm_path, preload=True)

    raw_old = raw.copy()
    dig_path = Path(__file__).parent / "output"
    points = pd.read_csv(dig_path / "test1_digitisation.csv")


    raw.pick(["00:01-BZ_CL", '00:02-BZ_CL', "00:03-BZ_CL", "00:04-BZ_CL"])

    mne.rename_channels(raw.info, {"00:01-BZ_CL" : "FL3", 
                                    "00:02-BZ_CL" : "FL10", 
                                    "00:03-BZ_CL" : "FL16", 
                                    "00:04-BZ_CL" : "FL62"})
    


    depth_meas = [40/1000, 47/1000, 44/1000, 40/1000] # mm converted to meter (order = 3, 10, 16, 62)

    sensor_layout = OPMSensorLayout(
            label=["FL3", "FL10", "FL16", "FL62"], 
            depth=depth_meas,
            helmet_template=FL_alpha1_helmet,
            
            # delete this line, but useful for plotting as orientation of OPMs (default coil types) are difficult to see on alignment plot
            coil_type=NamedInt("SQ20950N", 3024)
            ) 
   
    
    add_dig_montage(raw, points)
    add_sensor_layout(raw, sensor_layout)
    add_device_to_head(raw, points)

    fig = plot_alignment(raw.info, meg=("sensors"), dig = True, coord_frame="head", verbose = True)  
    Plotter().show()