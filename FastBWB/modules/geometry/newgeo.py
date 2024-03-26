"""
    FAST - Copyright (c) 2016 ONERA ISAE
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

import openmdao.api as om
from fastoad.module_management.constants import ModelDomain
from fastoad.module_management.service_registry import RegisterOpenMDAOSystem, RegisterSubmodel

# Import the os module
import os

# # Print the current working directory
# print("Current working directory: {0}".format(os.getcwd()))

# # Change the current working directory
# os.chdir(r'C:\Users\Justo\FAST-OAD_notebooks\04_Testing')
# # os.chdir(r'C:\Users\Justo\OneDrive - ISAE-SUPAERO\ISAE SUPAERO\Research Project\FAST-OAD\FAST-OAD-master\src\fastoad\models\geometry\Testing')

from .constants import (
    SERVICE_FUSELAGE_GEOMETRY_BASIC,
    SERVICE_FUSELAGE_GEOMETRY_WITH_CABIN_SIZING,
    SERVICE_HORIZONTAL_TAIL_GEOMETRY,
    SERVICE_NACELLE_PYLON_GEOMETRY,
    SERVICE_VERTICAL_TAIL_GEOMETRY,
    SERVICE_WING_GEOMETRY,
    SERVICE_AIRCRAFT_WETTED_AREA,
    SERVICE_AIRCRAFT_AERODYNAMIC_CENTER,
)


@RegisterOpenMDAOSystem("fastoad.geometry.test.2")
class Newgeo(om.Group):
    """
    Computes geometric characteristics of the BWB aircraft:
      - fuselage size can be computed from payload requirements
      - wing dimensions are computed from global parameters (area, taper ratio...)
      - tail planes are dimensioned from HQ requirements
    """

    def initialize(self): ## Basically acts like a switch. If the Cabin sizing option is called, it jumps to line 78, as explained below.
        self.options.declare(
            "CABIN_SIZING_OPTION",
            types=bool,
            default=True,
            desc="If True, fuselage dimensions will be computed from cabin specifications."
            "\nIf False, fuselage dimensions will be input data.",
        )

    def setup(self):

        if self.options["CABIN_SIZING_OPTION"]:  ### Adds the fuselage module/subsystem. Computes the cabin sizing for a BWB.
            self.add_subsystem(
                "compute_fus_2",
                RegisterSubmodel.get_submodel("compute_fus_cabin_sizing.test"),
                promotes=["*"],
            )
        else:
            self.add_subsystem(
                "compute_fuselage_test",
                RegisterSubmodel.get_submodel("compute_fus_test"),
                promotes=["*"],
            )
            
        self.add_subsystem(  # Adds the wing module/subsystem
            "compute_wing", 
            RegisterSubmodel.get_submodel("compute_wing_bwb"), 
            promotes=["*"]
        )
        
        self.add_subsystem(
            "compute_nacelle_bwb",
            RegisterSubmodel.get_submodel("bwb.nacelle"),
            promotes=["*"],
            )

        self.add_subsystem(
            "compute_vt_test",
            RegisterSubmodel.get_submodel("compute_VT_test"),
            promotes=["*"],
            )
        
        self.add_subsystem(
            "compute_total_area",
            RegisterSubmodel.get_submodel("compute_total_area_bwb"),
            promotes=["*"],
            )
        
        self.add_subsystem(
            "aero_center_bwb",
            RegisterSubmodel.get_submodel("aerocenter.bwb"),
            promotes=["*"],
            )
            
        self.add_subsystem(
            "fuselage_cnbeta_bwb",
            RegisterSubmodel.get_submodel("fuselage.cnbeta.bwb"),
            promotes=["*"],
            )
        
        

