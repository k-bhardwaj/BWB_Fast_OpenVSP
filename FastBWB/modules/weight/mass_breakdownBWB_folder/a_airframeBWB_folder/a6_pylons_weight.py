"""
Estimation of pylons weight - A6 COMPONENT
---------------------------------------------
- Registered under the name "fastoad.submodel.weight.mass.airframe.pylons.BWBtest.1"
A6 computed analytically

"""

import numpy as np
import openmdao.api as om
from fastoad.module_management.service_registry import RegisterSubmodel

from .constants import SERVICE_PYLONS_MASS


@RegisterSubmodel(SERVICE_PYLONS_MASS, "fastoad.submodel.weight.mass.airframe.pylons.BWBtest.1")
class PylonsWeight(om.ExplicitComponent):
    """
    Weight estimation for pylons

    Based on formula in :cite:`supaero:2014`, mass contribution A6
    """

    def setup(self):
        self.add_input("data:geometry:propulsion:pylon:wetted_area", val=np.nan, units="m**2")
        self.add_input("data:geometry:propulsion:layout", val=np.nan)
        self.add_input("data:weight:propulsion:engine:mass", val=np.nan, units="kg")
        self.add_input("data:geometry:propulsion:engine:count", val=np.nan)
        self.add_input("tuning:weight:airframe:pylon:mass:k", val=1.0)
        self.add_input("tuning:weight:airframe:pylon:mass:offset", val=0.0, units="kg")

        self.add_output("data:weight:airframe:pylon:mass", units="kg")

    def setup_partials(self):
        self.declare_partials("*", "*", method="fd")

    def compute(self, inputs, outputs, discrete_inputs=None, discrete_outputs=None):
        wet_area_pylon = inputs["data:geometry:propulsion:pylon:wetted_area"]
        weight_engine = inputs["data:weight:propulsion:engine:mass"]
        n_engines = inputs["data:geometry:propulsion:engine:count"]
        k_a6 = inputs["tuning:weight:airframe:pylon:mass:k"]
        offset_a6 = inputs["tuning:weight:airframe:pylon:mass:offset"]
        propulsion_layout = np.round(inputs["data:geometry:propulsion:layout"])

        if propulsion_layout == 1.0:
            temp_a6 = (
                1.2
                * wet_area_pylon**0.5
                * n_engines
                * (23 + 0.588 * (weight_engine / n_engines) ** 0.708)
            )
        else:
            temp_a6 = 0.08 * weight_engine

        outputs["data:weight:airframe:pylon:mass"] = k_a6 * temp_a6 + offset_a6
