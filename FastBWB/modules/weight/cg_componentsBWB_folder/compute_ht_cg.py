"""
Estimation of horizontal tail center of gravity (CG_A31)
------------------------------------------
This file calculates the absolute CG of the HT. (expected value = 0)

"""

import math

import numpy as np
import openmdao.api as om
from fastoad.module_management.service_registry import RegisterSubmodel

from ..constantscg import SERVICE_HORIZONTAL_TAIL_CG


@RegisterSubmodel(SERVICE_HORIZONTAL_TAIL_CG, "fastoad.submodel.weight.cg.horizontal_tail.BWBtest.1")
class ComputeHTcg(om.ExplicitComponent):
    # TODO: Document equations. Cite sources
    """Horizontal tail center of gravity estimation"""

    def setup(self):
        self.add_input("data:geometry:horizontal_tail:root:chord", val=np.nan, units="m")
        self.add_input("data:geometry:horizontal_tail:tip:chord", val=np.nan, units="m")
        self.add_input(
            "data:geometry:horizontal_tail:MAC:at25percent:x:from_wingMAC25", val=np.nan, units="m"
        )
        self.add_input("data:geometry:horizontal_tail:span", val=np.nan, units="m")
        self.add_input("data:geometry:wing:MAC:at25percent:x", val=np.nan, units="m")
        self.add_input("data:geometry:horizontal_tail:sweep_25", val=np.nan, units="deg")
        self.add_input("data:geometry:horizontal_tail:MAC:length", val=np.nan, units="m")
        self.add_input(
            "data:geometry:horizontal_tail:MAC:at25percent:x:local", val=np.nan, units="m"
        )

        self.add_output("data:weight:airframe:horizontal_tail:CG:x", units="m")

    def setup_partials(self):
        self.declare_partials("data:weight:airframe:horizontal_tail:CG:x", "*", method="fd")

    def compute(self, inputs, outputs):
        root_chord = inputs["data:geometry:horizontal_tail:root:chord"]
        tip_chord = inputs["data:geometry:horizontal_tail:tip:chord"]
        b_h = inputs["data:geometry:horizontal_tail:span"]
        sweep_25_ht = inputs["data:geometry:horizontal_tail:sweep_25"]
        fa_length = inputs["data:geometry:wing:MAC:at25percent:x"]
        lp_ht = inputs["data:geometry:horizontal_tail:MAC:at25percent:x:from_wingMAC25"]
        mac_ht = inputs["data:geometry:horizontal_tail:MAC:length"]
        x0_ht = inputs["data:geometry:horizontal_tail:MAC:at25percent:x:local"]

        tmp = (
            root_chord * 0.25 + b_h / 2 * math.tan(sweep_25_ht / 180.0 * math.pi) - tip_chord * 0.25
        )

        l_cg = 0.62 * (root_chord - tip_chord) + tip_chord
        x_cg_ht = 0.42 * l_cg + 0.38 * tmp
        x_cg_ht_absolute = lp_ht + fa_length - 0.25 * mac_ht + (x_cg_ht - x0_ht)

        outputs["data:weight:airframe:horizontal_tail:CG:x"] = x_cg_ht_absolute
