import time
import numpy as np
import matplotlib.pyplot as plt
import os
import math


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

def set_factory_software_defaults(serialobj):
    serialobj.write(b'W')  # Send 'W' command
    time.sleep(0.1)  # Pause for 100 milliseconds


def clear_old_data(serialobj):
    while serialobj.in_waiting > 0:  # Check if there are bytes waiting in the buffer
        serialobj.read(serialobj.in_waiting)  # Read and discard any available data


def output_cm(serialobj):
    # Set Fasttrack to output centimeters (metric)
    serialobj.write(b'u')  # Send 'u' command to set metric units
    time.sleep(0.1)  # Pause for 100 ms


def get_n_receivers(serialobj):
    serialobj.write(b'P')  # Send 'P' command to request number of probes
    time.sleep(0.1) 

    # Initialize the number of receivers
    n_recievers = 0

    # Check for available data in the serial buffer
    while serialobj.in_waiting > 0:
        # Read one line of data (until newline character) from the buffer
        line = serialobj.readline().decode().strip()  # Read and decode a single line
        
        if line:  # If the line is not empty
            n_recievers += 1  # Increment receiver count
            
    return n_recievers


def idx_of_next_point(distance, idx, limit = 30):
    # if stylus was clicked more than limit away from the head reference, the last point is undone
    if distance > limit:
        # Play a beep sound to indicate that data is ready
        os.system("afplay " + 'wrongbeep.wav')
        if idx == 0:
            return 0
        else:
            return idx - 1
    else: # moving on to the next
        os.system("afplay " + 'beep.wav')
        return idx + 1


def calculate_distance(point1, point2):
    # unpack the coordinates of point1 and point2
    x1, y1, z1 = point1
    x2, y2, z2 = point2
    
    return math.sqrt((x2 - x1)**2 + (y2 - y1)**2 + (z2 - z1)**2)
def update_message_box(ax, sensor_type, sensor_name, message):
    """Updates the message box with current sensor information."""
    ax.clear()
    ax.axis('off')  # Turn off axis lines
    ax.text(0.5, 0.4, f'{sensor_type}: {sensor_name}', va='center', ha='center', fontsize=14)
    ax.text(0.5, 0.8, message, va='center', ha='center', fontsize=14, color='red')

def add_point_3d(x, y, z, sensor_type, ax):
    """Add a point to the 3D plot."""
    if sensor_type == "OPM":
        color = "blue"
    elif sensor_type == "EEG":
        color = "orange"
    elif sensor_type == "fiducials":
        color = "green"

    ax.scatter(x, y, z, c=color, label=sensor_type)

def mark_sensors(serialobj, n_receivers, sensor_names, sensor_type="OPM", datalength=47, stylus=0, head_ref=1, prev_digitised=None):
    print('Pressing the stylus button more than 30 cm from the head reference will undo the point')

    sensor_position = np.zeros((len(sensor_names), 3))

    # set up the figure with two subplots: one for 3D plot, one for messages
    fig = plt.figure(figsize=(10, 6))
    
    # 3D plot subplot
    ax_3d = fig.add_subplot(121, projection='3d')
    ax_3d.set_xlabel('X')
    ax_3d.set_ylabel('Y')
    ax_3d.set_zlabel('Z')
    ax_3d.set_title(f'{sensor_type} Sensor Digitization')
    ax_3d.set_xlim([-30, 30])
    ax_3d.set_ylim([-30, 30])
    ax_3d.set_zlim([-30, 30])

    if prev_digitised:
        for sensor_type_tmp, points in prev_digitised.items():
            for point in points:
                add_point_3d(point[0], point[1], point[2], sensor_type=sensor_type_tmp, ax=ax_3d)

    # textbox subplot
    ax_text = fig.add_subplot(122)
    ax_text.axis('off')  # No axis for the text box


    idx = 0
    while idx < len(sensor_names):   
        update_message_box(ax_text, sensor_name=sensor_names[idx], sensor_type=sensor_type, message="Ready for digitization...") 
        plt.draw()
        
        # Wait for all data from the receivers to arrive in the buffer
        while serialobj.in_waiting < n_receivers * datalength:
            pass  
        
        # Convert ASCII data into numbers and store in sensor_data array
        sensor_data = np.zeros((7, n_receivers))
        
        for j in range(n_receivers):
            ftstring = serialobj.readline().decode().strip()
            header, x, y, z, azimuth, elevation, roll = ftformat(ftstring)

            sensor_data[0, j] = header
            sensor_data[1, j] = x
            sensor_data[2, j] = y
            sensor_data[3, j] = z
            sensor_data[4, j] = azimuth
            sensor_data[5, j] = elevation
            sensor_data[6, j] = roll

        # Get sensor position relative to head reference
        vector = rotate_and_translate(
            sensor_data[1, head_ref],
            sensor_data[2, head_ref],
            sensor_data[3, head_ref],
            sensor_data[4, head_ref],
            sensor_data[5, head_ref],
            sensor_data[6, head_ref],
            sensor_data[1, stylus],
            sensor_data[2, stylus],
            sensor_data[3, stylus]
        )
        
        sensor_position[idx] = vector[:3]  
        
        # Add the current point to the 3D plot
        add_point_3d(sensor_position[idx, 0], sensor_position[idx, 1], sensor_position[idx, 2], ax=ax_3d, sensor_type=sensor_type)

        # Checking if the click was more than 30 cm from the head reference
        point1 = (sensor_data[1, 0], sensor_data[2, 0], sensor_data[3, 0])
        point2 = (sensor_data[1, 1], sensor_data[2, 1], sensor_data[3, 1])

        idx = idx_of_next_point(calculate_distance(point1, point2), idx, limit=30)

        plt.pause(0.1)  # Pause briefly to update the plot
    
    plt.close()
    
    return sensor_position