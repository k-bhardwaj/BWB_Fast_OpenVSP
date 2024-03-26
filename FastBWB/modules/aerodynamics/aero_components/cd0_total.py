"""
This file contains one component: "soma_cd0". It is the last component called 
by the "cd0" group and sums the form drags of all the airplane's components. 
It outputs the total form drag, the total form drag in clean configuration and
the parasitic drag for both cruise and low speed conditions, depending on
whether the "low_speed_aero" option is activated or not.
"""

import numpy as np
import openmdao.api as om
from fastoad.module_management.service_registry import RegisterSubmodel


@RegisterSubmodel("soma_cd0", "soma_cd0.2")
class Cd0Total(om.ExplicitComponent):
    """Computes the sum of form drags from aircraft components."""

    def initialize(self):
        self.options.declare("low_speed_aero", default=False, types=bool)

    def setup(self):
        self.add_input("data:geometry:aircraft:wetted_area", val=np.nan, units="m**2")

        if self.options["low_speed_aero"]:
            self.add_input("data:aerodynamics:wing:low_speed:CD0", shape_by_conn=True, val=np.nan) 
            self.add_input(
                "data:aerodynamics:fuselage:low_speed:CD0", shape_by_conn=True, val=np.nan
            ) 
            self.add_input("data:aerodynamics:horizontal_tail:low_speed:CD0", val=np.nan) 
            self.add_input("data:aerodynamics:vertical_tail:low_speed:CD0", val=np.nan) 
            self.add_input("data:aerodynamics:nacelles:low_speed:CD0", val=np.nan) 
            self.add_input("data:aerodynamics:pylons:low_speed:CD0", val=np.nan) 
            self.add_output(
                "data:aerodynamics:aircraft:low_speed:CD0",
                copy_shape="data:aerodynamics:wing:low_speed:CD0",
            )
            self.add_output(
                "data:aerodynamics:aircraft:low_speed:CD0:clean",
                copy_shape="data:aerodynamics:wing:low_speed:CD0",
            )
            self.add_output(
                "data:aerodynamics:aircraft:low_speed:CD0:parasitic",
                copy_shape="data:aerodynamics:wing:low_speed:CD0",
            )
        else:
            self.add_input("data:aerodynamics:wing:cruise:CD0", shape_by_conn=True, val=np.nan) 
            self.add_input("data:aerodynamics:fuselage:cruise:CD0", shape_by_conn=True, val=np.nan)
            self.add_input("data:aerodynamics:horizontal_tail:cruise:CD0", val=np.nan) 
            self.add_input("data:aerodynamics:vertical_tail:cruise:CD0", val=np.nan) 
            self.add_input("data:aerodynamics:nacelles:cruise:CD0", val=np.nan)
            self.add_input("data:aerodynamics:pylons:cruise:CD0", val=np.nan) 
            self.add_output(
                "data:aerodynamics:aircraft:cruise:CD0",
                copy_shape="data:aerodynamics:wing:cruise:CD0",
            ) 
            self.add_output(
                "data:aerodynamics:aircraft:cruise:CD0:clean",
                copy_shape="data:aerodynamics:wing:cruise:CD0",
            ) 
            self.add_output(
                "data:aerodynamics:aircraft:cruise:CD0:parasitic",
                copy_shape="data:aerodynamics:wing:cruise:CD0",
            ) 

    def setup_partials(self):
        self.declare_partials("*", "*", method="fd")

    def compute(self, inputs, outputs, discrete_inputs=None, discrete_outputs=None):
        wet_area_total = inputs["data:geometry:aircraft:wetted_area"]
        if self.options["low_speed_aero"]:
            cd0_wing = inputs["data:aerodynamics:wing:low_speed:CD0"] 
            cd0_fus = inputs["data:aerodynamics:fuselage:low_speed:CD0"]
            cd0_ht = inputs["data:aerodynamics:horizontal_tail:low_speed:CD0"]
            cd0_vt = inputs["data:aerodynamics:vertical_tail:low_speed:CD0"]
            cd0_nac = inputs["data:aerodynamics:nacelles:low_speed:CD0"]
            cd0_pylon = inputs["data:aerodynamics:pylons:low_speed:CD0"]
        else:
            cd0_wing = inputs["data:aerodynamics:wing:cruise:CD0"] 
            cd0_fus = inputs["data:aerodynamics:fuselage:cruise:CD0"]
            cd0_ht = inputs["data:aerodynamics:horizontal_tail:cruise:CD0"]
            cd0_vt = inputs["data:aerodynamics:vertical_tail:cruise:CD0"]
            cd0_nac = inputs["data:aerodynamics:nacelles:cruise:CD0"]
            cd0_pylon = inputs["data:aerodynamics:pylons:cruise:CD0"]
        
        k_techno = 1
        
        # CX0 total
        cd0_total_clean = cd0_fus + cd0_ht + cd0_vt + cd0_pylon + cd0_nac + cd0_wing

        # Cx Parasites
        k_parasite = - 2.39 * pow(10, -12) * wet_area_total ** 3 + 2.58 * pow(
            10, -8) * wet_area_total ** 2 - 0.89 * pow(10, -4) * wet_area_total + 0.163
        
        cd0_parasite = k_parasite * k_techno * cd0_total_clean

        cd0_total = cd0_total_clean + cd0_parasite

        if self.options["low_speed_aero"]:
            outputs["data:aerodynamics:aircraft:low_speed:CD0"] = cd0_total
            outputs["data:aerodynamics:aircraft:low_speed:CD0:clean"] = cd0_total_clean
            outputs["data:aerodynamics:aircraft:low_speed:CD0:parasitic"] = (
                cd0_parasite
            )
        else:
            outputs["data:aerodynamics:aircraft:cruise:CD0"] = cd0_total
            outputs["data:aerodynamics:aircraft:cruise:CD0:clean"] = cd0_total_clean
            outputs["data:aerodynamics:aircraft:cruise:CD0:parasitic"] = cd0_total - cd0_total_clean