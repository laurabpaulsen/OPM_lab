import sys
from pathlib import Path

current_file = Path(__file__).resolve()
parent_directory = current_file.parent.parent
sys.path.append(str(parent_directory))
from OPM_lab.digitising import Digitiser
from OPM_lab.fastrak_connector import FastrakConnector


if __name__ == "__main__":
    # Get participant information
    output_path = Path(__file__).parents[1] / "output"

    if not output_path.exists():
        output_path.mkdir(parents=True)

    # Sensor names
    fiducials = ["lpa", "rpa", "nasion"]
    OPM_sensors = ["FL52", "FL61", "FL92", "FL99"]
    EEG_sensors = ["fake", "fake"]
    helmet_fiducials = [
        "A1",
        "A2",
        "A3",
        "A4",
        "A5",
        "A6",
        "A7",
        "A8",
        "B1",
        "B2",
        "B3",
        "B4",
        "B5",
        "B6",
        "B7",
        "B8",
        "B9",
    ]

    scalp_surface_size = 40

    connector = FastrakConnector(usb_port="/dev/cu.usbserial-110")
    connector.prepare_for_digitisation()

    digitiser = Digitiser(connector=connector)

    digitiser.add(category="fiducials", labels=fiducials, dig_type="single")
    digitiser.add(category="OPM", labels=OPM_sensors, dig_type="single")
    digitiser.add(
        category="helmet_fiducials", labels=helmet_fiducials, dig_type="single"
    )
    digitiser.add(category="head", n_points=scalp_surface_size, dig_type="continuous")

    digitiser.run_digitisation()

    digitiser.save_digitisation(output_path=output_path / "test_digitisation.csv")
