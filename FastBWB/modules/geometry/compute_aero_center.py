"""
    Estimation of aerodynamic center
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

import fastoad.api as oad
import numpy as np
import openmdao.api as om

@oad.RegisterSubmodel(
    "aerocenter.bwb",
    "fastoad.submodel.geometry.aircraft.aerodynamic_center.bwb",
)
class ComputeAeroCenter(om.ExplicitComponent):
    # TODO: Document equations. Cite sources
    """Aerodynamic center estimation"""

    def setup(self):
        self.add_input("data:geometry:wing:MAC:leading_edge:x:local", val=np.nan, units="m")
        self.add_input("data:geometry:wing:MAC:length", val=np.nan, units="m")
        self.add_input("data:geometry:wing:root:virtual_chord", val=np.nan, units="m")
        self.add_input("data:geometry:fuselage:maximum_width", val=np.nan, units="m")
        self.add_input("data:geometry:fuselage:length", val=np.nan, units="m")
        self.add_input("data:geometry:wing:MAC:at25percent:x", val=np.nan, units="m")
        self.add_input("data:geometry:wing:area", val=np.nan, units="m**2")
        self.add_input("data:geometry:horizontal_tail:area", val=np.nan, units="m**2")
        self.add_input("data:geometry:horizontal_tail:MAC:at25percent:x:from_wingMAC25", val=np.nan, units="m")
        self.add_input("data:aerodynamics:aircraft:cruise:CL_alpha", val=np.nan)
        self.add_input("data:aerodynamics:horizontal_tail:cruise:CL_alpha", val=np.nan)

        self.add_output("data:aerodynamics:cruise:neutral_point:x")

    def setup_partials(self):
        self.declare_partials("*", "*", method="fd")

    def compute(self, inputs, outputs):
        x0_wing = inputs["data:geometry:wing:MAC:leading_edge:x:local"]
        l0_wing = inputs["data:geometry:wing:MAC:length"]
        l1_wing = inputs["data:geometry:wing:root:virtual_chord"]
        width_max = inputs["data:geometry:fuselage:maximum_width"]
        fa_length = inputs["data:geometry:wing:MAC:at25percent:x"]
        fus_length = inputs["data:geometry:fuselage:length"]
        wing_area = inputs["data:geometry:wing:area"]
        s_h = inputs["data:geometry:horizontal_tail:area"]
        lp_ht = inputs["data:geometry:horizontal_tail:MAC:at25percent:x:from_wingMAC25"] # "Aero-center" position of Horizontal taill
        cl_alpha_wing = inputs["data:aerodynamics:aircraft:cruise:CL_alpha"]
        cl_alpha_ht = inputs["data:aerodynamics:horizontal_tail:cruise:CL_alpha"]
        
        x0_25 = fa_length - 0.25 * l0_wing - x0_wing + 0.25 * l1_wing
        ratio_x025 = x0_25 / fus_length
        # Fitting result of Daniel P. Raymer's Aircraft Design a Conceptual Approach, figure 16.14
        k_h = 0.01222 - 7.40541E-4 * ratio_x025 + 2.1956E-5 * ratio_x025**2
        # Equation from Raymer book, eqn 16.22
        cm_alpha_fus = k_h * width_max**2 * \
            fus_length / (l0_wing * wing_area) * 57.3
        x_ca_plane = (cl_alpha_wing * (fa_length - cm_alpha_fus / cl_alpha_wing) +
                      cl_alpha_ht * (1 - 0.4) * 0.9 *
                      s_h / wing_area * (lp_ht + fa_length)) / \
            (cl_alpha_wing +
             cl_alpha_ht * (1 - 0.4) * 0.9 * s_h / wing_area)

        x_aero_center = x_ca_plane - fa_length / l0_wing + 0.25
        
        x_aero_center = x_aero_center / fus_length

        outputs["data:aerodynamics:cruise:neutral_point:x"] = x_aero_center