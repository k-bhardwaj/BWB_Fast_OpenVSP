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

# Print the current working directory
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

SERVICE_FUSELAGE_GEOMETRY_BASIC = "compute_fus"
SERVICE_FUSELAGE_GEOMETRY_WITH_CABIN_SIZING = "compute_fus_cabin_sizing.test" #The id of the submodel


@oad.RegisterSubmodel(
    SERVICE_FUSELAGE_GEOMETRY_WITH_CABIN_SIZING, "compute_fus_2"
)
class ComputeFuselageGeometryCabinSizing(om.ExplicitComponent):
    # TODO: Document equations. Cite sources
    """Geometry of fuselage part A - Cabin (Commercial) estimation"""

    def setup(self):

        self.add_input("data:geometry:cabin:seats:economical:width", val=np.nan, units="m")
        self.add_input("data:geometry:cabin:seats:economical:length", val=np.nan, units="m")
        self.add_input("data:geometry:cabin:seats:economical:count_by_row", val=np.nan)
        self.add_input("data:geometry:cabin:aisle_width", val=np.nan, units="m")
        self.add_input("data:geometry:cabin:aisle_number", val=np.nan)
        self.add_input("data:geometry:cabin:exit_width", val=np.nan, units="m")
        self.add_input("data:TLAR:NPAX", val=np.nan)
        # self.add_input("data:geometry:propulsion:engine:count", val=np.nan)
        self.add_input("data:geometry:fuselage:sweep_25_centerbody", val=np.nan, units="deg")
        self.add_input("data:geometry:fuselage:toc_centerbody", val=np.nan)

        self.add_output("data:geometry:cabin:NPAX1")
        self.add_output("data:weight:systems:flight_kit:CG:x", units="m")
        self.add_output("data:weight:furniture:passenger_seats:CG:x", units="m")
        self.add_output("data:geometry:fuselage:length", units="m")
        self.add_output("data:geometry:fuselage:maximum_width", units="m")
        self.add_output("data:geometry:fuselage:maximum_height", units="m")
        self.add_output("data:geometry:fuselage:front_length", units="m")
        self.add_output("data:geometry:fuselage:rear_length", units="m")
        self.add_output("data:geometry:fuselage:PAX_length", units="m")
        self.add_output("data:geometry:cabin:length", units="m")
        self.add_output("data:geometry:fuselage:wetted_area", units="m**2")
        self.add_output("data:geometry:fuselage:area_centerbody", units="m**2")
        self.add_output("data:geometry:cabin:crew_count:commercial")

    def setup_partials(self):
        self.declare_partials("data:geometry:cabin:NPAX1", ["data:TLAR:NPAX"], method="fd")
        self.declare_partials(
            "data:geometry:fuselage:maximum_width",
            [
                "data:geometry:cabin:seats:economical:count_by_row",
                "data:geometry:cabin:seats:economical:width",
                "data:geometry:cabin:aisle_width",
                "data:geometry:cabin:aisle_number",
            ],
            method="fd",
        )
        self.declare_partials(
            "data:geometry:fuselage:maximum_height",
            [
                "data:geometry:cabin:seats:economical:count_by_row",
                "data:geometry:cabin:seats:economical:width",
                "data:geometry:cabin:aisle_width",
            ],
            method="fd",
        )
        self.declare_partials(
            "data:geometry:fuselage:front_length",
            [
                "data:geometry:cabin:seats:economical:count_by_row",
                "data:geometry:cabin:seats:economical:width",
                "data:geometry:cabin:aisle_width",
            ],
            method="fd",
        )
        self.declare_partials(
            "data:geometry:fuselage:rear_length",
            [
                "data:geometry:cabin:seats:economical:count_by_row",
                "data:geometry:cabin:seats:economical:width",
                "data:geometry:cabin:aisle_width",
            ],
            method="fd",
        )
        self.declare_partials(
            "data:geometry:fuselage:PAX_length",
            ["data:geometry:cabin:seats:economical:length", "data:geometry:cabin:exit_width"],
            method="fd",
        )
        self.declare_partials(
            "data:geometry:fuselage:length",
            [
                "data:geometry:cabin:seats:economical:count_by_row",
                "data:geometry:cabin:aisle_width",
                "data:geometry:cabin:seats:economical:length",
                "data:geometry:cabin:seats:economical:width",
                "data:geometry:cabin:exit_width",
            ],
            method="fd",
        )
        self.declare_partials(
            "data:geometry:cabin:length",
            [
                "data:geometry:cabin:seats:economical:count_by_row",
                "data:geometry:cabin:aisle_width",
                "data:geometry:cabin:seats:economical:length",
                "data:geometry:cabin:seats:economical:width",
                "data:geometry:cabin:exit_width",
            ],
            method="fd",
        )
        self.declare_partials(
            "data:weight:systems:flight_kit:CG:x",
            [
                "data:geometry:cabin:seats:economical:count_by_row",
                "data:geometry:cabin:seats:economical:width",
                "data:geometry:cabin:seats:economical:length",
                "data:geometry:cabin:exit_width",
                "data:geometry:cabin:aisle_width",
            ],
            method="fd",
        )
        self.declare_partials(
            "data:weight:furniture:passenger_seats:CG:x",
            [
                "data:geometry:cabin:seats:economical:count_by_row",
                "data:geometry:cabin:seats:economical:width",
                "data:geometry:cabin:seats:economical:length",
                "data:geometry:cabin:exit_width",
                "data:geometry:cabin:aisle_width",
            ],
            method="fd",
        )
        self.declare_partials(
            "data:geometry:fuselage:wetted_area",
            [
                "data:geometry:cabin:seats:economical:count_by_row",
                "data:geometry:cabin:aisle_width",
                "data:geometry:cabin:seats:economical:length",
                "data:geometry:cabin:seats:economical:width",
                "data:geometry:cabin:exit_width",
            ],
            method="fd",
        )

    def compute(self, inputs, outputs):
        front_seat_number_eco = inputs["data:geometry:cabin:seats:economical:count_by_row"] # Number of seats per row
        ws_eco = inputs["data:geometry:cabin:seats:economical:width"] # Width of economy class seats
        ls_eco = inputs["data:geometry:cabin:seats:economical:length"] # Length of economy class seats
        w_aisle = inputs["data:geometry:cabin:aisle_width"] # Width of aisle
        n_aisle = inputs["data:geometry:cabin:aisle_number"] # Number of aisles in the cabin
        w_exit = inputs["data:geometry:cabin:exit_width"] # Exit width
        npax = inputs["data:TLAR:NPAX"] # Number of passengers
    
        sweep_25 = inputs["data:geometry:fuselage:sweep_25_centerbody"]
        toc = inputs["data:geometry:fuselage:toc_centerbody"]

        # Cabin width = N * seat width + Aisle width + (N+2)*2"+2 * 1"
        wcabin = (
            front_seat_number_eco * ws_eco + w_aisle*n_aisle + (front_seat_number_eco + 2) * 0.051 + 0.05 +0.14   #### Added a 0.14
        ) 
        
        width_max = wcabin # Max width

        # Number of rows = Npax / N
        npax_1 = npax # Number of passengers auxiliary variable
        n_rows = int(npax_1 / front_seat_number_eco)+1 ##Added a +1
        pnc = int((npax + 17) / 35)
        # Length of pax cabin = Length of seat area + Width of 1 Emergency exit
        lpax = (n_rows * ls_eco) + 1 * w_exit #Same as for conventional aircraft
        l_cyl = lpax - (2 * front_seat_number_eco - 4) * ls_eco 
        lav = wcabin / 2. * math.tan(sweep_25* math.pi / 180.) # Length of the fuselage section in front of the cabin
        fus_length = (lav+lpax)/0.7  # Total fuselage length
        cabin_length = 0.81 * fus_length # Cabin length
        lar = 0.3 * fus_length # Length of the fuselage section behind the cabin
        area_cb = 0.5 * lav * wcabin + wcabin * lpax + 0.5 * lar * wcabin # Centerbody area
        height_max = fus_length * toc # Maximum height 
        x_cg_passenger = lav - front_seat_number_eco * ls_eco + lpax / 2
        
        b_f = width_max
        h_f = height_max

        cabin_length = lpax
        x_cg_c6 = lav - (front_seat_number_eco - 4) * ls_eco + lpax * 0.1 # Same as conventional aircraft
        x_cg_d2 = lav - (front_seat_number_eco - 4) * ls_eco + lpax / 2 # Same as conventional aircraft
        
        wet_area_fus = 2.2 * area_cb # Fuselage wet area

        outputs["data:geometry:cabin:NPAX1"] = npax_1
        outputs["data:weight:systems:flight_kit:CG:x"] = x_cg_c6
        outputs["data:weight:furniture:passenger_seats:CG:x"] = x_cg_d2
        outputs["data:geometry:fuselage:length"] = fus_length
        outputs["data:geometry:fuselage:maximum_width"] = b_f
        outputs["data:geometry:fuselage:maximum_height"] = h_f
        outputs["data:geometry:fuselage:front_length"] = lav
        outputs["data:geometry:fuselage:rear_length"] = lar
        outputs["data:geometry:fuselage:PAX_length"] = lpax
        outputs["data:geometry:fuselage:area_centerbody"] = area_cb
        outputs["data:geometry:cabin:length"] = cabin_length
        outputs["data:geometry:cabin:crew_count:commercial"] = pnc
        outputs["data:geometry:fuselage:wetted_area"] = wet_area_fus



