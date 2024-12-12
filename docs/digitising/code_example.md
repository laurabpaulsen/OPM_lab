# Polhemus digitisation
To digtise using this module,first you need to initialise a FastrakConnector object where you specify the USB port the device is connected to. Afterwards you prepare for digitisation, which will return the fastrak to factory settings, set the output to metric, clear any incoming data and check whether the stylus and head receiver are connected properly. 

```python
connector = FastrakConnector(usb_port='/dev/cu.usbserial-110')
connector.prepare_for_digitisation()
```

The next step is to setup the digitiser object and add any points you would like to digitise
```python
digitiser = Digitiser(connector=connector)

fiducials = ["lpa", "rpa", "nasion"]
OPM_sensors = ["FL52", "FL61", "FL92", "FL99"]
EEG_sensors = ["Fp1", "Fp2"]
head_surface_size = 60
    
digitiser.add("fiducials", labels=fiducials, dig_type="single")
digitiser.add("OPM", labels=OPM_sensors, dig_type="single")
digitiser.add("EEG", labels=EEG_sensors, dig_type="single")
digitiser.add("head", n_points=head_surface_size, dig_type="continuous")
```

Then you run the digitisation and save the output
```python
digitiser.run_digitisation()
digitiser.save_digitisation(output_path='insert/your/path/here.csv')
```

Note on dig_type argument in the Digtiser.add() function:
- `single`: Takes a category (for example "OPM") and a list of labels (["FL1", "FL2", "FL3"]). Thus this function is useful for marking marking points with a label attached to them (i.e. if you need to know which specific sensor or fiducial). If you want to re-digtise a point just press the stylus 30 cm away from the head. 
- `continuous`: Used for marking a specified amount of points with out any specific label. This could for example be 60 points distributed across the head of the participant. This function allows to keep the button of the stylus pressed down continuosly to mark consecutive points. 

The digitisation will be shown using matplotlib - however sometimes the plot takes a bit to update, and the plot does not show until the first point is made


Note: during digitisation some sounds are played to provide feedback. However this functionally currently only works on mac