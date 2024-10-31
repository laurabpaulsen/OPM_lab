"""

"""

# for local imports
import sys
from pathlib import Path

# make sure to append path to OPM_lab
current_file = Path(__file__).resolve()
parent_directory = current_file.parent.parent 
sys.path.append(str(parent_directory)) 
from OPM_lab.digitise import Digitiser, FastrakConnector


def get_participant_information():
    print("Please enter participant information:")
    
    participant_info = {}

    participant_info['participant_id'] = input("Participant ID: ")

    return participant_info


if __name__ == "__main__":
    participant_info = get_participant_information()
    output_path = Path(__file__).parents[1] / "output"

    if not output_path.exists():
        output_path.mkdir(parents=True)

    fiducials = ["lpa", "rpa", "nasion"]
    OPM_sensors = ["FL52", "FL61", "FL92", "FL99"]
    EEG_sensors = ["Fp1", "Fp2"]

    head_surface_size = 60

    connector = FastrakConnector(usb_port='/dev/cu.usbserial-110')
    connector.prepare_for_digitisation()

    digitiser = Digitiser(connector=connector)
    
    digitiser.add(category="fiducials", labels=fiducials, dig_type="single")
    digitiser.add(category="OPM", labels=OPM_sensors, dig_type="single")
    digitiser.add(category="EEG", labels=EEG_sensors, dig_type="single")
    digitiser.add(category="head", n_points=head_surface_size, dig_type="continuous")

    digitiser.run_digitisation()

    digitiser.save_digitisation(output_path = output_path / f'{participant_info["participant_id"]}_digitisation.csv')