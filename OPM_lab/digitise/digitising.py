import matplotlib.pyplot as plt
from matplotlib import gridspec
import os
import math
import pandas as pd
from pathlib import Path
from .fastrak_connector import FastrakConnector
from ..sensor_position import HelmetTemplate

BASE_DIR = Path(__file__).resolve().parents[1]
SOUND_DIR = BASE_DIR / "soundfiles"



class DigitisationPlotter:
    def __init__(self, helmet_template:HelmetTemplate, set_axes_limits:bool=True):
        self.fig, self.ax_dig, self.ax_helmet, self.ax_text = self.setup_figure(set_axes_limits)
        self.helmet_template = helmet_template

    import matplotlib.pyplot as plt


    def setup_figure(self, set_axes_limits=True):
        # Set up the figure with a GridSpec layout to better control subplot positions
        fig = plt.figure(figsize=(15, 6))
        gs = gridspec.GridSpec(1, 3, width_ratios=[1, 1, 0.3], wspace=0.4)  # Adjust width_ratios and wspace for spacing

        # 3D plot subplot for digitised points
        ax_dig = fig.add_subplot(gs[0], projection="3d")
        ax_dig.set_xlabel("X")
        ax_dig.set_ylabel("Y")
        ax_dig.set_zlabel("Z")
        ax_dig.set_title("Points Digitised")
        if set_axes_limits:
            ax_dig.set_xlim([-30, 30])
            ax_dig.set_ylim([-30, 30])
            ax_dig.set_zlim([-30, 30])

        # 3D plot subplot for OPM helmet template
        ax_helmet = fig.add_subplot(gs[1], projection="3d")
        ax_helmet.set_xlabel("X")
        ax_helmet.set_ylabel("Y")
        ax_helmet.set_zlabel("Z")
        ax_helmet.set_title("OPM Helmet Template")


        # Textbox subplot with spacing for messages
        ax_text = fig.add_subplot(gs[2])
        ax_text.axis("off")

        return fig, ax_dig, ax_helmet, ax_text

    
    
    def helmet_plot(self, marked_sensors = list[str], focused_sensor:str = None):
        for pos in self.helmet_template.chan_pos:
            self.ax_helmet.scatter(*pos, c="lightblue", label="all sensors", alpha=0.7, s=30, marker="s")
        
        for pos in self.helmet_template.get_chs_pos(marked_sensors):
            self.ax_helmet.scatter(*pos, c="blue", label="all sensors", alpha=0.6, s=8)
        
        if isinstance(focused_sensor, str): 
            focus = self.helmet_template.get_chs_pos([focused_sensor])[0]
            self.ax_helmet.scatter(*focus, c="red", label="all sensors", alpha=1, s=20)
    

    def update_message_box(self, category:str, label:str, message:str):
        """Updates the message box with the current sensor information."""
        self.ax_text.clear()
        self.ax_text.axis("off")  # Turn off axis lines
        self.ax_text.text(
            0.5, 0.4, f"{category}: {label}", va="center", ha="center", fontsize=14
        )
        self.ax_text.text(
            0.5, 0.8, message, va="center", ha="center", fontsize=14, color="red"
        )

    def add_point_3d(self, x:float, y:float, z:float, category:str):
        """Add a point to the 3D plot."""
        alpha = 0.9
        size = 6
        if category == "OPM":
            color = "blue"
        elif category == "EEG":
            color = "orange"
        elif category == "fiducials":
            color = "green"
        else:
            color = "k"
            alpha = 0.2
            size = 3

        self.ax_dig.scatter(x, y, z, c=color, label=category, alpha=alpha, s=size)

    def refresh_plot(self):
        """Refreshes the plot to reflect any new changes."""
        plt.draw()
        plt.pause(0.3)

    def refresh_plot_fast(self):
        """Refreshes the plot to reflect any new changes."""
        plt.draw()
        plt.pause(0.1)

    def close_plot(self):
        """Closes the plot"""
        plt.close()


