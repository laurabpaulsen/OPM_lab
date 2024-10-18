# OPM_lab
Under development. This repository holds a module for integrating the (semi)-rigid helmet from FieldLine for OPMs with `mne-python` software and polhemus fastrak digitiser


# Usage

## 👩‍💻 Code
## Polhemus digitisation
To digtise using this module, you need to make sure you have the `OPM_lab` directory which contains files with functions you will need.

In the `src/digitise_example.py` you will find an example of how to setup the code for running the digitisation. 

First you need to initialise a FastrakConnector object where you specify the USB port the device is connected to. Afterwards you prepare for digitisation, which will return the fastrak to factory settings, set the output to metric, clear any incoming data and check whether the stylus and head receiver are connected properly. 
```
connector = FastrakConnector(usb_port='/dev/cu.usbserial-110')
connector.prepare_for_digitisation()
```

The next step is to setup the digitiser object and add any points you would like to digitise
```
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
```
digitiser.run_digitisation()
digitiser.save_digitisation(output_path='insert/your/path/here.csv')
```

Note on dig_type argument in the Digtiser.add() function:
- `continuous`: Takes a category (for example "OPM") and a list of labels (["FL1", "FL2", "FL3"]). Thus this function is useful for marking marking points with a label attached to them (i.e. if you need to know which specific sensor or fiducial). If you want to re-digtise a point just press the stylus 30 cm away from the head. 
- `single`: Used for marking a specified amount of points with out any specific label. This could for example be 60 points distributed across the head of the participant. This function allows to keep the button of the stylus pressed down continuosly to mark consecutive points. 

The digitisation will be shown using matplotlib - however sometimes the plot takes a bit to update, and the plot does not show until the first point is made


## Co-registration
TBD

## 🥼 In the lab
1. Metal strip participant
2. Put on EEG cap
3. Gel electrodes
4. Check impedances
5. Go to the MSR and place them in the helmet
6. Put in dummy sensors
7. Put on chin strap
8. Mark OPMs with felt pen
9. Measure Z depth of sensors -> may be useful as a sanity check but not needed in the current pipeline
10. Run experiment
11. Remove participant from MSR
12. Digitise (fiducials, OPM-felt pen markers, EEG electrodes, facial features for co-registration with MR)



## Potential future work
### Continuous measurement of head-position 
* HPI in EEG cap (or on head)
* Place EEG sensors on the Fieldline helmet 
* Use EEG sensors on helmet to get the HPI fit

Benefit of using EEG sensors is that their bandwidth larger than that of the OPMs
