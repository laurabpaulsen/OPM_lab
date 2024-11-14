import sys
import csv
from pathlib import Path
current_file = Path(__file__).resolve()
parent_directory = current_file.parents[1]
sys.path.append(str(parent_directory))
from OPM_lab.sensor_position import FL_alpha1_helmet, HelmetTemplate
import matplotlib.pyplot as plt
from matplotlib import gridspec

def _input(message, input_type=str):
    while True:
        try:
            return input_type(input(message))
        except ValueError:
            pass

def setup_plot():
    # Initialize plot with the figure and axis
    fig = plt.figure(figsize=(15, 6))
    ax = fig.add_subplot(111, projection="3d")
    return fig, ax

def get_measurements(sensors, template: HelmetTemplate):
    measurements = {}
    fig, ax = setup_plot()

    for sensor in sensors:
        # Clear previous plot data
        ax.cla()

        # Plot the helmet template positions
        for pos in template.chan_pos:
            ax.scatter(*pos, c="lightblue", alpha=0.7, s=30, marker="s")

        # Plot all sensors
        for pos in template.get_chs_pos(sensors):
            ax.scatter(*pos, c="blue", label="all sensors", alpha=0.6, s=8)

        # Focus on the current sensor
        focus = template.get_chs_pos([sensor])[0]
        ax.scatter(*focus, c="red", label="focused sensor", alpha=1, s=20)

        # Update the plot and pause to allow user interaction
        plt.draw()
        plt.pause(0.1)  # Allow a brief pause for the plot to update

        # Collect input for the current sensor
        measurements[sensor] = _input(f"Depth measurement for {sensor}: ")

    # close the plot after all inputs are collected
    plt.close()

    return measurements

def save_measurements_to_csv(measurements, output_path):
    csv_file = output_path / "depth_measurements.csv"

    
    with open(csv_file, mode="w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["sensor", "depth"])
        
        for sensor, depth in measurements.items():
            writer.writerow([sensor, depth])
    print(f"Measurements saved to {csv_file}")


if __name__ == "__main__":

    participant = "001"
    output_path = Path(__file__).parents[1] / "output" / participant
    
    if not output_path.exists():
        output_path.mkdir(parents=True)

    sensor_numbers = [67, 10, 78]  # Define sensor numbers
    OPM_sensors = [f"FL{number}" for number in sensor_numbers]
    measurements = get_measurements(OPM_sensors, FL_alpha1_helmet)

    # save measurements to a CSV file
    save_measurements_to_csv(measurements, output_path)

