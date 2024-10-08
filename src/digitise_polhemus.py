import serial
import csv

# for local imports
import sys
from pathlib import Path
current_file = Path(__file__).resolve()
parent_directory = current_file.parent.parent 
sys.path.append(str(parent_directory)) 
from OPM_lab.digitising import *


def get_participant_information():
    print("Please enter participant information:")
    
    participant_info = {}

    participant_info['participant_id'] = input("Participant ID: ")
    participant_info['age'] = int(input("Age: "))
    participant_info['gender'] = input("Gender: ")

    return participant_info


def input_depth_measurement(OPMs):
    print("Please enter depth measurements of OPMs using caliper in milimeters")
    
    depth_measurements = {}
    for OPM in OPMs:
        depth_measurements['OPM'] = input(f"Caliper measurement for {OPM}: ")

    return depth_measurements

if __name__ == "__main__":
    # Get participant information
    participant_info = get_participant_information()
    output_path = Path(__file__).parents[1] / "output"

    if not output_path.exists():
        output_path.mkdir(parents=True)

    # Sensor names
    fiducials = ["LA", "RA", "NASION"]
    OPM_sensors = ["FL52", "FL61", "FL92", "FL99"]
    EEG_sensors = ["fake", "fake"]

    scalp_surface_size = 60

    # Receiver configuration
    stylus_receiver = 0
    head_reference = 1

    # initialize serial object
    serialobj = serial.Serial(
        port='/dev/cu.usbserial-110',   # Port name (adjust as necessary)
        baudrate=115200,                # Baud rate
        stopbits=serial.STOPBITS_ONE,   # Stop bits (1 stop bit)
        parity=serial.PARITY_NONE,      # No parity
        bytesize=serial.EIGHTBITS,      # 8 data bits
        rtscts=False,                   # No hardware flow control (RTS/CTS)
        timeout=1,                      # Read timeout in seconds (adjust as needed)
        write_timeout=1,                # Write timeout in seconds (optional)
        xonxoff=False                   # No software flow control (XON/XOFF)
    )

    # Configure and prepare for digitization
    set_factory_software_defaults(serialobj)
    clear_old_data(serialobj)
    output_cm(serialobj)
    n_receivers = get_n_receivers(serialobj)
    
    if n_receivers != 2:
        print("Make sure both receivers are connected - stylus in port 1 and head reference in port 2")
        exit()  # Exit script if receivers are not properly connected

    already_digitised = {}

    for sensor_labels, sensor_type in zip([["head"]*scalp_surface_size, fiducials, OPM_sensors, EEG_sensors], ["head_shape", "fiducials", "OPM", "EEG"]):
        clear_old_data(serialobj) # to make sure any "residue" button presses from previously does not interfere

        if sensor_type == "head_shape":
            coordinates = mark_headshape(serialobj, n_receivers, scalp_surface_size=scalp_surface_size)
        
        else:
            coordinates = mark_sensors(serialobj, n_receivers, sensor_labels, sensor_type=sensor_type, prev_digitised=already_digitised)
        
        already_digitised[sensor_type] = coordinates
        
        # save coordinates to CSV file (append mode 'a')
        with open(output_path / f'{participant_info["participant_id"]}_digitisation.csv', 'a', newline='') as csvfile:
            writer = csv.writer(csvfile)
            
            file_exists = (output_path / f'{participant_info["participant_id"]}_digitisation.csv').exists()

            # only write the header if the file doesn't already exist
            if not file_exists:
                writer.writerow(['sensor_type', 'label', 'x', 'y', 'z'])
            
            # Write sensor data to the file
            for idx, label in enumerate(sensor_labels):
                writer.writerow([sensor_type, label, coordinates[idx, 0], coordinates[idx, 1], coordinates[idx, 2]])


    # get depth measurements for OPM 
    # NOTE: NOT TESTED YET
    depth_measurements = input_depth_measurement()
    with open(output_path / f'{participant_info["participant_id"]}_depthmeas.csv', 'a', newline='') as csvfile:
        writer = csv.writer(csvfile)
            
        writer.writerow(['sensor_type', 'label', 'depth'])
            
        # Write sensor data to the file
        for sens, depth in depth_measurements.items():
            writer.writerow(["OPM", sens, depth])
    