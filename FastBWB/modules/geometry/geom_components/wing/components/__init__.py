"""
Estimation of vertical tail geometry (components)
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

# flake8: noqa

from .bwb_b50 import ComputeB50
from .bwb_cl_alpha import ComputeCLalpha
from .bwb_MAC_wing import ComputeMACWingBWB
from .bwb_MFW import ComputeMFWBWB
from .bwb_compute_l2_l3 import ComputeL2AndL3Wing
from .bwb_compute_sweep_wing import ComputeSweepWingBWB
from .bwb_compute_toc_wing import ComputeToCWingBWB
from .bwb_compute_wet_area_wing import ComputeWetAreaWingBWB
from .bwb_compute_x_wing import ComputeXWingBWB
from .bwb_compute_y_wing import ComputeYWingBWB
from .bwb_l1_l4 import ComputeL1AndL4WingBWB
