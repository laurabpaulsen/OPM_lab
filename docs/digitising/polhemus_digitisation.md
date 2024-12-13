---
title: Polhemus digitistation
nav_order: 1
parent: Digtising
layout: default
---

# Polhemus digitisation

## Physical setup
* Polhemus Fastrak device, transmitter, stylus, reciever

Transmitter: Connect the transmitter to the port labelled transmitter on the device
Receiver ports: Stylus connected to receiver port 1, receiver to be placed on forehead connected to receiver port 2
Computer: Connect the computer to the RS-232 using a USB to RS-232 converter

## Code
This tutorial, shows an example of how to build the code for digitising a set of points around the head of the participant, a few OPM and EEG sensors, as well as three fiducials.

We begin by loading the modules we need
```
from OPM_lab.digitise import Digitiser, FastrakConnector
from OPM_lab.sensor_position import FL_alpha1_helmet, EEGcapTemplate
```


To digtise using this module, first you need to initialise a FastrakConnector object where you specify the USB port the device is connected to. Afterwards you prepare for digitisation, which will return the fastrak to factory settings, set the output to metric, clear any incoming data and check whether the stylus and head receiver are connected properly. 

```python
connector = FastrakConnector(usb_port='/dev/cu.usbserial-110')
connector.prepare_for_digitisation()
```


We define a few variables, with the labels of the sensors and fiducials, as well as the number of head points we want to record. 
```python
fiducials = ["lpa", "rpa", "nasion"]
OPM_sensors = ["FL52", "FL61", "FL92", "FL99"]
EEG_sensors = ["Fp1", "Fp2"]
head_surface_size = 60

```

The next step is to setup the digitiser object and add any points you would like to digitise. Currently, two types of digitistation schemes are available, and can be set using the `dig_type` flag. 
- `single`: Takes a category (for example "OPM") and a list of labels (["FL1", "FL2", "FL3"]). Thus this function is useful for marking marking points with a label attached to them (i.e. if you need to know which specific sensor or fiducial). If you want to re-digtise a point just press the stylus 30 cm away from the head. 
- `continuous`: Used for marking a specified amount of points with out any specific label. This could for example be 60 points distributed across the head of the participant. This function allows to keep the button of the stylus pressed down continuosly to mark consecutive points, that do not need to be distinguished from eachother. 


```python
digitiser = Digitiser(connector=connector)    
digitiser.add(category="fiducials", labels=fiducials, dig_type="single")
digitiser.add(category="OPM", labels=OPM_sensors, dig_type="single", template=FL_alpha1_helmet)
digitiser.add(category="EEG", labels=EEG_sensors, dig_type="single", template= EEGcapTemplate("easycap-M1"))
digitiser.add(category="head", n_points=head_surface_size, dig_type="continuous")
```

There is the option to display a template indicating which specific point needs to be digitised at any given moment. These templates can either be predefined by the user or easily loaded from MNE-Python by specifying the identifier of a specific EEG cap. Additionally, the repository includes a representation of the semi-rigid helmet. This feature is particularly helpful for maintaining an overview during the process, reducing the risk of mixing up the points.

Now the digitisation can be run. Remember to save the output!
```python
digitiser.run_digitisation()
digitiser.save_digitisation(output_path='insert/your/path/here.csv')
```

