"""
    Estimation of wing chords (l1 and l4)
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


class ComputeL1AndL4WingBWB(om.ExplicitComponent):
    """Wing chords (l1 and l4) estimation
    Inputs: Wing area, wingspan, fuselage max width, 
    Outputs: Wing root virtual chord length, wingtip chord length"""

    def setup(self):
        self.add_input("data:geometry:wing:area", val=np.nan, units="m**2")
        self.add_input("data:geometry:wing:span", val=np.nan, units="m")
        self.add_input("data:geometry:fuselage:maximum_width", val=np.nan, units="m")
        self.add_input("data:geometry:wing:eps1", val=np.nan)

        self.add_output("data:geometry:wing:root:virtual_chord", units="m")
        self.add_output("data:geometry:wing:tip:chord", units="m")

    def setup_partials(self):
        self.declare_partials("data:geometry:wing:root:virtual_chord", "*", method="fd")
        self.declare_partials("data:geometry:wing:tip:chord", "*", method="fd")

    def compute(self, inputs, outputs):
        wing_area = inputs["data:geometry:wing:area"] 
        span = inputs["data:geometry:wing:span"]
        width_max = inputs["data:geometry:fuselage:maximum_width"]
        eps1 = inputs["data:geometry:wing:eps1"]

        l1_wing = wing_area/((span-width_max)*(1.+eps1)/2.) # Adapted from Preliminary Design manual.
        
        l4_wing=eps1*l1_wing # p.40 Preliminary Design Manual.

        outputs["data:geometry:wing:root:virtual_chord"] = l1_wing
        outputs["data:geometry:wing:tip:chord"] = l4_wing
