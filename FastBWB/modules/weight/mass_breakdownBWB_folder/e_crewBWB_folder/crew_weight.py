"""
Estimation of crew weight - D1 component
---------------------------------------------
- Registered under the name "fastoad.submodel.weight.mass.crew.BWBtest.1"
Depends on cockpit crew and cabin crew

 """

import numpy as np
import openmdao.api as om
from fastoad.module_management.service_registry import RegisterSubmodel

from ..constants import SERVICE_CREW_MASS


@RegisterSubmodel(SERVICE_CREW_MASS, "fastoad.submodel.weight.mass.crew.BWBtest.1")
class CrewWeight(om.ExplicitComponent):
    """
    Weight estimation for aircraft crew

    Based on :cite:`supaero:2014`, mass contribution E
    """

    def setup(self):
        self.add_input("data:geometry:cabin:crew_count:technical", val=np.nan)
        self.add_input("data:geometry:cabin:crew_count:commercial", val=np.nan)

        self.add_output("data:weight:crew:mass", units="kg")

    def setup_partials(self):
        self.declare_partials("*", "*", method="fd")

    def compute(self, inputs, outputs, discrete_inputs=None, discrete_outputs=None):
        cockpit_crew = inputs["data:geometry:cabin:crew_count:technical"]
        cabin_crew = inputs["data:geometry:cabin:crew_count:commercial"]

        outputs["data:weight:crew:mass"] = 85 * cockpit_crew + 75 * cabin_crew
