import serial
import csv

# for local imports
import sys
from pathlib import Path
current_file = Path(__file__).resolve()
parent_directory = current_file.parent.parent 
sys.path.append(str(parent_directory)) 
from OPM_lab.digitising import *

"""
key: fid, value: 
 {'label': [['A1'], ['A2'], ['A3'], ['A4'], ['A5'], ['A6'], ['A7'], ['A8'], ['B1'], ['B2'], ['B3'], ['B4'], ['B5'], ['B6'], ['B7'], ['B8'], ['B9']], 'pos': array([[ 0.08923,  0.06384, -0.034  ],
       [ 0.07301,  0.09659, -0.018  ],
       [ 0.04718,  0.12448, -0.009  ],
       [ 0.02051,  0.13806, -0.008  ],
       [-0.02051,  0.13806, -0.008  ],
       [-0.04718,  0.12448, -0.009  ],
       [-0.07301,  0.09659, -0.018  ],
       [-0.08923,  0.06384, -0.034  ],
       [ 0.09968, -0.01251, -0.05268],
       [ 0.09881,  0.0258 , -0.0139 ],
       [ 0.08515,  0.07538, -0.03885],
       [ 0.04198,  0.12871, -0.01391],
       [ 0.     ,  0.14151, -0.01391],
       [-0.04198,  0.12871, -0.01391],
       [-0.08515,  0.07538, -0.03885],
       [-0.09881,  0.0258 , -0.0139 ],
       [-0.09968, -0.01251, -0.05268]])}


"""

if __name__ == "__main__":
    output_path = Path(__file__).parents[1] / "output"

    if not output_path.exists():
        output_path.mkdir(parents=True)

    fiducials = ['A1', 'A2', 'A3', 'A4', 'A5', 'A6', 'A7', 'A8', 'B1', 'B2', 'B3', 'B4', 'B5', 'B6', 'B7', 'B8', 'B9']
    scalp_surface_size = 1000

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

    for sensor_labels, sensor_type in zip([["helmet"]*scalp_surface_size, fiducials], ["helmet", "fiducials"]):
        clear_old_data(serialobj) # to make sure any "residue" button presses from previously does not interfere

        if sensor_type == "helmet":
            coordinates = mark_headshape(serialobj, n_receivers, scalp_surface_size=scalp_surface_size)
        
        else:
            coordinates = mark_sensors(serialobj, n_receivers, sensor_labels, sensor_type=sensor_type, prev_digitised=already_digitised)
        
        already_digitised[sensor_type] = coordinates
        
        # save coordinates to CSV file (append mode 'a')
        with open(output_path / f'helmet_digitisation.csv', 'a', newline='') as csvfile:
            writer = csv.writer(csvfile)
            
            file_exists = (output_path / 'helmet_digitisation.csv').exists()

            # only write the header if the file doesn't already exist
            if not file_exists:
                writer.writerow(['sensor_type', 'label', 'x', 'y', 'z'])
            
            # Write sensor data to the file
            for idx, label in enumerate(sensor_labels):
                writer.writerow([sensor_type, label, coordinates[idx, 0], coordinates[idx, 1], coordinates[idx, 2]])

    