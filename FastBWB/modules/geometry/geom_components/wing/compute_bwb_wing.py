"""
    Estimation of wing geometry
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
import openmdao.api as om
import os


from .components import (
    ComputeB50,
    ComputeCLalpha,
    ComputeL1AndL4WingBWB,
    ComputeMACWingBWB,
    ComputeMFWBWB,
    ComputeSweepWingBWB,
    ComputeToCWingBWB,
    ComputeWetAreaWingBWB,
    ComputeXWingBWB,
    ComputeYWingBWB,
    ComputeL2AndL3Wing
)

@oad.RegisterSubmodel("compute_wing_bwb","compute_wing")
class ComputeWingGeometry(om.Group):
    # TODO: Document equations. Cite sources
    """Wing geometry estimation"""

    ### The Compute_wing_bwb module calls all the following components, in the top to bottom order
    #shown below.
    def setup(self):
        self.add_subsystem("y_wing", ComputeYWingBWB(), promotes=["*"])
        self.add_subsystem("l14_wing", ComputeL1AndL4WingBWB(), promotes=["*"])
        self.add_subsystem("l2l3_wing", ComputeL2AndL3Wing(), promotes=["*"])
        self.add_subsystem("x_wing", ComputeXWingBWB(), promotes=["*"])
        self.add_subsystem("mac_wing", ComputeMACWingBWB(), promotes=["*"])
        self.add_subsystem("b50_wing", ComputeB50(), promotes=["*"])
        self.add_subsystem("sweep_wing", ComputeSweepWingBWB(), promotes=["*"])
        self.add_subsystem("toc_wing", ComputeToCWingBWB(), promotes=["*"])
        self.add_subsystem("wetarea_wing", ComputeWetAreaWingBWB(), promotes=["*"])
        #self.add_subsystem("clapha_wing", ComputeCLalpha(), promotes=["*"])
        self.add_subsystem("mfw", ComputeMFWBWB(), promotes=["*"])