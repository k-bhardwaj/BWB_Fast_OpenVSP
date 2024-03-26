"""
Computation of wing position
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

# from fastoad.module_management.constants import ModelDomain
from fastoad.module_management.service_registry import RegisterOpenMDAOSystem
from fastoad.module_management.constants import ModelDomain

@RegisterOpenMDAOSystem("bwb.loop.wing_position", domain=ModelDomain.OTHER)
class ComputeWingPositionBWB(om.Group):
    def setup(self):
            self.add_subsystem("wing_pos_bwb", _ComputeWingPositionBWB(), promotes=["*"])
class _ComputeWingPositionBWB(om.ExplicitComponent):
    """
    Computes the wing position for a static margin target
    Inputs: HQ static margin, HQ margin target, Wing mean aerodynaamic chord length, 
    Wing MAC position when the aircraft is loaded in the most aft CG case, A/C CG in the most
    aft loading case.
    Outputs: Wing MAC @25% chord position from nose.
    """
    def setup(self):
        self.add_input("data:handling_qualities:static_margin", val=np.nan)
        self.add_input("data:handling_qualities:static_margin:target", val=np.nan)
        self.add_input("data:geometry:wing:MAC:length", val=np.nan, units="m")
        self.add_input("data:weight:aircraft:CG:aft:MAC_position", val=np.nan)
        self.add_input("data:weight:aircraft:CG:aft:x", val=np.nan, units="m")

        self.add_output("data:geometry:wing:MAC:at25percent:x", val=21.6, units="m") ## 21.6 Corresponds to 0.9*Fus_length (initialization value)
    def setup_partials(self):
        self.declare_partials(of="*", wrt="*", method="fd")

    def compute(self, inputs, outputs, discrete_inputs=None, discrete_outputs=None):
        static_margin = inputs["data:handling_qualities:static_margin"]
        target_static_margin = inputs["data:handling_qualities:static_margin:target"]
        l0_wing = inputs["data:geometry:wing:MAC:length"]
        cg_ratio = inputs["data:weight:aircraft:CG:aft:MAC_position"]
        cg_x = inputs["data:weight:aircraft:CG:aft:x"]

        mac_position = (
            cg_x
            + 0.25 * l0_wing
            - cg_ratio * l0_wing
            - (static_margin - target_static_margin) * l0_wing
        ) ## Check Raymer, talked about in the chapter of stability.
        
        outputs["data:geometry:wing:MAC:at25percent:x"] = mac_position