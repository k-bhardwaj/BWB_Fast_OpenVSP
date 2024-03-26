"""
Estimation of vertical tail center of gravity (CG_A32)
------------------------------------------
This file calculates the absolute CG of the VT.

"""

import math

import numpy as np
import openmdao.api as om
from fastoad.module_management.service_registry import RegisterSubmodel

from ..constantscg import SERVICE_VERTICAL_TAIL_CG


@RegisterSubmodel(SERVICE_VERTICAL_TAIL_CG, "fastoad.submodel.weight.cg.vertical_tail.BWBtest.1")
class ComputeVTcg(om.ExplicitComponent):
    # TODO: Document equations. Cite sources
    """Vertical tail center of gravity estimation"""

    def setup(self):
        self.add_input("data:geometry:vertical_tail:MAC:length", val=np.nan, units="m")
        self.add_input("data:geometry:vertical_tail:root:chord", val=np.nan, units="m")
        self.add_input("data:geometry:vertical_tail:tip:chord", val=np.nan, units="m")
        self.add_input(
            "data:geometry:vertical_tail:MAC:at25percent:x:from_wingMAC25", val=np.nan, units="m"
        )
        self.add_input("data:geometry:vertical_tail:MAC:at25percent:x:local", val=np.nan, units="m")
        self.add_input("data:geometry:vertical_tail:sweep_25", val=np.nan, units="deg")
        self.add_input("data:geometry:vertical_tail:span", val=np.nan, units="m")
        self.add_input("data:geometry:wing:MAC:at25percent:x", val=np.nan, units="m")

        self.add_output("data:weight:airframe:vertical_tail:CG:x", units="m")

    def setup_partials(self):
        self.declare_partials("data:weight:airframe:vertical_tail:CG:x", "*", method="fd")

    def compute(self, inputs, outputs):
        root_chord = inputs["data:geometry:vertical_tail:root:chord"]
        tip_chord = inputs["data:geometry:vertical_tail:tip:chord"]
        lp_vt = inputs["data:geometry:vertical_tail:MAC:at25percent:x:from_wingMAC25"]
        mac_vt = inputs["data:geometry:vertical_tail:MAC:length"]
        fa_length = inputs["data:geometry:wing:MAC:at25percent:x"]
        x0_vt = inputs["data:geometry:vertical_tail:MAC:at25percent:x:local"]
        sweep_25_vt = inputs["data:geometry:vertical_tail:sweep_25"]
        b_v = inputs["data:geometry:vertical_tail:span"]

        tmp = root_chord * 0.25 + b_v * math.tan(sweep_25_vt / 180.0 * math.pi) - tip_chord * 0.25
        l_cg_vt = (1 - 0.55) * (root_chord - tip_chord) + tip_chord
        x_cg_vt = 0.42 * l_cg_vt + 0.55 * tmp
        x_cg_vt_absolute = lp_vt + fa_length - 0.25 * mac_vt + (x_cg_vt - x0_vt)

        outputs["data:weight:airframe:vertical_tail:CG:x"] = x_cg_vt_absolute
