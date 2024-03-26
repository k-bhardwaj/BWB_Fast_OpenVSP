"""
Payload mass computation
-----------------------------------------------------------
This file is in charge of computing the payload PL and the
maximum payload PL_max of the aircraft. It takes into account 
the number of passengers NPAX from the TLARS and the the max 
estimated mass per passenger. 
It is registered under the name "fastoad.submodel.weight.mass.payload.legacy.2".

"""
import numpy as np
from fastoad.module_management.service_registry import RegisterSubmodel
from openmdao import api as om

from .constants import SERVICE_PAYLOAD_MASS


@RegisterSubmodel(SERVICE_PAYLOAD_MASS, "fastoad.submodel.weight.mass.payload.legacy.2")
class ComputePayload(om.ExplicitComponent):
    """Computes payload from NPAX"""

    def setup(self):
        self.add_input("data:TLAR:NPAX", val=np.nan)
        self.add_input(
            "settings:weight:aircraft:payload:design_mass_per_passenger",
            val=90.72,
            units="kg",
            desc="Design value of mass per passenger",
        )
        self.add_input(
            "settings:weight:aircraft:payload:max_mass_per_passenger",
            val=130.72,
            units="kg",
            desc="Maximum value of mass per passenger",
        )

        self.add_output("data:weight:aircraft:payload", units="kg")
        self.add_output("data:weight:aircraft:max_payload", units="kg")

    def setup_partials(self):
        self.declare_partials("*", "*", method="fd")

    def compute(self, inputs, outputs, discrete_inputs=None, discrete_outputs=None):
        npax = inputs["data:TLAR:NPAX"]
        mass_per_pax = inputs["settings:weight:aircraft:payload:design_mass_per_passenger"]
        max_mass_per_pax = inputs["settings:weight:aircraft:payload:max_mass_per_passenger"]

        outputs["data:weight:aircraft:payload"] = npax * mass_per_pax
        outputs["data:weight:aircraft:max_payload"] = npax * max_mass_per_pax
