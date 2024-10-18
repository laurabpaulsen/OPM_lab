
import numpy as np
import matplotlib.pyplot as plt
import os
import math
import pandas as pd
from pathlib import Path
from fastrak_connector import FastrakConnector


BASE_DIR = Path(__file__).resolve().parent
SOUND_DIR = BASE_DIR / 'soundfiles'

def idx_of_next_point(distance, idx, limit = 30):
    wrong_beep_path = SOUND_DIR / 'wrongbeep.wav'
    beep_path = SOUND_DIR / 'beep.wav'

    # if stylus was clicked more than limit away from the head reference, the last point is undone
    if distance > limit:
        # Play a beep sound to indicate that data is ready
        os.system(f'afplay "{str(wrong_beep_path)}"')
        if idx == 0:
            return 0, False
        else:
            return idx - 1, False
    else: # moving on to the next
        os.system(f'afplay "{str(beep_path)}"')
        return idx + 1, True


def calculate_distance(point1, point2):
    # unpack the coordinates of point1 and point2
    x1, y1, z1 = point1
    x2, y2, z2 = point2
    
    return math.sqrt((x2 - x1)**2 + (y2 - y1)**2 + (z2 - z1)**2)

def update_message_box(ax, category, label, message):
    """Updates the message box with current sensor information."""
    ax.clear()
    ax.axis('off')  # Turn off axis lines
    ax.text(0.5, 0.4, f'{category}: {label}', va='center', ha='center', fontsize=14)
    ax.text(0.5, 0.8, message, va='center', ha='center', fontsize=14, color='red')

def add_point_3d(x, y, z, category, ax):
    """Add a point to the 3D plot."""
    alpha = 1
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

    ax.scatter(x, y, z, c=color, label=category, alpha = alpha, s = size)


def setup_figure(set_axes_limits = True):
    # set up the figure with two subplots: one for 3D plot, one for messages
    fig = plt.figure(figsize=(10, 6))
    
    # 3D plot subplot
    ax_3d = fig.add_subplot(121, projection='3d')
    ax_3d.set_xlabel('X')
    ax_3d.set_ylabel('Y')
    ax_3d.set_zlabel('Z')
    ax_3d.set_title(f'Points digitised')
    if set_axes_limits:
        ax_3d.set_xlim([-30, 30])
        ax_3d.set_ylim([-30, 30])
        ax_3d.set_zlim([-30, 30])

    # textbox subplot
    ax_text = fig.add_subplot(122)
    ax_text.axis('off')

    return fig, ax_3d, ax_text




class Digitiser:
    def __init__(self, connector: FastrakConnector):
        """
        Args:
            connector (FastrakConnector):
        """
        self.connector = connector
        self.digitised_points = pd.DataFrame(columns=['category','label','x','y','z'])
        self.digitisation_scheme = []
        
    def add(self, category, labels = None, dig_type = "single", n_points = None):
        """
        Adds to the digitisiation scheme
        
        Args:
            category (str): which type of points you want to digitise (for example OPM, fiducials or head)
            labels (None or list): the labels of the points for example ["rpa", "lpa", "nasion"]. If None the label will be the same as the category. 
            dig_type (str): whether to digitise the points seperately with specific labels (single) or continuously (continuous)
            n_points (None or int): if no labels are provided, you need to indicate how many points you want to digitise
        """

        if dig_type not in ["single", "continuous"]:
            raise ValueError
        
        if dig_type == "continuous" and n_points == None:
            raise ValueError("If the digitisation type is continous, you need to add the number of points you want to digitise using the n_points flag")

        self.digitisation_scheme.append({
            "category": category,
            "labels": labels,
            "dig_type": dig_type,
            "n_points": n_points
            })
            

    def digitise_continuous(self, category, n_points, ax_3d, ax_text):
        update_message_box(ax_text, label=category, category=category,
                        message="Ready for digitization... Press the stylus button to record points.") 
        
        plt.draw()  # Ensures the initial plot is drawn
        plt.show(block=False)  # Show the plot without blocking the rest of the code

        idx = 0
        print("Press the stylus button to start scanning")

        
        # Run until we have captured enough points or user stops scanning
        while idx < n_points:
            data, position = self.connector.get_position_relative_to_head_receiver()
                
            self.digitised_points = pd.concat(
                [self.digitised_points,
                pd.DataFrame.from_dict({
                    "category": category,
                    "label": category,
                    "x": position[0],
                    "y": position[1],
                    "z": position[2]
                    })])
                
            print(f"Point {idx + 1}/{n_points} digitized at {position}")
            idx += 1  # Move to the next point
                    
            # Update the 3D plot with the newly captured point
            add_point_3d(*position, ax=ax_3d, category=category)
            plt.draw()  # Refresh the plot

        os.system(f'afplay "{SOUND_DIR / "done.mp3"}"')

    def digitise_single(self, category, labels, ax_3d, ax_text, limit = 30):
        """
 
        """
        print('Pressing the stylus button more than 30 cm from the head reference will undo the point')

        idx = 0
        
        update_message_box(ax_text, sensor_name=labels[idx], category=category, message="Ready for digitization...") 
        plt.draw()  # Ensures the initial plot is drawn
        plt.pause(0.1)


        while idx < len(labels):
            sensor_data, position = self.connector.get_position_relative_to_head_receiver()
            
            # checking if the click was more than 30 cm from the head reference
            point1 = (sensor_data[1, 0], sensor_data[2, 0], sensor_data[3, 0])
            point2 = (sensor_data[1, 1], sensor_data[2, 1], sensor_data[3, 1])

            # adjust the index based on whether the point is valid or needs to be undone (i.e. more than 30 cm away from head receiver)
            idx, cont = idx_of_next_point(calculate_distance(point1, point2), idx, limit=limit)
            
            if idx <= len(labels)-1:
                update_message_box(ax_text, sensor_name=labels[idx], category=category, message="Now digitising:") 
            
            if cont:
                # add the point to the 3D plot
                add_point_3d(*position, ax=ax_3d, category=category)
                
                self.digitised_points = pd.concat(
                    [self.digitised_points,
                     pd.DataFrame.from_dict({
                         "category": category,
                         "label": labels[idx-1],
                         "x": position[0],
                         "y": position[1],
                         "z": position[2]
                     })])
            else: 
                # remove the last row of the digitised points
                self.digitised_points = self.digitised_points.head(-1)

            plt.draw()
            plt.pause(0.1)

        plt.close()



    def run_digitisation(self):
        """
        
        """
        fig, ax_3d, ax_text = setup_figure()

        for dig in self.digitisation_scheme:
            # to make sure any "residue" button presses from previously does not interfere
            self.connector.clear_old_data()

            category = dig["category"]
            labels = dig["labels"]
            dig_type = dig["dig_type"]

            if dig_type == "continuous":
                self.digitise_continuous(category, dig["n_points"], ax_3d, ax_text)

            elif dig_type == "single":
                self.digitise_single(category, labels, ax_3d, ax_text)
            
            else:
                raise ValueError(f"dig_type {dig_type} is not implemented. Use either single or continuous")
        

    def save_digitisation(self, output_path):
        """
        Args:
            output_path (Path or str): path to save a csv file with the digitised points
        """
        self.digitised_points.to_csv(output_path, index=False)
    