class Digitiser:
    def __init__(
        self, 
        connector: FastrakConnector,
        helmet_template: HelmetTemplate,
        digtisation_scheme: list[dict] = [],
    ):
        """
        Args:
            connector (FastrakConnector):
            plotter (DigitisationPlotter):
        """
        self.connector = connector
        self.digitised_points = pd.DataFrame(
            columns=["category", "label", "x", "y", "z"]
        )
        self.digitisation_scheme = digtisation_scheme
        self.plotter = DigitisationPlotter(helmet_template)

    def add(self, category:str, labels:list[str]=[], dig_type:str="single", n_points=None):
        """
        Adds to the digitisiation scheme

        Args:
            category (str): which type of points you want to digitise (for example OPM, fiducials or head)
            labels (list of strings): the labels of the points for example ["rpa", "lpa", "nasion"]. If None the label will be the same as the category.
            dig_type (str): whether to digitise the points seperately with specific labels (single) or continuously (continuous)
            n_points (None or int): if no labels are provided, you need to indicate how many points you want to digitise
        """

        if dig_type not in ["single", "continuous"]:
            raise ValueError

        if dig_type == "continuous" and n_points is None:
            raise ValueError(
                "If the digitisation type is continous, you need to add the number of points you want to digitise using the n_points flag"
            )

        self.digitisation_scheme.append(
            {
                "category": category,
                "labels": labels,
                "dig_type": dig_type,
                "n_points": n_points,
            }
        )

    def update_digitised_data(self, category:str, label:str, position:tuple[float, float, float]):
        """
        Helper method to update the 3D plot and digitised points DataFrame.

        Args:
            category (str): The category of the point (e.g., OPM, EEG, fiducials).
            label (str): The label of the point (e.g., specific marker name).
            position (tuple): The (x, y, z) coordinates of the point.
        """
        # Add the point to the 3D plot
        self.plotter.add_point_3d(*position, category=category)

        new_data = pd.DataFrame(
            {
                "category": [category],
                "label": [label],
                "x": [position[0]],
                "y": [position[1]],
                "z": [position[2]],
            }
        )

        self.digitised_points = pd.concat(
            [self.digitised_points, new_data], ignore_index=True
        )

    def digitise_continuous(self, category, n_points):
        self.plotter.update_message_box(
            label=category,
            category=category,
            message="Ready for digitization... Press the stylus button to record points.",
        )

        idx = 0
        print("Press the stylus button to start scanning")

        # Run until we have captured enough points or user stops scanning
        while idx < n_points:
            data, position = self.connector.get_position_relative_to_head_receiver()

            self.plotter.update_message_box(
                    label="", category=category, message=f"Now digitising:{idx}/{ n_points}"
                )

            self.update_digitised_data(
                category=category, label=category, position=position
            )

            idx += 1  # Move to the next point
            self.plotter.refresh_plot_fast()

        self.play_sound("done")

    def digitise_single(self, category:str, labels:list[str], limit:int=30):
        """ """
        print(
            "Pressing the stylus button more than 30 cm from the head reference will undo the point"
        )

        idx = 0

        if category == "OPM":
            self.plotter.helmet_plot(marked_sensors=labels, focused_sensor=labels[idx])

        self.plotter.update_message_box(
            label=labels[idx], category=category, message="Ready for digitization..."
        )
        self.plotter.refresh_plot()

        while idx < len(labels):
            print(idx)
            sensor_data, position = (
                self.connector.get_position_relative_to_head_receiver()
            )

            # checking if the click was more than 30 cm from the head reference
            point1 = (sensor_data[1, 0], sensor_data[2, 0], sensor_data[3, 0])
            point2 = (sensor_data[1, 1], sensor_data[2, 1], sensor_data[3, 1])

            # adjust the index based on whether the point is valid or needs to be undone (i.e. more than 30 cm away from head receiver)
            idx, cont = self.idx_of_next_point(
                self.calculate_distance(point1, point2), idx, limit=limit
            )

            if idx <= len(labels) - 1:
                self.plotter.update_message_box(
                    label=labels[idx], category=category, message="Now digitising:"
                )
                if category == "OPM":
                    self.plotter.helmet_plot(marked_sensors=labels, focused_sensor=labels[idx])

            if cont:
                self.update_digitised_data(
                    category=category, label=labels[idx - 1], position=position
                )

            else:
                # remove the last row of the digitised points
                self.digitised_points = self.digitised_points.head(-1)
            
        

            self.plotter.refresh_plot()


    def run_digitisation(self):
        """
        Runs the digitisation scheme
        """

        for dig in self.digitisation_scheme:
            # to make sure any "residue" button presses from previously does not interfere
            self.connector.clear_old_data()

            category = dig["category"]
            labels = dig["labels"]
            dig_type = dig["dig_type"]

            if dig_type == "continuous":
                self.digitise_continuous(category, dig["n_points"])

            elif dig_type == "single":
                self.digitise_single(category, labels)

            else:
                raise ValueError(
                    f"dig_type {dig_type} is not implemented. Use either single or continuous"
                )
        self.plotter.close_plot()

    def save_digitisation(self, output_path:Path):
        """
        Args:
            output_path (Path or str): path to save a csv file with the digitised points
        """
        self.digitised_points.to_csv(output_path, index=False)
    
    @staticmethod
    def calculate_distance(point1:tuple, point2:tuple):
        # unpack the coordinates of point1 and point2
        x1, y1, z1 = point1
        x2, y2, z2 = point2

        return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2 + (z2 - z1) ** 2)
    
    def idx_of_next_point(self, distance:float, idx:int, limit:float=30.,):
        # if stylus was clicked more than limit away from the head reference, the last point is undone
        if distance > limit:
            self.play_sound("wrong")
            if idx == 0:
                return 0, False
            else:
                return idx - 1, False
        else:  # moving on to the next
            self.play_sound("beep")
            return idx + 1, True
        
    @staticmethod
    def play_sound(sound_type):
        if sound_type == "beep":
            os.system(f'afplay "{SOUND_DIR / "beep.wav"}"')
        elif sound_type == "wrong":
            os.system(f'afplay "{SOUND_DIR / "wrongbeep.wav"}"')
        elif sound_type == "done":
            os.system(f'afplay "{SOUND_DIR / "done.mp3"}"')



    


