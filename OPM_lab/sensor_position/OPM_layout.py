import numpy as np 
from .helmet_layout import HelmetTemplate
from mne.utils._bunch import NamedInt
from .template_base import TemplateBase

class OPMSensorLayout(TemplateBase):
    def __init__(self, label:list[str], depth:list[float], helmet_template:HelmetTemplate, coil_type:NamedInt = NamedInt("FieldLine OPM sensor Gen1 size = 2.00   mm", 8101)):
        """
        Represents the layout of an Optically Pumped Magnetometer (OPM) sensor array
        within a helmet template. This layout uses orientation and depth measurements to
        position sensors on a helmet model, adjusting their locations according to 
        measured depth and orientation.

        Parameters
        ----------
        label : list[str]
            The labels of the sensors, used to identify it in the helmet template (as all sensors slots may not be used).
        depth : list[float]
            A list of depth measurements in mm for channel, affecting sensor 
            positioning within the template.
        helmet_template : HelmetTemplate
            An instance of the HelmetTemplate class, providing the base template for
            sensor positioning and orientation.
        coil_type : NamedInt, optional
            The coil type of the OPM, specified as a NamedInt. Default is 
            NamedInt("FieldLine OPM sensor Gen1 size = 2.00 mm", 8101).

        Attributes
        ----------
        label : list[str]
            The labels identifying the sensor in the template.
        depth : list[float]
            Depth measurements.
        helmet_template : HelmetTemplate
            The helmet template providing OPM position and orientation.
        unit : str
            The unit of measurement from the helmet template.
        coil_type : NamedInt
            The coil type associated with the channel (see https://github.com/mne-tools/mne-python/blob/main/mne/data/coil_def.dat).
        chan_pos : np.ndarray
            Array containing the transformed channel positions after accounting for depth measurement
        chan_ori : list
            List of orientation vectors for each channel.
        """

        #self.label = label
        self.depth = depth
        self.helmet_template = helmet_template
        #self.unit = self.
        self.coil_type = coil_type
        chan_pos, self.chan_ori = self.make_sensor_layout(label)
        super().__init__(label, helmet_template.unit, chan_pos)

    def make_sensor_layout(self, labels):
        chan_pos = self.transform_template_depth(labels)
        chan_ori = self.helmet_template.get_chs_ori(labels)
        return chan_pos, chan_ori

    
    def transform_template_depth(self, labels): #len_sleeve:float = 75/1000, offset:float = 13/1000
        template_ori = self.helmet_template.get_chs_ori(labels)
        template_pos = self.helmet_template.get_chs_pos(labels)
        
        # Create a new list to store the updated positions
        transformed_pos = []
        
        # Move template pos by measurement length in template ori direction
        for pos, ori, depth in zip(template_pos, template_ori, self.depth):
            updated_depth = (52-depth)/1000
            x = (pos[0] - (updated_depth* ori[2,0]))
            y = (pos[1] - (updated_depth* ori[2,1]))
            z = pos[2] + (updated_depth * ori[2,2])

            transformed_pos.append([x, y, z])
        
        return np.array(transformed_pos)

    def get_chs_ori(self, labels: list[str]=None):
        return self._get_attributes_by_labels(labels, 'chan_ori')
    