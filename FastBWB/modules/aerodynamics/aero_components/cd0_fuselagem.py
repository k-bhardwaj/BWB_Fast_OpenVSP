"""
This file contains one component: "calculo_form_drag_fuselagem" which computes 
the fuselage's form drag for cruise or low speed conditions, depending on
whether the "low_speed_aero" option is activated or not. 
This component is called by the "cd0" group.
It takes as inputs the Reynolds, the Mach and the CL, as well as the fuselage's
geometry.
"""

import math
import numpy as np
import openmdao.api as om
from fastoad.module_management.service_registry import RegisterSubmodel


@RegisterSubmodel(
    "calculo_form_drag_fuselagem", "cd0_fuselagem.2")

class cd0_fuselagem(om.ExplicitComponent):
    """Computes the coefficient that should be multiplied by CL**2 to get induced drag."""

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
                "data:aerodynamics:fuselage:low_speed:CD0",
                copy_shape="data:aerodynamics:aircraft:low_speed:CL",
            ) 
        else:
            self.add_input("data:aerodynamics:wing:cruise:reynolds", val=np.nan) 
            self.add_input("data:aerodynamics:aircraft:cruise:CL", shape_by_conn=True, val=np.nan) 
            self.add_input("data:TLAR:cruise_mach", val=np.nan) 
            self.add_output(
                "data:aerodynamics:fuselage:cruise:CD0",
                copy_shape="data:aerodynamics:aircraft:cruise:CL",
            ) 

        self.add_input("data:geometry:wing:area", val=np.nan, units="m**2") 
        self.add_input("data:geometry:fuselage:length", val=np.nan, units="m") 
        self.add_input("data:geometry:fuselage:maximum_width", val=np.nan, units="m") 
        self.add_input("data:geometry:fuselage:maximum_height", val=np.nan, units="m") 
        self.add_input("data:geometry:fuselage:wetted_area", val=np.nan, units="m**2") 
        self.add_input("data:geometry:configuration", val=np.nan) 
        self.add_input("data:geometry:fuselage:toc_centerbody", val=np.nan) 
        self.add_input("data:geometry:fuselage:sweep_25_centerbody", val=np.nan, units="deg") 

    def setup_partials(self):
        self.declare_partials("*", "*", method="fd")

    def compute(self, inputs, outputs, discrete_inputs=None, discrete_outputs=None):
        height_max = inputs["data:geometry:fuselage:maximum_height"] 
        width_max = inputs["data:geometry:fuselage:maximum_width"] 
        wet_area_fus = inputs["data:geometry:fuselage:wetted_area"] 
        wing_area = inputs["data:geometry:wing:area"] 
        fus_length = inputs["data:geometry:fuselage:length"] 
        configuration = inputs["data:geometry:configuration"] 
        el_fus = inputs["data:geometry:fuselage:toc_centerbody"] 
        sweep_25_cb = inputs["data:geometry:fuselage:sweep_25_centerbody"] 
        if self.options["low_speed_aero"]:
            cl = inputs["data:aerodynamics:aircraft:low_speed:CL"] 
            mach = inputs["data:aerodynamics:aircraft:takeoff:mach"] 
            reynolds = inputs["data:aerodynamics:wing:low_speed:reynolds"] 
        else:
            cl = inputs["data:aerodynamics:aircraft:cruise:CL"] 
            mach = inputs["data:TLAR:cruise_mach"] 
            reynolds = inputs["data:aerodynamics:wing:cruise:reynolds"] 
        
        ki_arrow_cx0 = 0.04
        
        cf_fus_hs = 0.455 / ((1 + 0.126 * mach ** 2) * (math.log10(reynolds * fus_length)) ** (2.58))
        
        if configuration == 1:
            cx0_friction_fus_hs = (0.98 + 0.745 * math.sqrt(height_max *
                                                            width_max) / fus_length) * \
                cf_fus_hs * wet_area_fus / wing_area
            cx0_upsweep_fus_hs = (
                0.0029 * cl ** 2 - 0.0066 * cl + 0.0043) * (
                0.67 * 3.6 * height_max * width_max) / wing_area
            cx0_fus_hs = cx0_friction_fus_hs + cx0_upsweep_fus_hs
        elif configuration == 2:
            ke_cx0_fus = 4.688 * el_fus ** 2 + 3.146 * el_fus
            kc_cx0_fus = 2.859 * (cl / (math.cos(sweep_25_cb / 180. * math.pi))**2) ** 3 \
                - 1.849 * (cl / (math.cos(sweep_25_cb / 180. * math.pi))**2) ** 2 + 0.382 * \
                (cl / (math.cos(sweep_25_cb / 180. * math.pi))**2) + 0.06    
            k_phi_cx0_fus = 1 - 0.000178 * \
                (sweep_25_cb) ** 2 - 0.0065 * (sweep_25_cb)  
            cx0_fus_hs = ((ke_cx0_fus + kc_cx0_fus) * k_phi_cx0_fus +
                        ki_arrow_cx0 + 1) * cf_fus_hs * wet_area_fus / wing_area
            
            
        if self.options["low_speed_aero"]:
            outputs["data:aerodynamics:fuselage:low_speed:CD0"] = cx0_fus_hs
        else:
            outputs["data:aerodynamics:fuselage:cruise:CD0"] = cx0_fus_hs