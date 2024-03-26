"""
Estimation of navigation systems weight - C3 component
---------------------------------------------
- Registered under the name "fastoad.submodel.weight.mass.systems.navigation.BWBtest.1"
C3 computed analytically according to range from TLARs and fuselage length

 """
import numpy as np
import openmdao.api as om
from fastoad.constants import RangeCategory
from fastoad.module_management.service_registry import RegisterSubmodel

from .constants import SERVICE_NAVIGATION_SYSTEMS_MASS


@RegisterSubmodel(
    SERVICE_NAVIGATION_SYSTEMS_MASS, "fastoad.submodel.weight.mass.systems.navigation.BWBtest.1"
)
class NavigationSystemsWeight(om.ExplicitComponent):
    """
    Weight estimation for navigation systems

    Based on figures in :cite:`supaero:2014`, mass contribution C3
    """

    def setup(self):
        self.add_input("data:TLAR:range", val=np.nan, units="NM")
        self.add_input("data:geometry:fuselage:length", val=np.nan, units="m")
        self.add_input("data:geometry:wing:b_50", val=np.nan, units="m")
        self.add_input("tuning:weight:systems:navigation:mass:k", val=1.0)
        self.add_input("tuning:weight:systems:navigation:mass:offset", val=0.0, units="kg")

        self.add_output("data:weight:systems:navigation:mass", units="kg")

    def setup_partials(self):
        self.declare_partials("*", "*", method="fd")

    def compute(self, inputs, outputs, discrete_inputs=None, discrete_outputs=None):
        tlar_range = inputs["data:TLAR:range"]
        fuselage_length = inputs["data:geometry:fuselage:length"]
        b_50 = inputs["data:geometry:wing:b_50"]
        k_c3 = inputs["tuning:weight:systems:navigation:mass:k"]
        offset_c3 = inputs["tuning:weight:systems:navigation:mass:offset"]

        if tlar_range in RangeCategory.SHORT:
            base_weight = 150.0
        elif tlar_range in RangeCategory.SHORT_MEDIUM:
            base_weight = 450.0
        elif tlar_range in RangeCategory.MEDIUM:
            base_weight = 700.0
        else:
            base_weight = 800.0

        temp_c3 = base_weight + 0.033 * fuselage_length * b_50
        outputs["data:weight:systems:navigation:mass"] = k_c3 * temp_c3 + offset_c3
