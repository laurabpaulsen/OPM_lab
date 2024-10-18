
import serial
import time
import numpy as np


class FastrakConnector:
    def __init__(self, usb_port:str, stylus_receiver = 0, head_reference = 1, data_length = 47):
        """
        A class to interface with the Polhemus FASTRAK system.
        
        Args:
            usb_port (str): The USB port to which the Polhemus FASTRAK is connected.
            stylus_receiver (int): The receiver port number for the stylus (default is 0).
            head_reference (int): The receiver port number for the head reference (default is 1).
            data_length (int): The expected length of data for each receiver reading.

        Methods:
            n_receivers(): Queries the number of active receivers.
            set_factory_software_defaults(): Resets the device to factory defaults.
            clear_old_data(): Clears outdated data from the serial buffer.
            output_metric(): Sets the measurement units to metric.
            prepare_for_digitisation(): Prepares the device for digitisation use.
            get_position_relative_to_head_receiver(): Computes the position from the stylus relative to the head receiver.
        """
        self.stylus_receiver = stylus_receiver
        self.head_reference = head_reference
        self.data_length = data_length

        # initialize serial object
        self.serialobj = serial.Serial(
            port=usb_port,                  # Port name (adjust as necessary)
            baudrate=115200,                # Baud rate
            stopbits=serial.STOPBITS_ONE,   # Stop bits (1 stop bit)
            parity=serial.PARITY_NONE,      # No parity
            bytesize=serial.EIGHTBITS,      # 8 data bits
            rtscts=False,                   # No hardware flow control 
            timeout=1,                      # Read timeout in seconds 
            write_timeout=1,                # Write timeout in seconds 
            xonxoff=False                   # No software flow control
        )

    def send_serial_command(self, command: bytes, sleep_time = 0.1):
        try:
            self.serialobj.write(command)
            time.sleep(sleep_time) 
        except serial.SerialTimeoutException:
            print("Serial write timeout occurred.")
        except serial.SerialException as e:
            print(f"Serial communication error: {e}")


    def n_receivers(self):
        self.send_serial_command(b'P')  # Send 'P' command to request number of probes

        # Initialize the number of receivers
        self.n_receivers = 0

        # Check for available data in the serial buffer
        while self.serialobj.in_waiting > 0:
            # Read one line of data (until newline character) from the buffer
            line = self.serialobj.readline().decode().strip()  # Read and decode a single line
            
            if line:  # If the line is not empty
                self.n_receivers += 1  # Increment receiver count

    def set_factory_software_defaults(self):
        """
        Resets the device to its factory software defaults by sending the appropriate command.
        """
        self.send_serial_command(b'W')  # Send 'W' command


    def clear_old_data(self):
        """
        Checks if there are bytes waiting in the buffer. If so it reads and discards. 
        """
        while self.serialobj.in_waiting > 0:
            self.serialobj.read(self.serialobj.in_waiting) 


    def output_metric(self):
        """
        Changes the output to centimeters instead of inches
        """
        self.send_serial_command(b'u')  # send 'u' command to set metric units

    def prepare_for_digitisation(self):
        self.set_factory_software_defaults()
        self.clear_old_data()
        self.output_metric()
        self.n_receivers()

        if self.n_receivers != 2:
            print("Make sure both receivers are connected - stylus in port 1 and head reference in port 2")


    def get_position_relative_to_head_receiver(self):
        # wait for all data from the receivers to arrive in the buffer
        while self.serialobj.in_waiting < self.n_receivers * self.data_length:
            pass  
        
        # Convert ASCII data into numbers and store in sensor_data array
        sensor_data = np.zeros((7, self.n_receivers))
            
        for j in range(self.n_receivers):
            ftstring = self.serialobj.readline().decode().strip()
            header, x, y, z, azimuth, elevation, roll = ftformat(ftstring)

            sensor_data[0, j] = header
            sensor_data[1, j] = x
            sensor_data[2, j] = y
            sensor_data[3, j] = z
            sensor_data[4, j] = azimuth
            sensor_data[5, j] = elevation            
            sensor_data[6, j] = roll

        # Get sensor position relative to head reference
        sensor_position = rotate_and_translate(
            sensor_data[1, self.head_reference],
            sensor_data[2, self.head_reference],
            sensor_data[3, self.head_reference],
            sensor_data[4, self.head_reference],
            sensor_data[5, self.head_reference],
            sensor_data[6, self.head_reference],
            sensor_data[1, self.stylus_receiver],
            sensor_data[2, self.stylus_receiver],
            sensor_data[3, self.stylus_receiver]
            )

        return sensor_data, sensor_position[:3]


def rotate_and_translate(xref, yref, zref, azi, ele, rol, xraw, yraw, zraw):
    # Convert angles to radians
    azi = -np.deg2rad(azi)
    ele = -np.deg2rad(ele)
    rol = -np.deg2rad(rol)
    
    # Rotation matrix around x-axis (roll)
    rx = np.array([
        [1, 0,          0,         0],
        [0, np.cos(rol), np.sin(rol), 0],
        [0, -np.sin(rol), np.cos(rol), 0],
        [0, 0,          0,         1]
    ])
    
    # Rotation matrix around y-axis (elevation)
    ry = np.array([
        [np.cos(ele),  0, -np.sin(ele), 0],
        [0,           1, 0,            0],
        [np.sin(ele),  0, np.cos(ele),  0],
        [0,           0, 0,            1]
    ])
    
    # Rotation matrix around z-axis (azimuth)
    rz = np.array([
        [np.cos(azi), np.sin(azi), 0, 0],
        [-np.sin(azi), np.cos(azi), 0, 0],
        [0,           0,           1, 0],
        [0,           0,           0, 1]
    ])
    
    # Translation matrix
    tm = np.array([
        [1, 0, 0, -xref],
        [0, 1, 0, -yref],
        [0, 0, 1, -zref],
        [0, 0, 0, 1]
    ])
    
    # Raw data as a 4x1 matrix (homogeneous coordinates)
    xyzraw = np.array([xraw, yraw, zraw, 1])

    # Translate the raw data
    xyzt = np.dot(tm, xyzraw)

    # Apply inverse rotations to align the point with the reference frame
    xyz = np.dot(rz.T, xyzt)
    xyz = np.dot(ry.T, xyz)
    xyz = np.dot(rx.T, xyz)

    # Return the corrected x, y, z coordinates
    return xyz[:3]  # Only return the 3D coordinates (ignore the 4th element)

def ftformat(fastdata):
    # Extract specific character slices and convert them to appropriate types
    header = int(fastdata[0:2].strip())  # Characters 1-2, stripped of whitespace, and converted to integer
    x = float(fastdata[3:10].strip())    # Characters 4-10, converted to float
    y = float(fastdata[10:17].strip())   # Characters 11-17, converted to float
    z = float(fastdata[17:24].strip())   # Characters 18-24, converted to float
    azimuth = float(fastdata[24:31].strip())   # Characters 25-31, converted to float
    elevation = float(fastdata[31:38].strip()) # Characters 32-38, converted to float
    roll = float(fastdata[38:46].strip())      # Characters 39-46, converted to float

    # Return the parsed values
    return header, x, y, z, azimuth, elevation, roll

