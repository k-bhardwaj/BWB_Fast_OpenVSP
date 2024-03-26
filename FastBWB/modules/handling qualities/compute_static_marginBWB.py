"""
Estimation of the static margin
----------------------------------------------
This file obtains the static margin. The group is named
"fastoad.handling_qualities.static_margin.TEST". It is computed 
by doing the difference between the CG ratio and the neutral point.
The objective is to obtain a static margin between 0.05 and 0.10. 
In this case, the target is fixed at 0.05.

Note: Normally the Handling Qualities folder is also in charge of 
performing the tail sizing. However, for the case of the BWB 
configuration analysed (tailess), this part was not considered. 
"""

import numpy as np
import openmdao.api as om

from fastoad.module_management.constants import ModelDomain
from fastoad.module_management.service_registry import RegisterOpenMDAOSystem


@RegisterOpenMDAOSystem(
    "fastoad.handling_qualities.static_margin.TEST", domain=ModelDomain.HANDLING_QUALITIES
)
class ComputeStaticMargin(om.ExplicitComponent):
    """
    Computation of static margin i.e. difference between CG ratio and neutral
    point.
    """

    def initialize(self):
        self.options.declare("target", types=float, allow_none=True, default=None)

    def setup(self):
        self.add_input("data:weight:aircraft:CG:aft:MAC_position", val=np.nan)
        self.add_input("data:aerodynamics:cruise:neutral_point:x", val=np.nan)

        self.add_output("data:handling_qualities:static_margin")

    def setup_partials(self):
        self.declare_partials("*", "*", method="fd")

    def compute(self, inputs, outputs, discrete_inputs=None, discrete_outputs=None):
        cg_ratio = inputs["data:weight:aircraft:CG:aft:MAC_position"]
        ac_ratio = inputs["data:aerodynamics:cruise:neutral_point:x"]
     
        outputs["data:handling_qualities:static_margin"] = ac_ratio - cg_ratio
