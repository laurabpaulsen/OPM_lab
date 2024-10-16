from pathlib import Path
import mat73
import pickle as pkl
import sys

current_file = Path(__file__).resolve()
parent_directory = current_file.parent.parent 
sys.path.append(str(parent_directory)) 
from OPM_lab.sensor_locations import HelmetTemplate


data_dict = mat73.loadmat('/Users/au661930/Library/CloudStorage/OneDrive-Aarhusuniversitet/Dokumenter/project placement/OPM_lab/OPM_lab/template/fieldlinealpha1.mat')
data = data_dict["fieldlinealpha1"]

FL_template = HelmetTemplate(
    chan_pos=data["chanpos"],
    chan_ori=data["chanori"],
    label=[label[0] for label in data["label"]],
    fid_label=[label[0] for label in data["fid"]["label"]],
    fid_pos=data["fid"]["pos"],
    unit=data["unit"])

outpath = Path(__file__).parents[1] / "OPM_lab" / "template"
with open(outpath / "FL_alpha1_helmet.pkl", 'wb') as file:
    pkl.dump(FL_template, file)
