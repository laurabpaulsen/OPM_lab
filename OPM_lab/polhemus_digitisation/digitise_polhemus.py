import serial
from digitising import *


if __name__ in "__main__":

    fiducials = ["LA", "RA", "NASION"]
    OPM_sensors = ["1", "2", "3", "4"]
    EEG_sesors = ["Fp1", "Fp2"]

    stylus_reciever = 0
    head_reference = 1

    # initialize serial object (adjust 'COM_PORT' and 'BAUD_RATE' as per your configuration)
    serialobj = serial.Serial(
        port='/dev/cu.usbserial-110',   # Port name
        baudrate=115200,             # Baud rate
        stopbits=serial.STOPBITS_ONE, # Stop bits (1 stop bit)
        parity=serial.PARITY_NONE,    # No parity
        bytesize=serial.EIGHTBITS,    # 8 data bits (equivalent to default setting)
        rtscts=False,                 # No hardware flow control (RTS/CTS)
        timeout=1,                    # Read timeout in seconds (adjust as needed)
        write_timeout=1,              # Write timeout in seconds (optional)
        xonxoff=False                 # No software flow control (XON/XOFF)
    )

    set_factory_software_defaults(serialobj)
    clear_old_data(serialobj)
    output_cm(serialobj)
    n_recievers = get_n_recievers(serialobj)
    
    if n_recievers != 2:
        print("Make sure both recievers are connected - stylus in 1 and head reference in 2")

    fiducial_coordinates = mark_sensors(serialobj, n_recievers, fiducials, sensor_type= "fiducials")
    OPM_coordinates_tmp = mark_sensors(serialobj, n_recievers, OPM_sensors, sensor_type="OPM", prev_digitised = {"fiducials": fiducial_coordinates})
    #EEG_coordinates = mark_sensors(serialobj, n_recievers, EEG_sesors, sensor_type="EEG")

    #scalp_surface = scan_scalp_surface(serialobj, n_recievers=n_recievers)
    #print(scalp_surface)