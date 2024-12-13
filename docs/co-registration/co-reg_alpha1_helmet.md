---
title: Co-registering OPM sensors in Fieldline Alpha1 semi-rigid helmet to MR
nav_order: 1
parent: Co-registration
layout: default
---
Knowing the position (and orientation in the case of sensors measuring magnetic fields) is crucial to allow for reconstruction of neural sources from the data measured at the sensors. 

Here we show an example of co-registering 4 OPM sensors placed in the Fieldline Alpha1 semi-rigid helmet to an MR of the participants brain. 

First, we load modules we need

```python
from pyvista import Plotter

from OPM_lab.mne_integration import add_dig_montage, add_device_to_head, add_sensor_layout
from OPM_lab.sensor_position import OPMSensorLayout, FL_alpha1_helmet

from mne.viz import plot_alignment
from mne.utils._bunch import NamedInt
import mne
import pandas as pd
```

The next step is to load both the raw OPM data, as well as the digitised points (i.e., the output after [Digitising sensor positions]({{ site.url }}{% link digitising/index.md %}))
```python
opm_path = "path_to_your_data.fif"
raw = mne.io.read_raw(opm_path, preload=True)

dig_path = "path_to_the_dig_file.csv"
points = pd.read_csv(dig_path)
```


Next, rename the channels in the raw OPM data to correspond to the label of the sensor slot in the semi-rigid helmet
```python
raw.pick(["00:01-BZ_CL", '00:02-BZ_CL', "00:03-BZ_CL", "00:04-BZ_CL"])

mne.rename_channels(
    raw.info, 
    {
        "00:01-BZ_CL" : "FL3", 
        "00:02-BZ_CL" : "FL10", 
        "00:03-BZ_CL" : "FL16", 
        "00:04-BZ_CL" : "FL62"
    }
)
```    

Define a variable with the depth measurements. It is important that the depth measurements are in the same order as the label input in the next code chunk!!
```
depth_meas = [40/1000, 47/1000, 44/1000, 40/1000] # mm converted to meter (order = 3, 10, 16, 62)
```


If you are using another type of sensor (e.g. not the default "FieldLine OPM sensor Gen1 size = 2.00 mm") remember to specify it here using the `coil_type` flag.
```python
sensor_layout = OPMSensorLayout(
    label=["FL3", "FL10", "FL16", "FL62"], 
    depth=depth_meas,
    helmet_template=FL_alpha1_helmet,   
    # coil_type=NamedInt("SQ20950N", 3024) # useful for plotting as orientation of OPMs (default coil types) are difficult to see on alignment plot

) 
```

```python
add_dig_montage(raw, points)
```

```python
add_sensor_layout(raw, sensor_layout)
```

```python
add_device_to_head(raw, points)

```python
fig = plot_alignment(raw.info, meg=("sensors"), dig = True, coord_frame="head", verbose = True)    
Plotter().show()
```

# TO DO - add code for rest of co-registration pipeline