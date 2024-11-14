import mne
import numpy as np
from .template_base import TemplateBase

class EEGcapTemplate(TemplateBase):
    def __init__(self, montage:str):
        self.montage = montage
        self.chan_pos, self.label, self.unit = self.get_montage_information()
        super().__init__(self.label, self.unit)
    
    def get_montage_information(self):

        mne_montage = mne.channels.make_standard_montage(self.montage)

        positions = []

        for digpoint in mne_montage.dig:
            if digpoint["kind"]==3: # if it is EEG 
                positions.append(digpoint["r"])        

        return np.array(positions), mne_montage.ch_names, "mm"