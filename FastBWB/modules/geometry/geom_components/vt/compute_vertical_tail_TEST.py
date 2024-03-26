"""
    Estimation of geometry of vertical tail
"""
#  This file is part of FAST-OAD : A framework for rapid Overall Aircraft Design
#  Copyright (C) 2021 ONERA & ISAE-SUPAERO
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

from .components import (
    ComputeVTChords,
    ComputeVTClalpha,
    ComputeVTArea,
    ComputeVTMAC,
    ComputeVTSweep,
)
"""
from compute_vt_chords_TEST import ComputeVTChords
from compute_vt_clalpha_TEST import ComputeVTClalpha
from compute_vt_distance_TEST import ComputeVTDistance
from compute_vt_mac_TEST import ComputeVTMAC
from compute_vt_sweep_TEST import ComputeVTSweep
"""


# Print the current working directory
# print("Current working directory: {0}".format(os.getcwd()))

SERVICE_VERTICAL_TAIL_GEOMETRY = "compute_VT_test"
    
@oad.RegisterSubmodel(
    SERVICE_VERTICAL_TAIL_GEOMETRY, "compute_VT.5"
)
class ComputeVerticalTailGeometry(om.Group):
    """Vertical tail geometry estimation"""
    
    def setup(self):
        self.add_subsystem("vt_area", ComputeVTArea(), promotes=["*"])
        self.add_subsystem("vt_clalpha", ComputeVTClalpha(), promotes=["*"])
        self.add_subsystem("vt_chords", ComputeVTChords(), promotes=["*"])
        self.add_subsystem("vt_mac", ComputeVTMAC(), promotes=["*"])
        self.add_subsystem("vt_sweep", ComputeVTSweep(), promotes=["*"])

