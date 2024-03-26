"""
This file contains one component: "calculo_cd0_vertical_tail" which computes 
the vertical tail's form drag for cruise or low speed conditions, depending on
whether the "low_speed_aero" option is activated or not. 
This component is called by the "cd0" group.
It takes as inputs the Reynolds, the Mach and the CL, as well as the vertical
tail geometry.
"""

import numpy as np
import math
import openmdao.api as om
from fastoad.module_management.service_registry import RegisterSubmodel


@RegisterSubmodel(
    "calculo_cd0_vertical_tail", "cd0_vertical_tail_2")
class Cd0VerticalTail(om.ExplicitComponent):

    def initialize(self):
        self.options.declare("low_speed_aero", default=False, types=bool)

    def setup(self):
        self.add_input("data:geometry:vertical_tail:MAC:length", val=np.nan, units="m") 
        self.add_input("data:geometry:vertical_tail:thickness_ratio", val=np.nan) 
        self.add_input("data:geometry:vertical_tail:sweep_25", val=np.nan, units="deg") 
        self.add_input("data:geometry:vertical_tail:wetted_area", val=np.nan, units="m**2") 
        self.add_input("data:geometry:wing:area", val=np.nan, units="m**2") 
        if self.options["low_speed_aero"]:
            self.add_input("data:aerodynamics:wing:low_speed:reynolds", val=np.nan) 
            self.add_input("data:aerodynamics:aircraft:takeoff:mach", val=np.nan) 
            self.add_output("data:aerodynamics:vertical_tail:low_speed:CD0") 
        else:
            self.add_input("data:aerodynamics:wing:cruise:reynolds", val=np.nan) 
            self.add_input("data:TLAR:cruise_mach", val=np.nan) 
            self.add_output("data:aerodynamics:vertical_tail:cruise:CD0") 

    def setup_partials(self):
        self.declare_partials("*", "*", method="fd")

    def compute(self, inputs, outputs, discrete_inputs=None, discrete_outputs=None):
        wing_area = inputs["data:geometry:wing:area"] 
        el_vt = inputs["data:geometry:vertical_tail:thickness_ratio"] 
        sweep_25_vt = inputs["data:geometry:vertical_tail:sweep_25"] 
        vt_length = inputs["data:geometry:vertical_tail:MAC:length"] 
        wet_area_vt = inputs["data:geometry:vertical_tail:wetted_area"] 
        if self.options["low_speed_aero"]:
            mach = inputs["data:aerodynamics:aircraft:takeoff:mach"] 
            reynolds = inputs["data:aerodynamics:wing:low_speed:reynolds"] 
        else:
            mach = inputs["data:TLAR:cruise_mach"] 
            reynolds = inputs["data:aerodynamics:wing:cruise:reynolds"] 
        
        ki_arrow_cx0 = 0.04
        
        cf_vt_hs = 0.455 / ((1 + 0.126 * mach ** 2) * (math.log10(reynolds * vt_length)) ** (2.58))
            
        ke_cx0_vt = 4.688 * el_vt ** 2 + 3.146 * el_vt
        k_phi_cx0_vt = 1 - 0.000178 * \
            (sweep_25_vt) ** 2 - 0.0065 * (sweep_25_vt)  
        cx0_vt_hs = (ke_cx0_vt * k_phi_cx0_vt + ki_arrow_cx0 / 8 + 1) * \
            cf_vt_hs * wet_area_vt / wing_area

        if self.options["low_speed_aero"]:
            outputs["data:aerodynamics:vertical_tail:low_speed:CD0"] = cx0_vt_hs
        else:
            outputs["data:aerodynamics:vertical_tail:cruise:CD0"] = cx0_vt_hs