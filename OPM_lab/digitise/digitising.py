import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib import gridspec
from pathlib import Path
import os
from .fastrak_connector import FastrakConnector
from ..sensor_position import HelmetTemplate
import math

BASE_DIR = Path(__file__).resolve().parents[1]
SOUND_DIR = BASE_DIR / "soundfiles"


class Digitiser:
    def __init__(
        self, 
        connector: FastrakConnector,
        digitisation_scheme: list[dict] = [],
    ):
        self.connector = connector
        self.digitised_points = pd.DataFrame(columns=["category", "label", "x", "y", "z"])
        self.digitisation_scheme = digitisation_scheme
        self.current_category = None
        self.labels:list[int] = []  # To track labels for single digitisation
        self.current_label_idx = 0
        self.n_points = 0
        self.fig, self.ax_dig, self.ani = None, None, None  # Plot elements

    def add(self, category: str, labels: list[str] = [], dig_type: str = "single", n_points: int = None, template:HelmetTemplate=None):
        if dig_type not in ["single", "continuous"]:
            raise ValueError("Invalid dig_type; must be either 'single' or 'continuous'.")

        if dig_type == "continuous" and n_points is None:
            raise ValueError("For 'continuous' digitisation, specify n_points.")

        self.digitisation_scheme.append({
            "category": category,
            "labels": labels,
            "dig_type": dig_type,
            "n_points": n_points,
            "template": template
        })

    def setup_plot(self):
        # Initialize plot with the figure and axis
        self.fig = plt.figure(figsize=(15, 6))
        gs = gridspec.GridSpec(1, 3, width_ratios=[1, 1, 1], wspace=0.2)
        self.ax_dig = self.fig.add_subplot(gs[0], projection="3d")
        self.ax_helmet = self.fig.add_subplot(gs[1], projection="3d")
        self.ax_text = self.fig.add_subplot(gs[2])
        self.ax_text.axis("off")

        # 3D plot settings for digitised points
        self.ax_dig.set_xlim([-30, 30])
        self.ax_dig.set_ylim([-30, 30])
        self.ax_dig.set_zlim([-30, 30])
        self.ax_dig.set_xlabel("X")
        self.ax_dig.set_ylabel("Y")
        self.ax_dig.set_zlabel("Z")
        self.ax_dig.set_title("Digitised points")


    def start_animation(self):
        # Start animation with FuncAnimation
        self.ani = FuncAnimation(self.fig, self.animate, interval=200, cache_frame_data=False)
        plt.show()
    
    def animate(self, i):
        # Initial setup for the first frame
        if i == 0:
            self.current_label = self.labels[self.current_label_idx]
        # Handle continuous or single mode logic
        elif self.current_dig_type == "single":
            self.handle_single_digitisation(i)
        elif self.current_dig_type == "continuous":
            self.handle_continuous_digitisation(i)

        # Plot the digitised points
        self.update_plot()

        # Update the helmet view and instructions
        self.update_helmet_and_instructions()

        # Reset axis labels and limits for the 3D plots
        self.reset_plot_axes()

    def handle_single_digitisation(self, i):
        """
        Handle logic for single digitisation mode:
        - Check if the point is valid (within the range from the head receiver).
        - Update the label index and play sound accordingly.
        """
        data, position = self.connector.get_position_relative_to_head_receiver()

        # Check if the point is too far from the head (more than 30 cm)
        point1 = (data[1, 0], data[2, 0], data[3, 0])
        point2 = (data[1, 1], data[2, 1], data[3, 1])

        # Calculate distance and determine whether to move to next point or undo
        distance = self.calculate_distance(point1, point2)
        idx, cont = self.idx_of_next_point(distance, self.current_label_idx)

        if not cont:
            self.play_sound("wrong")
            self.current_label_idx = idx
            if self.current_label_idx != 0:
                self.current_label_idx = idx
            # Undo the last point
            self.digitised_points = self.digitised_points.head(-1)
            print(self.digitised_points.tail(3))
        else:
            self.update_digitised_data(self.current_category, self.current_label, position)
            self.current_label_idx += 1
            try:
                self.current_label = self.labels[self.current_label_idx]
            except IndexError: # when no more labes are present close the plot
                plt.close()
        
    def handle_continuous_digitisation(self, i):
        """
        Handle logic for continuous digitisation mode:
        - Continuously capture data and update the points.
        - Progress the label index after each valid capture.
        """
        data, position = self.connector.get_position_relative_to_head_receiver()

        self.update_digitised_data(self.current_category, self.current_label, position)
        self.current_label_idx += 1

        try:
            self.current_label = self.labels[self.current_label_idx]
        except IndexError: # when no more labes are present close the plot
            plt.close()

    def update_plot(self):
        """
        Update the 3D plot with the digitised points.
        This method will clear the previous plot and re-render the points.
        """
        self.ax_dig.cla()  # Clear previous frame
        colors = {'OPM': 'blue', 'head': 'grey', "fiducials": "red", "EEG": "purple"}
        alpha = {'head': 0.5, 'OPM': 1.0, 'fiducials': 1.0, 'EEG': 1.0}  # Define alpha values for each category

        if not self.digitised_points.empty:
            self.ax_dig.scatter(
                self.digitised_points['x'],
                self.digitised_points['y'],
                self.digitised_points['z'],
                c=self.digitised_points['category'].map(colors),
                alpha=self.digitised_points['category'].map(alpha)
            )
            for _, row in self.digitised_points.iterrows():
                if row['category'] != "head":  # Exclude head points
                    self.ax_dig.text(row['x'], row['y'], row['z'], row['label'])

    def update_helmet_and_instructions(self):
        """
        Update the helmet view and the instructions shown to the user.
        This includes displaying the current label and the point being digitised.
        """
        # Update helmet view
        self.ax_helmet.cla()  # Clear previous frame
        if self.current_template:
            for pos in self.current_template.chan_pos:
                self.ax_helmet.scatter(*pos, c="lightblue", alpha=0.7, s=30, marker="s")
            for pos in self.current_template.get_chs_pos(self.labels):
                self.ax_helmet.scatter(*pos, c="blue", label="all sensors", alpha=0.6, s=8)

            focus = self.current_template.get_chs_pos([self.current_label])[0]
            self.ax_helmet.scatter(*focus, c="red", label="current sensor", alpha=1, s=20)

        # Update instructions text
        self.ax_text.clear()  # Clear any previous instructions
        self.ax_text.axis('off')  # Hide axes for text display

        try:
            current_instruction = f"{self.current_category}\n{self.labels[self.current_label_idx]}"
        except IndexError:
            current_instruction = f"Done digitising {self.current_category}"
        
        self.ax_text.text(0.1, 0.8, current_instruction, fontsize=30, color="black")

        point_instruction = f"Point {self.current_label_idx + 1} of {self.n_points}"
        self.ax_text.text(0.1, 0.6, point_instruction, fontsize=20, color="black")

    def reset_plot_axes(self):
        """
        Reset the plot axes to default settings.
        """
        for ax in [self.ax_dig, self.ax_helmet]:
            ax.set_xlabel("X")
            ax.set_ylabel("Y")
            ax.set_zlabel("Z")

        self.ax_dig.set_xlim([-30, 30])
        self.ax_dig.set_ylim([-30, 30])
        self.ax_dig.set_zlim([-30, 30])
        self.ax_dig.set_title("Digitised points")

    def update_digitised_data(self, category: str, label: str, position: tuple[float, float, float]):
        """
        Update the dataframe with a new position for a digitised point.
        
        Args:
            category (str): The category of the point (e.g., 'OPM', 'head').
            label (str): The label associated with this point.
            position (tuple): The (x, y, z) coordinates of the point.
        """
        # Update the dataframe with new position data
        new_data = pd.DataFrame({
            "category": [category],
            "label": [label],
            "x": [position[0]],
            "y": [position[1]],
            "z": [position[2]],
        })
       
         
        self.digitised_points = pd.concat(
            [self.digitised_points if not self.digitised_points.empty else None, 
             new_data], 
            
            ignore_index=True)

    def run_digitisation(self):
        for dig in self.digitisation_scheme:
            # Set up for digitising points
            self.current_category = dig["category"]
            self.n_points = dig["n_points"] if dig["n_points"] else len(dig["labels"])
            self.labels = dig["labels"] if dig["labels"] else [self.current_category] * self.n_points
            self.current_label_idx = 0
            self.current_template = dig["template"]
            self.current_dig_type = dig["dig_type"]
            
            
            self.connector.clear_old_data()

            self.setup_plot()
            self.start_animation()

    def save_digitisation(self, output_path: Path):
        # Save the digitised points to a CSV file
        self.digitised_points.to_csv(output_path, index=False)

    @staticmethod
    def play_sound(sound_type):
        if sound_type == "beep":
            os.system(f'afplay "{SOUND_DIR / "beep.wav"}"')
        elif sound_type == "wrong":
            os.system(f'afplay "{SOUND_DIR / "wrongbeep.wav"}"')
        elif sound_type == "done":
            os.system(f'afplay "{SOUND_DIR / "done.mp3"}"')

    @staticmethod
    def calculate_distance(point1:tuple, point2:tuple):
        # unpack the coordinates of point1 and point2
        x1, y1, z1 = point1
        x2, y2, z2 = point2

        return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2 + (z2 - z1) ** 2)
    
    def idx_of_next_point(self, distance:float, idx:int, limit:float=30.):
        # if stylus was clicked more than limit away from the head reference, the last point is undone
        if distance > limit:
            if idx <= 0:
                return 0, False
            else:
                return idx - 1, False
        else:  # moving on to the next
            return idx + 1, True

