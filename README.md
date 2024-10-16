# OPM_lab
Under development. This repository holds a module for integrating the (semi)-rigid helmet from FieldLine for OPMs with `mne-python` software and polhemus fastrak digitiser


# Usage

## 👩‍💻 Code
## Polhemus digitisation
To digtise using this module, you need to make sure you have the `OPM_lab` directory which contains files with functions you will need.

In the `src/digitise_example.py` you will find an example of how to setup the code for running the digitisation. Two main functions are used:
- `mark_sensors`: This function takes a sensor type (for example "OPM") and a list of sensor labels (["FL1", "FL2", "FL3"]). Thus this function is useful for marking marking points with a label attached to them (i.e. if you need to know which specific sensor or fiducial). If you want to re-digtise a point just press the stylus 30 cm away from the head. 
- `mark_headshape`: Used for marking a specified amount of points with out any specific label. This could for example be 60 points distributed across the head of the participant. This function allows to keep the button of the stylus pressed down continuosly to mark consecutive points. 

The digitisation will be shown using matplotlib - however sometimes the plot takes a bit to update, and the plot does not show until the first point is made


## Co-registration
TBD

## 🥼 In the lab
1. Metal strip participant
2. Put on EEG cap
3. Go to the MSR and place them in the helmet
4. Put in dummy sensors
5. Mark OPMs with felt pen
6. Mark on MEG chair level
7. Mark on face and helmet to ensure ability to return to same position
8. Remove participant from MSR
9. Digitise (fiducials, OPM-felt pen markers, EEG electrodes, facial features for co-registration with MR)
10. Gel electrodes
11. Check impedances
12. Return to MSR
13. Align chair level and face marks 
14. Put on chin strap
15. Measure Z depth of sensors -> may be useful as a sanity check but not needed in the current pipeline




## Potential future work
### Continuous measurement of head-position 
* HPI in EEG cap (or on head)
* Place EEG sensors on the Fieldline helmet 
* Use EEG sensors on helmet to get the HPI fit

Benefit of using EEG sensors is that their bandwidth larger than that of the OPMs
