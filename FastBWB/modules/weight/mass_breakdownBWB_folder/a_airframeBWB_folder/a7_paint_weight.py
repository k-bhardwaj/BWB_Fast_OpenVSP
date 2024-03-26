"""
Estimation of paint weight - A7 COMPONENT
---------------------------------------------
- Registered under the name "fastoad.submodel.weight.mass.airframe.paint.BWBtest.1"
A7 computed analytically taking into account total wetted area

"""

import numpy as np
import openmdao.api as om
from fastoad.module_management.service_registry import RegisterSubmodel

from .constants import SERVICE_PAINT_MASS


@RegisterSubmodel(SERVICE_PAINT_MASS, "fastoad.submodel.weight.mass.airframe.paint.BWBtest.1")
class PaintWeight(om.ExplicitComponent):
    """
    Weight estimation for paint

    Based on formula in :cite:`supaero:2014`, mass contribution A7
    """

    def setup(self):
        self.add_input("data:geometry:aircraft:wetted_area", val=np.nan, units="m**2")
        self.add_input("tuning:weight:airframe:paint:mass:k", val=1.0)
        self.add_input("tuning:weight:airframe:paint:mass:offset", val=0.0, units="kg")

        self.add_output("data:weight:airframe:paint:mass", units="kg")

    def setup_partials(self):
        self.declare_partials("*", "*", method="fd")

    def compute(self, inputs, outputs, discrete_inputs=None, discrete_outputs=None):
        total_wet_surface = inputs["data:geometry:aircraft:wetted_area"]
        k_a7 = inputs["tuning:weight:airframe:paint:mass:k"]
        offset_a7 = inputs["tuning:weight:airframe:paint:mass:offset"]

        temp_a7 = 0.180 * total_wet_surface
        outputs["data:weight:airframe:paint:mass"] = k_a7 * temp_a7 + offset_a7
