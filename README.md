# OPM_lab
Under development. This repository holds a module for integrating the rigid helmet from FieldLine for OPMs with `mne-python` software.

## To do
- [ ] Find information about sensor locations in the helmet + figure out how to measure how deep the sensors are pushed into the slots
- [X] Figure out how to modify sensor locations for `Raw` in MNE - likely something similar to what was done for [bsc thesis](https://github.com/laurabpaulsen/decodingMEG/blob/main/source_reconstruction/epochs_2_source_space.py)
- [ ] Figure out how to get sensor locations from Fieldline helmet
- [ ] Calculate device to head (or head to device) transformation


## Inspiration
* Videos from [NatMEG on-scalp MEG symposium 2022](https://natmeg.se/activities/on-scalp-meg-symposium-2022.html)
* [On-scalp MEG sensor localization using magnetic dipole-like coils: A method
for highly accurate co-registration](https://www.sciencedirect.com/science/article/pii/S1053811920301737)