import sys
from pathlib import Path
current_file = Path(__file__).resolve()
parent_directory = current_file.parent.parent 
sys.path.append(str(parent_directory)) 
from OPM_lab.digtise.digitising import Digitiser
from OPM_lab.digtise.fastrak_connector import FastrakConnector

if __name__ == "__main__":
    output_path = Path(__file__).parents[1] / "output"

    if not output_path.exists():
        output_path.mkdir(parents=True)

    fiducials = ['A1', 'A2', 'A3', 'A4', 'A5', 'A6', 'A7', 'A8', 'B1', 'B2', 'B3', 'B4', 'B5', 'B6', 'B7', 'B8', 'B9']
    surface_size = 200

    connector = FastrakConnector(usb_port='/dev/cu.usbserial-110')
    connector.prepare_for_digitisation()

    digitiser = Digitiser(connector=connector)
    
    digitiser.add(category="fiducials", labels=fiducials, dig_type="single")
    digitiser.add(category="helmet", n_points=surface_size, dig_type="continuous")

    digitiser.run_digitisation()

    digitiser.save_digitisation(output_path = output_path / 'helmet_digitisation.csv')