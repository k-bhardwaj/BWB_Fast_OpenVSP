"""
Estimation of unconsumables weight - B3 component
---------------------------------------------
- Registered under the name "fastoad.submodel.weight.mass.propulsion.unconsumables.BWBtest.1"
B3 computed analytically according to number of engines and MFW.

"""

import numpy as np
import openmdao.api as om
from fastoad.module_management.service_registry import RegisterSubmodel

from .constants import SERVICE_UNCONSUMABLES_MASS_BWB


@RegisterSubmodel(
    SERVICE_UNCONSUMABLES_MASS_BWB, "fastoad.submodel.weight.mass.propulsion.unconsumables.BWBtest.1"
)
class UnconsumablesWeight(om.ExplicitComponent):
    """
    Weight estimation for oil and unusable fuel

    Based on formula in :cite:`supaero:2014`, mass contribution B3
    """

    def setup(self):
        self.add_input("data:geometry:propulsion:engine:count", val=np.nan)
        self.add_input("data:weight:aircraft:MFW", val=np.nan, units="kg")
        self.add_input("tuning:weight:propulsion:unconsumables:mass:k", val=1.0)
        self.add_input("tuning:weight:propulsion:unconsumables:mass:offset", val=0.0, units="kg")

        self.add_output("data:weight:propulsion:unconsumables:mass", units="kg")

    def setup_partials(self):
        self.declare_partials("*", "*", method="fd")

    def compute(self, inputs, outputs, discrete_inputs=None, discrete_outputs=None):
        n_engines = inputs["data:geometry:propulsion:engine:count"]
        mfw = inputs["data:weight:aircraft:MFW"]
        k_b3 = inputs["tuning:weight:propulsion:unconsumables:mass:k"]
        offset_b3 = inputs["tuning:weight:propulsion:unconsumables:mass:offset"]

        temp_b3 = 25 * n_engines + 0.0035 * mfw
        outputs["data:weight:propulsion:unconsumables:mass"] = k_b3 * temp_b3 + offset_b3
