"""
This file contains one component: "calculo_cd0_asa" which computes the wing 
form drag for cruise or low speed conditions, depending on whether the 
"low_speed_aero" option is activated or not. 
This component is called by the "cd0" group.
It takes as inputs the Reynolds, the Mach and the CL, as well as the wing
geometry.
"""

import math
import numpy as np
import openmdao.api as om
from fastoad.module_management.service_registry import RegisterSubmodel

@RegisterSubmodel("calculo_cd0_asa", "cd0_asa.2")
class Cd0Wing(om.ExplicitComponent):

    def initialize(self):
        self.options.declare("low_speed_aero", default=False, types=bool)

    def setup(self):
        if self.options["low_speed_aero"]:
            self.add_input("data:aerodynamics:wing:low_speed:reynolds", val=np.nan) 
            self.add_input(
                "data:aerodynamics:aircraft:low_speed:CL", shape_by_conn=True, val=np.nan
            ) 
            self.add_input("data:aerodynamics:aircraft:takeoff:mach", val=np.nan) 
            self.add_output(
                "data:aerodynamics:wing:low_speed:CD0",
                copy_shape="data:aerodynamics:aircraft:low_speed:CL",
            ) 
        else:
            self.add_input("data:aerodynamics:wing:cruise:reynolds", val=np.nan) 
            self.add_input("data:aerodynamics:aircraft:cruise:CL", shape_by_conn=True, val=np.nan) 
            self.add_input("data:TLAR:cruise_mach", val=np.nan) 
            self.add_output(
                "data:aerodynamics:wing:cruise:CD0",
                copy_shape="data:aerodynamics:aircraft:cruise:CL",
            ) 

        self.add_input("data:geometry:wing:area", val=np.nan, units="m**2") 
        self.add_input("data:geometry:wing:wetted_area", val=np.nan, units="m**2") 
        self.add_input("data:geometry:wing:MAC:length", val=np.nan, units="m") 
        self.add_input("data:geometry:wing:sweep_25", val=np.nan, units="deg") 
        self.add_input("data:geometry:wing:thickness_ratio", val=np.nan) 

    def setup_partials(self):
        self.declare_partials("*", "*", method="fd")

    def compute(self, inputs, outputs, discrete_inputs=None, discrete_outputs=None):
        
        l0_wing = inputs["data:geometry:wing:MAC:length"]
        sweep_25 = inputs["data:geometry:wing:sweep_25"]
        wing_area = inputs["data:geometry:wing:area"]
        wet_area_wing = inputs["data:geometry:wing:wetted_area"]
        el_aero = inputs["data:geometry:wing:thickness_ratio"]
        
        if self.options["low_speed_aero"]:
            cl = inputs["data:aerodynamics:aircraft:low_speed:CL"]
            mach = inputs["data:aerodynamics:aircraft:takeoff:mach"]
            reynolds = inputs["data:aerodynamics:wing:low_speed:reynolds"]
        else:
            cl = inputs["data:aerodynamics:aircraft:cruise:CL"]
            mach = inputs["data:TLAR:cruise_mach"]
            reynolds = inputs["data:aerodynamics:wing:cruise:reynolds"]
            
        ki_arrow_cx0 = 0.04
            
        cf_wing = 0.455 / ((1 + 0.126 * mach ** 2) * (math.log10(reynolds * l0_wing)) ** (2.58))
        
           
        ke_cx0_wing = 4.688 * el_aero ** 2 + 3.146 * el_aero
        kc_cx0_wing = 2.859 * (cl / (math.cos(sweep_25 / 180. * math.pi))**2) ** 3 \
            - 1.849 * (cl / (math.cos(sweep_25 / 180. * math.pi))**2) ** 2 + 0.382 * \
            (cl / (math.cos(sweep_25 / 180. * math.pi))**2) + 0.06    
        k_phi_cx0_wing = 1 - 0.000178 * \
            (sweep_25) ** 2 - 0.0065 * (sweep_25)  
        cx0_wing = ((ke_cx0_wing + kc_cx0_wing) * k_phi_cx0_wing +
                    ki_arrow_cx0 + 1) * cf_wing * wet_area_wing / wing_area

        if self.options["low_speed_aero"]:
            outputs["data:aerodynamics:wing:low_speed:CD0"] = cx0_wing
        else:
            outputs["data:aerodynamics:wing:cruise:CD0"] = cx0_wing
            
    