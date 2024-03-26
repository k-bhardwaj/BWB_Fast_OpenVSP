#!/usr/bin/env python
# coding: utf-8

# # Compute_Fuselage Model (BWB)

# In[14]:


import openmdao.api as om
from fastoad.module_management.constants import ModelDomain
from fastoad.module_management.service_registry import RegisterOpenMDAOSystem, RegisterSubmodel


# In[15]:


# Import the os module
import os

# # Print the current working directory
# print("Current working directory: {0}".format(os.getcwd()))

# # Change the current working directory
# os.chdir(r'C:\Users\Justo\OneDrive - ISAE-SUPAERO\ISAE SUPAERO\Research Project\FAST-OAD\FAST-OAD-master\src\fastoad\models\geometry\Testing')

# # Print the current working directory
# print("Current working directory: {0}".format(os.getcwd()))


# In[16]:


"""
    Estimation of geometry of fuselase part A - Cabin (Commercial)
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
import fastoad.api as oad
import numpy as np
import openmdao.api as om


# In[17]:


# from constants import (
#     SERVICE_FUSELAGE_GEOMETRY_BASIC,
#     SERVICE_FUSELAGE_GEOMETRY_WITH_CABIN_SIZING,
# ) ## CHECK DIRECTORIES AND CONSTANTS NEEDED


# In[18]:
# DATA_FOLDER = "data"
# WORK_FOLDER = "workdir"
SERVICE_FUSELAGE_GEOMETRY_BASIC = "compute_fus_test" ##
SERVICE_FUSELAGE_GEOMETRY_WITH_CABIN_SIZING = "compute_fus_cabin_sizing.test"

@oad.RegisterSubmodel(
    SERVICE_FUSELAGE_GEOMETRY_BASIC, "compute_fus_1"
)
class ComputeFuselageGeometryBasic(om.ExplicitComponent):
    # TODO: Document equations. Cite sources
    """Geometry of fuselage part A - Cabin (Commercial) estimation"""

    def setup(self):
        self.add_input("data:geometry:cabin:NPAX1", val=np.nan)
        self.add_input("data:geometry:fuselage:length", val=np.nan, units="m")
        self.add_input("data:geometry:fuselage:maximum_width", val=np.nan, units="m")
        self.add_input("data:geometry:fuselage:maximum_height", val=np.nan, units="m")
        self.add_input("data:geometry:fuselage:front_length", val=np.nan, units="m")
        self.add_input("data:geometry:fuselage:rear_length", val=np.nan, units="m")
        self.add_input("data:geometry:fuselage:PAX_length", val=np.nan, units="m")
       
        self.add_output("data:weight:systems:flight_kit:CG:x", units="m")
        self.add_output("data:weight:furniture:passenger_seats:CG:x", units="m")
        self.add_output("data:geometry:cabin:length", units="m")
        self.add_output("data:geometry:fuselage:wetted_area", units="m**2")
        self.add_output("data:geometry:cabin:crew_count:commercial")

    def setup_partials(self):
        self.declare_partials(
            "data:weight:systems:flight_kit:CG:x",
            ["data:geometry:fuselage:front_length", "data:geometry:fuselage:PAX_length"],
            method="fd",
        )
        self.declare_partials(
            "data:weight:furniture:passenger_seats:CG:x",
            ["data:geometry:fuselage:front_length", "data:geometry:fuselage:PAX_length"],
            method="fd",
        )
        self.declare_partials(
            "data:geometry:cabin:length", ["data:geometry:fuselage:length"], method="fd"
        )
        self.declare_partials(
            "data:geometry:fuselage:wetted_area",
            [
                "data:geometry:fuselage:maximum_width",
                "data:geometry:fuselage:maximum_height",
                "data:geometry:fuselage:front_length",
                "data:geometry:fuselage:rear_length",
                "data:geometry:fuselage:length",
            ],
            method="fd",
        )
        self.declare_partials(
            "data:geometry:cabin:crew_count:commercial", ["data:geometry:cabin:NPAX1"], method="fd"
        )

    def compute(self, inputs, outputs):
        npax_1 = int(inputs["data:geometry:cabin:NPAX1"])
        ## Acá todo self = self y en Cabin se hacen calculos.
        lav = inputs["data:geometry:fuselage:front_length"]
        lpax = inputs["data:geometry:fuselage:PAX_length"]
        fus_length = inputs["data:geometry:fuselage:length"]
        b_f = inputs["data:geometry:fuselage:maximum_width"]
        h_f = inputs["data:geometry:fuselage:maximum_height"]
        lar = inputs["data:geometry:fuselage:rear_length"]
  

        l_cyl = fus_length - lav - lar ##lpax - (2 * self.aircraft.cabin.eco.front_seat_number - 4) * \ self.aircraft.cabin.eco.get_ls(Units.metre)
        cabin_length = 0.81 * fus_length
        x_cg_d2 = lav + 0.35 * lpax
        x_cg_c6 = lav + 0.1 * lpax
        pnc = int((npax_1 + 17) / 35)

        # Equivalent diameter of the fuselage
        fus_dia = math.sqrt(b_f * h_f)
        wet_area_nose = 2.45 * fus_dia * lav
        wet_area_cyl = 3.1416 * fus_dia * l_cyl
        wet_area_tail = 2.3 * fus_dia * lar
        wet_area_fus = wet_area_nose + wet_area_cyl + wet_area_tail

        outputs["data:weight:systems:flight_kit:CG:x"] = x_cg_c6
        outputs["data:weight:furniture:passenger_seats:CG:x"] = x_cg_d2
        outputs["data:geometry:cabin:length"] = cabin_length
        outputs["data:geometry:cabin:crew_count:commercial"] = pnc
        outputs["data:geometry:fuselage:wetted_area"] = wet_area_fus