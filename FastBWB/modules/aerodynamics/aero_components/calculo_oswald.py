"""
This file contains two components: "calculo_induced_drag_coefficient" and 
"calculo_oswald". 

The first component computes the induced drag in either low speed or cruise
conditions, depending on whether it is being called in the file 
aerodynamics_high_speed.py or aerodynamics_low_speed.py. For that purpose, it
takes as input the wing's aspect ratio and the oswald coefficient.

The oswald coefficient, in turn, is computed by the component "calculo_oswald"
coded further below. It takes the fuselage's maximum width and length as well
as the wing's geometry to do so.
"""

import math
import numpy as np
import openmdao.api as om
from fastoad.module_management.service_registry import RegisterSubmodel


@RegisterSubmodel("calculo_induced_drag_coefficient", "induced_drag_coefficient.2")
class DragInduzido(om.ExplicitComponent):
    """Computes the coefficient that should be multiplied by CL**2 to get induced drag."""

    def initialize(self):
        self.options.declare("low_speed_aero", default=False, types=bool)

    def setup(self):
        self.add_input("data:geometry:wing:aspect_ratio", val=np.nan)

        if self.options["low_speed_aero"]:
            self.add_input("data:aerodynamics:aircraft:low_speed:oswald_coefficient", val=np.nan) 
            self.add_output("data:aerodynamics:aircraft:low_speed:induced_drag_coefficient")
        else:
            self.add_input("data:aerodynamics:aircraft:cruise:oswald_coefficient", val=np.nan)
            self.add_output("data:aerodynamics:aircraft:cruise:induced_drag_coefficient")

 
    def setup_partials(self):
        self.declare_partials("*", "*", method="fd")


    def compute(self, inputs, outputs, discrete_inputs=None, discrete_outputs=None):
        aspect_ratio = inputs["data:geometry:wing:aspect_ratio"]

        if self.options["low_speed_aero"]:
            coef_e = inputs["data:aerodynamics:aircraft:low_speed:oswald_coefficient"]
        else:
            coef_e = inputs["data:aerodynamics:aircraft:cruise:oswald_coefficient"]

        coef_k = 1.0 / (np.pi * aspect_ratio * coef_e)

        if self.options["low_speed_aero"]:
            outputs["data:aerodynamics:aircraft:low_speed:induced_drag_coefficient"] = coef_k
        else:
            outputs["data:aerodynamics:aircraft:cruise:induced_drag_coefficient"] = coef_k

@RegisterSubmodel("calculo_oswald", "coeficiente_oswald.2")
class calculo_oswald(om.ExplicitComponent):
    """Computation of coef_e"""
    
    def initialize(self):
        self.options.declare("low_speed_aero", default=False, types=bool)
        
    def setup(self):
        self.add_input("data:geometry:wing:span", val=np.nan, units="m")
        self.add_input("data:geometry:fuselage:maximum_height", val=np.nan, units="m")
        self.add_input("data:geometry:fuselage:maximum_width", val=np.nan, units="m")
        self.add_input("data:geometry:wing:root:chord", val=np.nan, units="m") 
        self.add_input("data:geometry:wing:tip:chord", val=np.nan, units="m") 
        self.add_input("data:geometry:wing:sweep_25", val=np.nan, units="deg")
        self.add_input("data:geometry:wing:area", val=np.nan, units="m**2")
        
        if self.options["low_speed_aero"]:
            self.add_input("data:aerodynamics:aircraft:takeoff:mach", val=np.nan)
            self.add_output("data:aerodynamics:aircraft:low_speed:oswald_coefficient")
        else:
            self.add_input("data:TLAR:cruise_mach", val=np.nan)
            self.add_output("data:aerodynamics:aircraft:cruise:oswald_coefficient")
            

    def compute(self, inputs, outputs, discrete_inputs=None, discrete_outputs=None):
        
        l2_wing = inputs["data:geometry:wing:root:chord"] 
        l4_wing = inputs["data:geometry:wing:tip:chord"] 
        height_fus = inputs["data:geometry:fuselage:maximum_height"]
        width_fus = inputs["data:geometry:fuselage:maximum_width"]
        sweep_25 = inputs["data:geometry:wing:sweep_25"]
        wing_area = inputs["data:geometry:wing:area"]
        span = inputs["data:geometry:wing:span"]
        
        if self.options["low_speed_aero"]:
            mach = inputs["data:aerodynamics:aircraft:takeoff:mach"]
        else:
            mach = inputs["data:TLAR:cruise_mach"]
            
        span = span / math.cos(5. / 180 * math.pi)
        df = math.sqrt(width_fus * height_fus) 
        lamda = l4_wing / l2_wing 
        delta_lamda = -0.357 + 0.45 * math.exp(0.0375 * sweep_25 / 180. * math.pi) 
        lamda = lamda - delta_lamda
        f_lamda = 0.0524 * lamda**4 - 0.15 * lamda**3 + 0.1659 * lamda**2 - 0.0706 * lamda + 0.0119 
        e_theory = 1 / (1 + f_lamda * span**2 / wing_area) 

        if mach <= 0.4: 
            ke_m = 1.
        else:
            ke_m = -0.001521 * ((mach - 0.05) / 0.3 - 1)**10.82 + 1

        ke_f = 1 - 2 * (df / span)**2
        coef_e = e_theory * ke_f * ke_m * 0.9
        
        if self.options["low_speed_aero"]:
            outputs["data:aerodynamics:aircraft:low_speed:oswald_coefficient"] = coef_e
        else:
            outputs["data:aerodynamics:aircraft:cruise:oswald_coefficient"] = coef_e
        