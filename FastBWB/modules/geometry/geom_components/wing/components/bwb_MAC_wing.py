"""
    Estimation of wing mean aerodynamic chord
"""

#  This file is part of FAST-OAD_CS25
#  Copyright (C) 2022 ONERA & ISAE-SUPAERO
#  FAST is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <https://www.gnu.org/licenses/>.
import numpy as np
import openmdao.api as om
import math


# TODO: it would be good to have a function to compute MAC for HT, VT and WING
class ComputeMACWingBWB(om.ExplicitComponent):
    # TODO: Document equations. Cite sources
    """Wing mean aerodynamic chord estimation"""

    def setup(self):
        self.add_input("data:geometry:wing:kink:leading_edge:x:local", val=np.nan, units="m")#X3
        self.add_input("data:geometry:wing:root:y", val=np.nan, units="m") #Y2
        self.add_input("data:geometry:wing:tip:chord", val=np.nan, units="m") #L4
        self.add_input("data:geometry:wing:root:virtual_chord", val=np.nan, units="m") #L1
        self.add_input("data:geometry:wing:span", val=np.nan, units="m")
        self.add_input("data:geometry:wing:eps1", val=np.nan)
        self.add_input("data:geometry:wing:tip:y",val=np.nan, units = "m") #Y4

        self.add_output("data:geometry:wing:MAC:length", units="m")
        self.add_output("data:geometry:wing:MAC:leading_edge:x:local", units="m")
        self.add_output("data:geometry:wing:MAC:y", units="m")

    def setup_partials(self):
        self.declare_partials(
            "data:geometry:wing:MAC:length",
            [
                "data:geometry:wing:kink:leading_edge:x:local",
                "data:geometry:wing:root:y",
                "data:geometry:wing:tip:chord",
                "data:geometry:wing:root:virtual_chord",
                "data:geometry:wing:span",
                "data:geometry:wing:eps1",
            ],
            method="fd",
        )
        self.declare_partials(
            "data:geometry:wing:MAC:leading_edge:x:local",
            [
                "data:geometry:wing:kink:leading_edge:x:local",
                "data:geometry:wing:root:y",
                "data:geometry:wing:tip:chord",
                "data:geometry:wing:root:virtual_chord",
                "data:geometry:wing:span",
                "data:geometry:wing:eps1",
            ],
            method="fd",
        )
        self.declare_partials(
            "data:geometry:wing:MAC:y",
            [
                "data:geometry:wing:kink:leading_edge:x:local",
                "data:geometry:wing:root:y",
                "data:geometry:wing:tip:chord",
                "data:geometry:wing:root:virtual_chord",
                "data:geometry:wing:span",
                "data:geometry:wing:eps1",
            ],
            method="fd",
        )

    def compute(self, inputs, outputs):
        x3_wing = inputs["data:geometry:wing:kink:leading_edge:x:local"]
        y2_wing = inputs["data:geometry:wing:root:y"]
        y4_wing = inputs["data:geometry:wing:tip:y"]
        l4_wing = inputs["data:geometry:wing:tip:chord"]
        l1_wing = inputs["data:geometry:wing:root:virtual_chord"]
        span = inputs["data:geometry:wing:span"]
        eps1 = inputs["data:geometry:wing:eps1"]

        l0_wing=2./3* l1_wing*((1.+eps1+eps1**2)/(1+eps1))
        y0_wing= span/2 /6 * (1.+2*eps1)*(1+eps1)
        sweep_0= math.atan((l1_wing-l4_wing)/(y4_wing-y2_wing)) * 180. / math.pi
        x0_wing=x3_wing+math.tan(sweep_0/ 180 * math.pi)*(y0_wing- y2_wing) 
         

        outputs["data:geometry:wing:MAC:length"] = l0_wing
        outputs["data:geometry:wing:MAC:leading_edge:x:local"] = x0_wing
        outputs["data:geometry:wing:MAC:y"] = y0_wing