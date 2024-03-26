"""
    Estimation of wing chords (l2 and l3)
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
import math

import numpy as np
import openmdao.api as om


class ComputeL2AndL3Wing(om.ExplicitComponent):
    """Wing chords (l2 and l3) estimation
    Inputs: Leading edge wing sweep, wing root virtual chord, wingtip chord, wing kink spanwise position,
    wing root spanwise position.
    Outputs: Wing root chord, wing kink chord, wing taper ratio."""

    def setup(self):
        self.add_input("data:geometry:wing:sweep_0", val=np.nan, units="deg")
        self.add_input("data:geometry:wing:root:virtual_chord", val=np.nan, units="m")
        self.add_input("data:geometry:wing:tip:chord", val=np.nan, units="m")
        self.add_input("data:geometry:wing:kink:y", val=np.nan, units="m")
        self.add_input("data:geometry:wing:root:y", val=np.nan, units="m")

        self.add_output("data:geometry:wing:root:chord", units="m")
        self.add_output("data:geometry:wing:kink:chord", units="m")
        self.add_output("data:geometry:wing:taper_ratio")

    def setup_partials(self):
        self.declare_partials(
            "data:geometry:wing:root:chord",
            [
                "data:geometry:wing:root:virtual_chord"
            ],
            method="fd",
         )
        self.declare_partials(
            "data:geometry:wing:kink:chord",
            [
                "data:geometry:wing:root:virtual_chord",
                "data:geometry:wing:kink:y",
                "data:geometry:wing:root:y",    
                "data:geometry:wing:sweep_0",
            ],
            method="fd",
        )

    def compute(self, inputs, outputs):
        l1_wing = inputs["data:geometry:wing:root:virtual_chord"]
        l4_wing = inputs["data:geometry:wing:tip:chord"]
        sweep_0 = inputs["data:geometry:wing:sweep_0"]
        y3_wing = inputs["data:geometry:wing:kink:y"]
        y2_wing = inputs["data:geometry:wing:root:y"]
      

        l2_wing = l1_wing # Equations from Preliminary Desing Manual, ADM course.
        l3_wing = l1_wing - math.tan(sweep_0 / 180. * math.pi)*(y3_wing - y2_wing)

        outputs["data:geometry:wing:root:chord"] = l2_wing
        outputs["data:geometry:wing:kink:chord"] = l3_wing
        outputs["data:geometry:wing:taper_ratio"] = l4_wing / l2_wing
