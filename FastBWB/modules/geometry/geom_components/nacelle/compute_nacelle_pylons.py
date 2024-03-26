"""
    Estimation of nacelle and pylon geometry
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

from math import sqrt
import fastoad.api as oad
import numpy as np
import openmdao.api as om


@oad.RegisterSubmodel(
    "bwb.nacelle", "fastoad.nacelle.bwb"
)
class ComputeNacelleAndPylonsGeometry(om.ExplicitComponent):
    # TODO: Document equations. Cite sources
    """Nacelle and pylon geometry estimation"""

    def setup(self):

        self.add_input("data:propulsion:MTO_thrust", val = np.nan, units="N") # Sea-level thrust.
        self.add_input("data:geometry:propulsion:engine:y_ratio", val=np.nan)
        self.add_input("data:geometry:wing:span", val=np.nan, units="m")
        self.add_input("data:geometry:fuselage:length", val=np.nan, units="m")

        self.add_output("data:geometry:propulsion:pylon:length", units="m")
        self.add_output("data:geometry:propulsion:fan:length", units="m")
        self.add_output("data:geometry:propulsion:nacelle:length", units="m")
        self.add_output("data:geometry:propulsion:nacelle:diameter", units="m")
        self.add_output("data:geometry:landing_gear:height", units="m")
        self.add_output("data:geometry:propulsion:nacelle:y", units="m")
        self.add_output("data:geometry:propulsion:pylon:wetted_area", units="m**2")
        self.add_output("data:geometry:propulsion:nacelle:wetted_area", units="m**2")
        self.add_output("data:weight:propulsion:engine:CG:x", units="m")

    def setup_partials(self):
        self.declare_partials(
            "data:geometry:propulsion:nacelle:diameter", "data:propulsion:MTO_thrust", method="fd"
        )
        self.declare_partials(
            "data:geometry:propulsion:nacelle:length", "data:propulsion:MTO_thrust", method="fd"
        )
        self.declare_partials(
            "data:geometry:landing_gear:height", "data:propulsion:MTO_thrust", method="fd"
        )
        self.declare_partials(
            "data:geometry:propulsion:fan:length", "data:propulsion:MTO_thrust", method="fd"
        )
        self.declare_partials(
            "data:geometry:propulsion:pylon:length", "data:propulsion:MTO_thrust", method="fd"
        )
        self.declare_partials(
            "data:geometry:propulsion:nacelle:y",
            [
                "data:propulsion:MTO_thrust",
                "data:geometry:propulsion:engine:y_ratio",
                "data:geometry:wing:span",
            ],
            method="fd",
        )
        self.declare_partials(
            "data:weight:propulsion:engine:CG:x",
            [
                "data:geometry:fuselage:length",
                "data:propulsion:MTO_thrust",
                "data:geometry:propulsion:engine:y_ratio",
                "data:geometry:wing:span",
            ],
            method="fd",
        )
        self.declare_partials(
            "data:geometry:propulsion:nacelle:wetted_area",
            "data:propulsion:MTO_thrust",
            method="fd",
        )
        self.declare_partials(
            "data:geometry:propulsion:pylon:wetted_area", "data:propulsion:MTO_thrust", method="fd"
        )

    def compute(self, inputs, outputs):
        thrust_sl = inputs["data:propulsion:MTO_thrust"]
        y_ratio_engine = inputs["data:geometry:propulsion:engine:y_ratio"]
        span = inputs["data:geometry:wing:span"]
        fus_length = inputs["data:geometry:fuselage:length"]


        nac_dia = 0.00904 * sqrt(thrust_sl * 0.225) + 0.7 # Nacelle diameter
        lg_height = 1.4 * nac_dia # Landing gear height.
        # The nominal thrust must be used in lbf
        nac_length = 0.032 * sqrt(thrust_sl * 0.225)  # FIXME: use output of engine module

        outputs["data:geometry:propulsion:nacelle:length"] = nac_length
        outputs["data:geometry:propulsion:nacelle:diameter"] = nac_dia
        outputs["data:geometry:landing_gear:height"] = lg_height

        fan_length = 0.60 * nac_length 
        pylon_length = 1.1 * nac_length

        y_nacell = y_ratio_engine * span / 2
        x_nacell_cg_absolute = 0.8*fus_length

        outputs["data:geometry:propulsion:pylon:length"] = pylon_length
        outputs["data:geometry:propulsion:fan:length"] = fan_length
        outputs["data:geometry:propulsion:nacelle:y"] = y_nacell
        outputs["data:weight:propulsion:engine:CG:x"] = x_nacell_cg_absolute

        # Wet surfaces
        wet_area_nac = 0.0004 * thrust_sl * 0.225 + 11  # Per engine
        wet_area_pylon = 0.35 * wet_area_nac

        outputs["data:geometry:propulsion:nacelle:wetted_area"] = wet_area_nac
        outputs["data:geometry:propulsion:pylon:wetted_area"] = wet_area_pylon