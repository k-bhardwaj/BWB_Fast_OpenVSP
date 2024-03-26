"""
Estimation of landing gears weight - A5 COMPONENT
---------------------------------------------
- Registered under the name "fastoad.submodel.weight.mass.airframe.landing_gears.BWBtest.1"
A51 = main landing gear
A52 = front landing gear
Computed analytically

"""
import numpy as np
import openmdao.api as om
from fastoad.module_management.service_registry import RegisterSubmodel

from .constants import SERVICE_LANDING_GEARS_MASS


@RegisterSubmodel(
    SERVICE_LANDING_GEARS_MASS, "fastoad.submodel.weight.mass.airframe.landing_gears.BWBtest.1"
)
class LandingGearWeight(om.ExplicitComponent):
    """
    Weight estimation for landing gears

    Based on formulas in :cite:`supaero:2014`, mass contribution A5
    """

    def setup(self):
        self.add_input("data:weight:aircraft:MTOW", val=np.nan, units="kg")
        self.add_input("tuning:weight:airframe:landing_gear:mass:k", val=1.0)
        self.add_input("tuning:weight:airframe:landing_gear:mass:offset", val=0.0, units="kg")

        self.add_output("data:weight:airframe:landing_gear:main:mass", units="kg")
        self.add_output("data:weight:airframe:landing_gear:front:mass", units="kg")

    def setup_partials(self):
        self.declare_partials("*", "*", method="fd")

    def compute(self, inputs, outputs, discrete_inputs=None, discrete_outputs=None):
        mtow = inputs["data:weight:aircraft:MTOW"]
        k_a5 = inputs["tuning:weight:airframe:landing_gear:mass:k"]
        offset_a5 = inputs["tuning:weight:airframe:landing_gear:mass:offset"]

        temp_a51 = 18.1 + 0.131 * mtow**0.75 + 0.019 * mtow + 2.23e-5 * mtow**1.5
        temp_a52 = 9.1 + 0.082 * mtow**0.75 + 2.97e-6 * mtow**1.5

        a51 = k_a5 * temp_a51 + offset_a5
        a52 = k_a5 * temp_a52 + offset_a5

        outputs["data:weight:airframe:landing_gear:main:mass"] = a51
        outputs["data:weight:airframe:landing_gear:front:mass"] = a52
