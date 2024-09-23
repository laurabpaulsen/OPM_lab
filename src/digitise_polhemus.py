import serial
import sys
sys.path.append("..")
from OPM_lab.digitising import *
import csv

def get_participant_information():
    print("Please enter participant information:")
    
    participant_info = {}

    participant_info['participant_id'] = input("Participant ID: ")
    participant_info['age'] = int(input("Age: "))
    participant_info['gender'] = input("Gender: ")

    return participant_info

if __name__ == "__main__":
    # Get participant information
    participant_info = get_participant_information()

    # Sensor names
    fiducials = ["LA", "RA", "NASION"]
    OPM_sensors = ["1", "2", "3", "4"]
    EEG_sensors = ["Fp1", "Fp2"]

    # Receiver configuration
    stylus_receiver = 0
    head_reference = 1

    # Initialize serial object
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
    print(n_receivers)
    
    if n_receivers != 2:
        print("Make sure both receivers are connected - stylus in 1 and head reference in 2")
        exit()  # Exit script if receivers are not properly connected


    for sensor_labels, sensor_type in zip([fiducials, OPM_sensors, EEG_sensors], ["fiducials", "OPM", "EEG"]):
        coordinates = mark_sensors(serialobj, n_receivers, sensor_labels, sensor_type=sensor_type)
    
        # save coordinates to CSV file
        with open(f'{participant_info["participant_id"]}_{sensor_type}.csv', 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['label', 'x', 'y', 'z'])
            for idx, fiducial in enumerate(sensor_labels):
                writer.writerow([fiducial, coordinates[idx, 0], coordinates[idx, 1], coordinates[idx, 2]])