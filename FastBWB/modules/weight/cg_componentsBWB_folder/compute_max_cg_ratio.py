"""
Estimation of maximum center of gravity ratio(CG_aft)
------------------------------------------
"""

import numpy as np
import openmdao.api as om


class ComputeMaxCGratio(om.ExplicitComponent):
    # TODO: Document equations. Cite sources
    """Maximum center of gravity ratio estimation"""

    def setup(self):
        self.add_input("data:weight:aircraft:empty:CG:MAC_position", val=np.nan)
        self.add_input("data:weight:aircraft:load_cases:CG:MAC_position:maximum", val=np.nan)
        self.add_input(
            "settings:weight:aircraft:CG:aft:MAC_position:margin",
            val=0.05,
            desc="Added margin for getting most aft CG position, "
            "as ratio of mean aerodynamic chord",
        )

        self.add_output("data:weight:aircraft:CG:aft:MAC_position")

    def setup_partials(self):
        self.declare_partials("*", "*", method="fd")

    def compute(self, inputs, outputs):
        outputs["data:weight:aircraft:CG:aft:MAC_position"] = inputs[
            "settings:weight:aircraft:CG:aft:MAC_position:margin"
        ] + np.nanmax(
            [
                inputs["data:weight:aircraft:empty:CG:MAC_position"],
                inputs["data:weight:aircraft:load_cases:CG:MAC_position:maximum"],
            ]
        )
