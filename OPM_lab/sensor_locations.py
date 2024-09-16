import numpy as np
from matplotlib import cm
import matplotlib.pyplot as plt


def plot_sensor_locations(info):
    loc = []
    
    for i, ch in enumerate(info["chs"]):
        tmp_loc = ch["loc"][:3]  # extract x, y, z
        loc.append(tmp_loc)  
    
    loc = np.array(loc)    

    x = loc[:, 0]
    y = loc[:, 1]
    z = loc[:, 2]

    # create an array of colors (one color per channel)
    n_channels = loc.shape[0] 
    colors = cm.rainbow(np.linspace(0, 1, n_channels)) 

    # creating a 3D scatter plot
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    ax.scatter(x, y, z, c=colors, marker='o')  # Assign the colors to each point

    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_zlabel('Z')

    plt.show() 

def update_sensor_loc(old_loc):
    print("Not updating sensor location at the moment. Remember to CHANGE THIS FUNCTION")
    return old_loc

def update_sensor_locations(info):

    old_loc = []
    new_loc = [] # for plottting

    for i, ch in enumerate(info["chs"]):
        tmp_loc = ch["loc"][:3]  # extract x, y, z
        old_loc.append(tmp_loc)       

        # change sensor positions
        tmp_new_loc = update_sensor_loc(tmp_loc)
        new_loc.apped(tmp_loc)
        
        info['chs'][i]['loc'][:3] = tmp_new_loc
        # change sensor orientations
        #rot_coils = np.array([location[3:6], location[6:9], location[9:12]]) # orientation
        #rot_coils = rot_coils @ R.T
        
        #location[3:12] = rot_coils.flatten() # check if this is correct

    new_loc = np.array(new_loc)

    return info

