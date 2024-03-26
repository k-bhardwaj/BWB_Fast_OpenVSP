"""
Estimation of empennage weight - A3 COMPONENT
---------------------------------------------
- Registered under the name "fastoad.submodel.weight.mass.airframe.empennage.BWBtest.1"
A31 = horizontal tail (for BWB configuration = 0)
A32 = vertical tail

"""

import numpy as np
import openmdao.api as om
from fastoad.module_management.service_registry import RegisterSubmodel

from .constants import SERVICE_EMPENNAGE_MASS


@RegisterSubmodel(SERVICE_EMPENNAGE_MASS, "fastoad.submodel.weight.mass.airframe.empennage.BWBtest.1")
class EmpennageWeight(om.ExplicitComponent):
    """
    Weight estimation for tail planes

    Based on formulas in :cite:`supaero:2014`, mass contribution A3
    """

    def setup(self):
        self.add_input("data:geometry:has_T_tail", val=np.nan)
        self.add_input("data:geometry:horizontal_tail:area", val=np.nan, units="m**2")
        self.add_input("data:geometry:vertical_tail:area", val=np.nan, units="m**2")
        self.add_input("data:geometry:propulsion:layout", val=np.nan)
        self.add_input("tuning:weight:airframe:horizontal_tail:mass:k", val=1.0)
        self.add_input("tuning:weight:airframe:horizontal_tail:mass:offset", val=0.0, units="kg")
        self.add_input("tuning:weight:airframe:vertical_tail:mass:k", val=1.0)
        self.add_input("tuning:weight:airframe:vertical_tail:mass:offset", val=0.0, units="kg")

        self.add_output("data:weight:airframe:horizontal_tail:mass", units="kg")
        self.add_output("data:weight:airframe:vertical_tail:mass", units="kg")

    def setup_partials(self):
        self.declare_partials("*", "*", method="fd")

    # pylint: disable=too-many-locals
    def compute(self, inputs, outputs, discrete_inputs=None, discrete_outputs=None):
        ht_area = inputs["data:geometry:horizontal_tail:area"]
        vt_area = inputs["data:geometry:vertical_tail:area"]
        k_a31 = inputs["tuning:weight:airframe:horizontal_tail:mass:k"]
        offset_a31 = inputs["tuning:weight:airframe:horizontal_tail:mass:offset"]
        k_a32 = inputs["tuning:weight:airframe:vertical_tail:mass:k"]
        offset_a32 = inputs["tuning:weight:airframe:vertical_tail:mass:offset"]
        propulsion_layout = np.round(inputs["data:geometry:propulsion:layout"])
        tail_type = np.round(inputs["data:geometry:has_T_tail"])

        k_tail = 1.3 if tail_type == 1 else 1.0

        # Mass of the horizontal tail plane
        temp_a31 = ht_area * (14.4 + 0.155 * ht_area) * k_tail
        outputs["data:weight:airframe:horizontal_tail:mass"] = k_a31 * temp_a31 + offset_a31

        # Mass of the vertical tail plane
        k_engine = 1 if propulsion_layout == 1.0 else 1.5

        temp_a32 = vt_area * (15.45 + 0.202 * vt_area) * k_engine * k_tail
        outputs["data:weight:airframe:vertical_tail:mass"] = k_a32 * temp_a32 + offset_a32
