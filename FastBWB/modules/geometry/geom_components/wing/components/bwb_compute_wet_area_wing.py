"""
    Estimation of wing wet area
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


class ComputeWetAreaWingBWB(om.ExplicitComponent):
    """Wing wet area estimation
    Inputs: Wing root chord, Wing root spanwise position, wing area, and fuselage
    max width.
    Outputs: Total wet area of centerbody + wing, wing wetted area."""

    def setup(self):
        self.add_input("data:geometry:wing:root:chord", val=np.nan, units="m")
        self.add_input("data:geometry:wing:root:y", val=np.nan, units="m")
        self.add_input("data:geometry:wing:area", val=np.nan, units="m**2")
        self.add_input("data:geometry:fuselage:maximum_width", val=np.nan, units="m")
        self.add_output("data:geometry:wing:s_pf", units="m**2") # Total wet area of centerbody + wing
        self.add_output("data:geometry:wing:wetted_area", units="m**2") # Only wing wet area.

    def setup_partials(self):
        self.declare_partials(
            "data:geometry:wing:s_pf",
            [
                "data:geometry:wing:area",
                "data:geometry:wing:root:y",
                "data:geometry:wing:root:chord",
            ],
            method="fd",
        )
        self.declare_partials(
            "data:geometry:wing:wetted_area",
            [
                "data:geometry:wing:area",
                "data:geometry:wing:root:chord",
                "data:geometry:fuselage:maximum_width",
            ],
            method="fd",
        )

    def compute(self, inputs, outputs):
        wing_area = inputs["data:geometry:wing:area"]
        l2_wing = inputs["data:geometry:wing:root:chord"]
        y2_wing = inputs["data:geometry:wing:root:y"]
        width_max = inputs["data:geometry:fuselage:maximum_width"]
        s_pf = wing_area - 2 * l2_wing * y2_wing # Equations from Preliminary Design Manual
        wet_area_wing = 2 * (wing_area - width_max * l2_wing) 
        
        
        #print("Loaded wing area on bwb_compute_wet_area_wing.py:" , wing_area)
        #print("Loaded l2_wing on bwb_compute_wet_area_wing.py:" , l2_wing)
        #print("Loaded y2_wing on bwb_compute_wet_area_wing.py:" , y2_wing)
        #print("Loaded fuselage maximum width on bwb_compute_wet_area_wing.py:" , width_max)
        #print("Loaded centerbody area on bwb_compute_wet_area_wing.py:" , area_cb)
        
        #print("Resulting s_pf on bwb_compute_wet_area_wing.py " , s_pf)
        #print("Resulting wing's wetted area on bwb_compute_wet_area_wing.py " , wet_area_wing)
        #print("")
        #print("")
        outputs["data:geometry:wing:s_pf"] = s_pf
        outputs["data:geometry:wing:wetted_area"] = wet_area_wing
