"""
Estimation of flight controls weight - A4 COMPONENT
---------------------------------------------
- Registered under the name "fastoad.submodel.weight.mass.airframe.flight_control.BWBtest.1"
A4 computed from analytical formula

"""

import numpy as np
import openmdao.api as om
from fastoad.module_management.service_registry import RegisterSubmodel

from .constants import SERVICE_FLIGHT_CONTROLS_MASS


@RegisterSubmodel(
    SERVICE_FLIGHT_CONTROLS_MASS, "fastoad.submodel.weight.mass.airframe.flight_control.BWBtest.1"
)
class FlightControlsWeight(om.ExplicitComponent):
    """
    Flight controls weight estimation

    Based on formulas in :cite:`supaero:2014`, mass contribution A4
    """

    def setup(self):
        self.add_input("data:geometry:fuselage:length", val=np.nan, units="m")
        self.add_input("data:geometry:wing:b_50", val=np.nan, units="m")
        self.add_input("data:mission:sizing:cs25:sizing_load_1", val=np.nan, units="kg")
        self.add_input("data:mission:sizing:cs25:sizing_load_2", val=np.nan, units="kg")
        self.add_input(
            "settings:weight:airframe:flight_controls:mass:k_fc", val=0.85
        )  # FIXME: this one should depend on a boolan electric/not-electric flight_controls
        self.add_input("tuning:weight:airframe:flight_controls:mass:k", val=1.0)
        self.add_input("tuning:weight:airframe:flight_controls:mass:offset", val=0.0, units="kg")

        self.add_output("data:weight:airframe:flight_controls:mass", units="kg")

    def setup_partials(self):
        self.declare_partials("*", "*", method="fd")

    def compute(self, inputs, outputs, discrete_inputs=None, discrete_outputs=None):
        fus_length = inputs["data:geometry:fuselage:length"]
        b_50 = inputs["data:geometry:wing:b_50"]
        k_fc = inputs["settings:weight:airframe:flight_controls:mass:k_fc"]
        k_a4 = inputs["tuning:weight:airframe:flight_controls:mass:k"]
        offset_a4 = inputs["tuning:weight:airframe:flight_controls:mass:offset"]

        max_nm = max(
            inputs["data:mission:sizing:cs25:sizing_load_1"],
            inputs["data:mission:sizing:cs25:sizing_load_2"],
        )

        temp_a4 = k_fc * max_nm * (fus_length**0.66 + b_50**0.66)

        outputs["data:weight:airframe:flight_controls:mass"] = k_a4 * temp_a4 + offset_a4
