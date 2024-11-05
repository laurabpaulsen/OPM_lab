import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import gridspec
from pathlib import Path
import os
from .fastrak_connector import FastrakConnector
from ..sensor_position import HelmetTemplate
import math
from abc import ABC, abstractmethod
BASE_DIR = Path(__file__).resolve().parents[1]
SOUND_DIR = BASE_DIR / "soundfiles"




class BasePlotter(ABC):
    
    @abstractmethod
    def setup_figure(self):
        pass
    
    @abstractmethod
    def add_point_3d(self, x, y, z, category):
        pass
    
    @abstractmethod
    def helmet_plot(self, marked_sensors, focused_sensor, template):
        pass

    @abstractmethod
    def update_message_box(self, category: str, label: str):
        pass

    @abstractmethod
    def refresh_plot(self):
        pass

class MatplotlibPlotter(BasePlotter):
    def __init__(self, set_axes_limits=True):
        self.fig, self.ax_dig, self.ax_helmet, self.ax_text = self.setup_figure(set_axes_limits)

    def setup_figure(self, set_axes_limits=True):
        fig = plt.figure(figsize=(15, 6))
        gs = gridspec.GridSpec(1, 3, width_ratios=[1, 1, 1], wspace=0.2)
        
        ax_dig = fig.add_subplot(gs[0], projection="3d")
        ax_helmet = fig.add_subplot(gs[1], projection="3d")
        ax_text = fig.add_subplot(gs[2])

        if set_axes_limits:
            ax_dig.set_xlim([-30, 30])
            ax_dig.set_ylim([-30, 30])
            ax_dig.set_zlim([-30, 30])

        for ax, title in zip([ax_helmet, ax_dig], ["Helmet template", "Digtised points"]):
            ax.set_xlabel("X")
            ax.set_ylabel("Y")
            ax.set_zlabel("Z")
            ax.set_title(title)

    
        ax_text.axis("off")
        ax_text.set_title( "Now digitising...")


        return fig, ax_dig, ax_helmet, ax_text

    def helmet_plot(self, marked_sensors, focused_sensor, template):
        for pos in template.chan_pos:
            self.ax_helmet.scatter(*pos, c="lightblue", alpha=0.7, s=30, marker="s")
        
        for pos in template.get_chs_pos(marked_sensors):
            self.ax_helmet.scatter(*pos, c="blue", label="all sensors", alpha=0.6, s=8)
        
        if isinstance(focused_sensor, str): 
            focus = template.get_chs_pos([focused_sensor])[0]
            self.ax_helmet.scatter(*focus, c="red", label="all sensors", alpha=1, s=20)

    def add_point_3d(self, x, y, z, category):
        color = {"OPM": "blue", "EEG": "orange", "fiducials": "green"}.get(category, "black")
        if category == "head":
            alpha = 0.5
        else:
            alpha = 1
        
        self.ax_dig.scatter(x, y, z, c=color, alpha=alpha, s=6)

    def update_message_box(self, category, label):
        for txt in self.ax_text.texts:
            txt.set_visible(False)
        self.ax_text.text(0.5, 0.8, f"{category}: {label}", va="center", ha="center", fontsize = 30)

    def refresh_plot(self, pace = "slow"):
        plt.draw()
        if pace == "slow":
            plt.pause(0.3)
        else:
            plt.pause(0.1)


class DigitisationPlotter:
    def __init__(self, library="matplotlib"):
        if library == "matplotlib":
            self.plotter = MatplotlibPlotter()

        else: 
            raise ValueError("not implemented")

    def helmet_plot(self, marked_sensors=[], focused_sensor=None, template=None):
        self.plotter.helmet_plot(marked_sensors, focused_sensor, template)

    def add_point_3d(self, x, y, z, category):
        self.plotter.add_point_3d(x, y, z, category)

    def update_message_box(self, category, label):
        self.plotter.update_message_box(category, label)

    def refresh_plot(self, **kwargs):
        self.plotter.refresh_plot(**kwargs)


class Digitiser:
    def __init__(
        self, 
        connector: FastrakConnector,
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
        self.plotter = DigitisationPlotter()

    def add(self, category:str, labels:list[str]=[], dig_type:str="single", n_points=None, template = None):
        """
        Adds to the digitisiation scheme

        Args:
            category (str): which type of points you want to digitise (for example OPM, fiducials or head)
            labels (list of strings): the labels of the points for example ["rpa", "lpa", "nasion"]. If None the label will be the same as the category.
            dig_type (str): whether to digitise the points seperately with specific labels (single) or continuously (continuous)
            n_points (None or int): if no labels are provided, you need to indicate how many points you want to digitise
            template (HelmetTemplate): to show to guide digitistation
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
                "template": template
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
            category=category
        )

        idx = 0
        print("Press the stylus button to start scanning")

        # Run until we have captured enough points or user stops scanning
        while idx < n_points:
            data, position = self.connector.get_position_relative_to_head_receiver()

            self.plotter.update_message_box(
                    label="", category=category, label=f"{idx}/{n_points}",
                )

            self.update_digitised_data(
                category=category, label=category, position=position
            )

            idx += 1  # Move to the next point
            self.plotter.refresh_plot(pace = "fast")

        self.play_sound("done")

    def digitise_single(self, category:str, labels:list[str], template:HelmetTemplate=None, limit:int=30):
        """ """
        print(
            "Pressing the stylus button more than 30 cm from the head reference will undo the point"
        )

        idx = 0

        if template:
            self.plotter.helmet_plot(marked_sensors=labels, focused_sensor=labels[idx], template = template)

        self.plotter.update_message_box(
            label=labels[idx], category=category,
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
                    label=labels[idx], category=category
                )
                if template:
                    self.plotter.helmet_plot(marked_sensors=labels, focused_sensor=labels[idx], template = template)


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
            template = dig["template"]

            if dig_type == "continuous":
                self.digitise_continuous(category, dig["n_points"])

            elif dig_type == "single":
                self.digitise_single(category, labels, template)

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