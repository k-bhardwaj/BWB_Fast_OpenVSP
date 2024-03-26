"""
Estimation of security kit weight - D4 component
---------------------------------------------
- Registered under the name "service.mass.furniture.security_kit.BWBtest.1"

 """

import numpy as np
import openmdao.api as om
from fastoad.module_management.service_registry import RegisterSubmodel

from .constants import SERVICE_SECURITY_KIT_MASS


@RegisterSubmodel(SERVICE_SECURITY_KIT_MASS, "service.mass.furniture.security_kit.BWBtest.1")
class SecurityKitWeight(om.ExplicitComponent):
    """
    Weight estimation for security kit

    Based on :cite:`supaero:2014`, mass contribution D4
    """

    """ Passenger security kit weight estimation (D4) """

    def setup(self):
        self.add_input("data:TLAR:NPAX", val=np.nan)
        self.add_input("tuning:weight:furniture:security_kit:mass:k", val=1.0)
        self.add_input("tuning:weight:furniture:security_kit:mass:offset", val=0.0, units="kg")

        self.add_output("data:weight:furniture:security_kit:mass", units="kg")

    def setup_partials(self):
        self.declare_partials("*", "*", method="fd")

    def compute(self, inputs, outputs, discrete_inputs=None, discrete_outputs=None):
        npax = inputs["data:TLAR:NPAX"]
        k_d4 = inputs["tuning:weight:furniture:security_kit:mass:k"]
        offset_d4 = inputs["tuning:weight:furniture:security_kit:mass:offset"]

        temp_d4 = 1.5 * npax
        outputs["data:weight:furniture:security_kit:mass"] = k_d4 * temp_d4 + offset_d4
