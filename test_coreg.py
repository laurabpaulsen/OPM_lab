import sys 
sys.path.append("OPM_lab")
from OPM_lab.sensor_position import OPMSensorLayout, FL_alpha1_helmet
from OPM_lab.mne_integration import add_device_to_head, add_dig_montage, add_sensor_layout
import pandas as pd
from pathlib import Path
import mne
from mne.utils._bunch import NamedInt
from pyvista import Plotter


if __name__ in "__main__":
    data_path = Path("/Volumes/untitled/opm_cerebell/20221003/001/")
    opm_path = data_path / "20221003_151904_SD_opm_cerebell_passive_omission_raw.fif"
    raw = mne.io.read_raw(opm_path, preload=True)

    raw_old = raw.copy()
    dig_path = Path(__file__).parent / "output"
    points = pd.read_csv(dig_path / "test1_digitisation.csv", names = ['sensor_type', 'label', 'x', 'y', 'z'])

    raw.pick(["00:01-BZ_CL", '00:02-BZ_CL', "00:03-BZ_CL", "00:04-BZ_CL"])

    mne.rename_channels(raw.info, {"00:01-BZ_CL" : "FL3", 
                                    "00:02-BZ_CL" : "FL10", 
                                    "00:03-BZ_CL" : "FL16", 
                                    "00:04-BZ_CL" : "FL62"})
    


    depth_meas = [40., 47., 44., 40.] # mm converted to meter (order = 3, 10, 16, 62)

    sensor_layout = OPMSensorLayout(
            label=["FL3", "FL10", "FL16", "FL62"], 
            depth=depth_meas,
            helmet_template=FL_alpha1_helmet,
            
            # delete this line, but useful for plotting as orientation of OPMs (default coil types) are difficult to see on alignment plot
            coil_type=NamedInt("SQ20950N", 3024)
            ) 
   
    
    add_dig_montage(raw, points)

    add_sensor_layout(raw, sensor_layout)

    print(f'updated coil type: {raw.info["chs"][0]["coil_type"]}')
    print(type(raw.info["chs"][0]["coil_type"]))

    add_device_to_head(raw, points)
    #print(raw.info["dev_head_t"])
    #print("Distance from head origin to MEG origin: " + f'{1000 * np.linalg.norm(raw.info["dev_head_t"]["trans"][:3, 3]):.1f} mm')
    fig = mne.viz.plot_alignment(raw.info, meg=("sensors"), dig = True, coord_frame="head", verbose = True)  
    Plotter().show()