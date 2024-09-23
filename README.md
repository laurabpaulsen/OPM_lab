# OPM_lab
Under development. This repository holds a module for integrating the (semi)-rigid helmet from FieldLine for OPMs with `mne-python` software and polhemus fastrak digitiser


# Usage

## 🥼 In the lab
1. Metal strip participant
2. Put on EEG cap
3. In MSR and helmet
4. Put in dummy sensors
5. Mark OPMs with felt pen
6. Mark on MEG chair level
7. Mark on face and helmet
8. Remove participant from MSR
9. Digitise (fiducials, OPM-felt pen markers, EEG electrodes, facial features for co-registration with MR)
10. Gel electrodes
11. Check impedances
12. Return to MSR
13. Align chair level and face marks 
14. Put on chin strap
15. Measure Z depth (is this actually useful if we do not have any digitisation of how the head is in the helmet?)


## 👩‍💻 Code 



## To do
- [ ] Device coordinates: Find information about sensor locations in the helmet + figure out how to measure how deep the sensors are pushed into the sockets
- [X] Figure out how to modify sensor locations for `Raw` in MNE - likely something similar to what was done for [bsc thesis](https://github.com/laurabpaulsen/decodingMEG/blob/main/source_reconstruction/epochs_2_source_space.py)


## Inspiration
* Videos from [NatMEG on-scalp MEG symposium 2022](https://natmeg.se/activities/on-scalp-meg-symposium-2022.html)
* [On-scalp MEG sensor localization using magnetic dipole-like coils: A method
for highly accurate co-registration](https://www.sciencedirect.com/science/article/pii/S1053811920301737)
* [Fieldtrip tutorial on co-registration](https://www.fieldtriptoolbox.org/tutorial/coregistration_opm/)
* Fieldtrip has some [gradiometer templates](https://github.com/fieldtrip/fieldtrip/tree/master/template/gradiometer) (matlab) that may be useful if any of them match the helmet 


## Notes

**Reference layout** 
* Each of the sensors location relative to each other
* Can improve localisation over solving the equation for each sensor individually
* Should be able to get from helmet documentation

**Bandwidth**
* Question: what is the bandwidth (Hz) for the OPMs we have? Can they measure outside of the signal we are interested in, or do we need to take into account that we can only measure HPI signals before/after/in breaks?
