"""
Estimation of fuel lines weight - B2 component
---------------------------------------------
- Registered under the name "fastoad.submodel.weight.mass.propulsion.fuel_lines.BWBtest.1"
B2 computed analytically according to engines mass, b50 geometrical variable and MFW.

"""

import numpy as np
import openmdao.api as om
from fastoad.module_management.service_registry import RegisterSubmodel

from .constants import SERVICE_FUEL_LINES_MASS_BWB


@RegisterSubmodel(
    SERVICE_FUEL_LINES_MASS_BWB, "fastoad.submodel.weight.mass.propulsion.fuel_lines.BWBtest.1"
)
class FuelLinesWeight(om.ExplicitComponent):
    """
    Weight estimation for fuel lines

    Based on formula in :cite:`supaero:2014`, mass contribution B2
    """

    def setup(self):
        self.add_input("data:geometry:wing:b_50", val=np.nan, units="m")
        self.add_input("data:weight:aircraft:MFW", val=np.nan, units="kg")
        self.add_input("data:weight:propulsion:engine:mass", val=np.nan, units="kg")
        self.add_input("tuning:weight:propulsion:fuel_lines:mass:k", val=1.0)
        self.add_input("tuning:weight:propulsion:fuel_lines:mass:offset", val=0.0, units="kg")

        self.add_output("data:weight:propulsion:fuel_lines:mass", units="kg")

    def setup_partials(self):
        self.declare_partials("*", "*", method="fd")

    def compute(self, inputs, outputs, discrete_inputs=None, discrete_outputs=None):
        b_50 = inputs["data:geometry:wing:b_50"]
        mfw = inputs["data:weight:aircraft:MFW"]
        k_b2 = inputs["tuning:weight:propulsion:fuel_lines:mass:k"]
        offset_b2 = inputs["tuning:weight:propulsion:fuel_lines:mass:offset"]
        weight_engines = inputs["data:weight:propulsion:engine:mass"]

        temp_b2 = 0.02 * weight_engines + 2.0 * b_50 + 0.35 * mfw**0.66
        outputs["data:weight:propulsion:fuel_lines:mass"] = k_b2 * temp_b2 + offset_b2
