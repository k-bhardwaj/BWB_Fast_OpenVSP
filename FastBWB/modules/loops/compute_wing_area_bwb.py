"""
Computation of wing area
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
import fastoad.api as oad
from ceras_engine import CerasEngine
from fastoad.module_management.constants import ModelDomain
from fastoad.module_management.service_registry import RegisterOpenMDAOSystem
from stdatm import AtmosphereSI

@RegisterOpenMDAOSystem("fastoad.loop.wing_area.bwb", domain=ModelDomain.OTHER)

class ComputeWingAreaBWB(om.Group):
    def setup(self):
            self.add_subsystem("wing_area_bwb", _ComputeWingAreaBWB(), promotes=["*"])
class _ComputeWingAreaBWB(om.ExplicitComponent):
    """Computation of wing area from needed approach speed and mission fuel"""
    
    def setup(self):
        self.add_input("data:TLAR:approach_speed", val=np.nan, units="m/s")
        self.add_input("data:propulsion:engine:count")
        self.add_input("data:TLAR:cruise_mach", val=np.nan)
        self.add_input("data:mission:sizing:main_route:cruise:altitude", val=np.nan, units="m")
        self.add_input("data:aerodynamics:aircraft:cruise:optimal_CL", val=np.nan)
        self.add_input("data:aerodynamics:aircraft:cruise:optimal_CD", val=np.nan)
        self.add_input("data:mission:sizing:climb:thrust_rate", val=np.nan)

        ## This must be checked
        #self.add_input("data:mission:sizing:climb:climb_thrust_setting", val = np.nan)

        self.add_output("data:geometry:wing:area", val=340, units="m**2")
        #This one yields negative values of the wetted area on the first iteration: self.add_output("data:geometry:wing:area", val=100, units="m**2")
        #This one doesnt even run: self.add_output("data:geometry:wing:area", val= np.nan, units="m**2")

    def setup_partials(self):
        self.declare_partials("data:geometry:wing:area", "*", method="fd")

    def compute(self, inputs, outputs):
        
        altitude_m = inputs["data:mission:sizing:main_route:cruise:altitude"]
        n_engines = inputs["data:propulsion:engine:count"]
        climb_thrust_setting = inputs["data:mission:sizing:climb:thrust_rate"]
        mach = inputs["data:TLAR:cruise_mach"]
        cd_opt = inputs["data:aerodynamics:aircraft:cruise:optimal_CD"]
        cl_opt = inputs["data:aerodynamics:aircraft:cruise:optimal_CL"]
        altitude_ft = 3.28084 * altitude_m
        
        atm = AtmosphereSI(altitude_m)
        sos = atm.speed_of_sound
        density = atm.density
        V = mach * sos
        ceng = CerasEngine() ## Can't call an instance method on the class itself, must create an instance, then call the method on that instance.
        thrust = ceng.compute_manual(mach, altitude_ft, climb_thrust_setting)[0] ## Manage this
        gamma = np.arctan(300./3.28/60./V)

        wing_area = 2 * n_engines * thrust / density / V**2 / (cd_opt + cl_opt * np.sin(gamma))
        
        #print("This is the new wing area in file compute_wing_area_bwb:",wing_area)
        outputs["data:geometry:wing:area"] = wing_area
        
        
class _ComputeWingAreaConstraints(om.ExplicitComponent):
    def setup(self):
        self.add_input("data:weight:aircraft:sizing_block_fuel", val=np.nan, units="kg")
        self.add_input("data:weight:aircraft:MFW", val=np.nan, units="kg")

        self.add_input("data:TLAR:approach_speed", val=np.nan, units="m/s")
        self.add_input("data:weight:aircraft:MLW", val=np.nan, units="kg")
        self.add_input("data:aerodynamics:aircraft:landing:CL_max", val=np.nan)
        self.add_input("data:geometry:wing:area", val=np.nan, units="m**2")

        self.add_output("data:weight:aircraft:additional_fuel_capacity", units="kg")
        self.add_output("data:aerodynamics:aircraft:landing:additional_CL_capacity")

    def setup_partials(self):
        self.declare_partials(
            "data:weight:aircraft:additional_fuel_capacity",
            ["data:weight:aircraft:MFW", "data:weight:aircraft:sizing_block_fuel"],
            method="fd",
        )
        self.declare_partials(
            "data:aerodynamics:aircraft:landing:additional_CL_capacity",
            [
                "data:TLAR:approach_speed",
                "data:weight:aircraft:MLW",
                "data:aerodynamics:aircraft:landing:CL_max",
                "data:geometry:wing:area",
            ],
            method="fd",
        )

    def compute(self, inputs, outputs, discrete_inputs=None, discrete_outputs=None):
        mfw = inputs["data:weight:aircraft:MFW"]
        mission_fuel = inputs["data:weight:aircraft:sizing_block_fuel"]
        v_approach = inputs["data:TLAR:approach_speed"]
        cl_max = inputs["data:aerodynamics:aircraft:landing:CL_max"]
        mlw = inputs["data:weight:aircraft:MLW"]
        wing_area = inputs["data:geometry:wing:area"]

        outputs["data:weight:aircraft:additional_fuel_capacity"] = mfw - mission_fuel
        outputs["data:aerodynamics:aircraft:landing:additional_CL_capacity"] = cl_max - mlw * g / (
            0.5 * 1.225 * (v_approach / 1.23) ** 2 * wing_area
        )
        