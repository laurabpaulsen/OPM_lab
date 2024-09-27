import serial
import csv

# for local imports
import sys
from pathlib import Path
current_file = Path(__file__).resolve()
parent_directory = current_file.parent.parent 
sys.path.append(str(parent_directory)) 
from OPM_lab.digitising import *

if __name__ == "__main__":
    output_path = Path(__file__).parents[1] / "output"

    if not output_path.exists():
        output_path.mkdir(parents=True)

    fiducials = ['A1', 'A2', 'A3', 'A4', 'A5', 'A6', 'A7', 'A8', 'B1', 'B2', 'B3', 'B4', 'B5', 'B6', 'B7', 'B8', 'B9']
    scalp_surface_size = 200

    # receiver configuration
    stylus_receiver = 0
    head_reference = 1

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

    set_factory_software_defaults(serialobj)
    clear_old_data(serialobj)
    output_cm(serialobj)
    n_receivers = get_n_receivers(serialobj)
    
    if n_receivers != 2:
        print("Make sure both receivers are connected - stylus in port 1 and head reference in port 2")
        exit()  # Exit script if receivers are not properly connected

    already_digitised = {}

    for sensor_labels, sensor_type in zip([ ["helmet"]*scalp_surface_size, fiducials], ["helmet", "fiducials"]):
        clear_old_data(serialobj) # to make sure any "residue" button presses from previously does not interfere

        if sensor_type == "helmet":
            coordinates = mark_headshape(serialobj, n_receivers, scalp_surface_size=scalp_surface_size)
        
        else:
            coordinates = mark_sensors(serialobj, n_receivers, sensor_labels, sensor_type=sensor_type, prev_digitised=already_digitised, limit = 50)
        
        already_digitised[sensor_type] = coordinates
        
        # save coordinates to CSV file (append mode 'a')
        with open(output_path / f'helmet_digitisation.csv', 'a', newline='') as csvfile:        
            file_exists = (output_path / 'helmet_digitisation.csv').exists()
            writer = csv.writer(csvfile)
            # only write the header if the file doesn't already exist
            if not file_exists:
                writer.writerow(['sensor_type', 'label', 'x', 'y', 'z'])
            
            # Write sensor data to the file
            for idx, label in enumerate(sensor_labels):
                writer.writerow([sensor_type, label, coordinates[idx, 0], coordinates[idx, 1], coordinates[idx, 2]])

    