"""
Estimation of fuselage weight - A2 COMPONENT
---------------------------------------------
- Registered under the name "fastoad.submodel.weight.mass.airframe.fuselage.BWBtest.1"
A2 computed from analytical formula.

"""

import numpy as np
import openmdao.api as om
from fastoad.module_management.service_registry import RegisterSubmodel

from .constants import SERVICE_FUSELAGE_MASS


@RegisterSubmodel(SERVICE_FUSELAGE_MASS, "fastoad.submodel.weight.mass.airframe.fuselage.BWBtest.1")
class FuselageWeight(om.ExplicitComponent):
    """
    Fuselage weight estimation

    Based on a statistical analysis. See :cite:`supaero:2014`, mass contribution A2
    """

    def setup(self):
        self.add_input("data:geometry:fuselage:wetted_area", val=np.nan, units="m**2")
        self.add_input("data:geometry:fuselage:maximum_width", val=np.nan, units="m")
        self.add_input("data:geometry:fuselage:maximum_height", val=np.nan, units="m")
        self.add_input("data:mission:sizing:cs25:sizing_load_1", val=np.nan, units="kg")
        self.add_input("tuning:weight:airframe:fuselage:mass:k", val=1.0)
        self.add_input("tuning:weight:airframe:fuselage:mass:offset", val=0.0, units="kg")
        self.add_input("settings:weight:airframe:fuselage:mass:k_lg", val=1.05)
        self.add_input("settings:weight:airframe:fuselage:mass:k_fus", val=1.0)
        self.add_input("data:weight:aircraft:MTOW", val=np.nan, units="kg")
        #self.add_input("data:weight:aircraft:MTOW", val=1.0) # for bwb

        self.add_output("data:weight:airframe:fuselage:mass", units="kg")

    def setup_partials(self):
        self.declare_partials("*", "*", method="fd")

    def compute(self, inputs, outputs, discrete_inputs=None, discrete_outputs=None):
        fuselage_wet_area = inputs["data:geometry:fuselage:wetted_area"]
        width_max = inputs["data:geometry:fuselage:maximum_width"]
        height_max = inputs["data:geometry:fuselage:maximum_height"]
        n1m1 = inputs["data:mission:sizing:cs25:sizing_load_1"]
        k_a2 = inputs["tuning:weight:airframe:fuselage:mass:k"]
        offset_a2 = inputs["tuning:weight:airframe:fuselage:mass:offset"]
        k_lg = inputs["settings:weight:airframe:fuselage:mass:k_lg"]
        k_fus = inputs["settings:weight:airframe:fuselage:mass:k_fus"]
        # TUBE AND WING
        temp_a2 = (
            fuselage_wet_area
            * (10 + 1.2 * np.sqrt(width_max * height_max) + 0.00019 * n1m1 / height_max**1.7)
            * k_lg
            * k_fus
        )
        # BWB
        # cabin_area = fuselage_wet_area
        ks = 30 # from <K_s>30</K_s> 
        mtow = inputs["data:weight:aircraft:MTOW"]

        temp_a2BWB = 0.316422 * ks * mtow ** 0.166552 * fuselage_wet_area ** 1.061158
        outputs["data:weight:airframe:fuselage:mass"] = k_a2 * temp_a2BWB + offset_a2
