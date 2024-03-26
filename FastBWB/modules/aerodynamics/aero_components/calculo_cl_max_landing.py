"""
This file contains the component "calculo_cl_landing" which contains one class
called ComputeMaxClLanding. The class calls the following inputs:
- Max lift coefficient in clean configuration (no lift surfaces deployed)
- Landing Gear CL coefficient - k
- Extra CL produced by the lift surfaces in landing configuration..
The component outputs the max lift coefficient in landing configuration.
"""

import numpy as np
from fastoad.module_management.service_registry import RegisterSubmodel
from openmdao.core.explicitcomponent import ExplicitComponent

@RegisterSubmodel("calculo_cl_landing", "cl_landing.2")
class ComputeMaxClLanding(ExplicitComponent):
    """Computation of max CL in landing conditions."""

    def setup(self):
        self.add_input("data:aerodynamics:aircraft:landing:CL_max_clean", val=np.nan) 
        self.add_input("tuning:aerodynamics:aircraft:cruise:CL:HL_LDG:k", val=np.nan) 
        self.add_input("data:aerodynamics:high_lift_devices:landing:CL", val=np.nan) 
        self.add_output("data:aerodynamics:aircraft:landing:CL_max") 

    def setup_partials(self):
        self.declare_partials("*", "*", method="fd")

    def compute(self, inputs, outputs):
        cl_max_clean = inputs["data:aerodynamics:aircraft:landing:CL_max_clean"]
        delta_cl_landing = inputs["data:aerodynamics:high_lift_devices:landing:CL"]
        k_hl_ldg = inputs["tuning:aerodynamics:aircraft:cruise:CL:HL_LDG:k"]
        cl_max_landing = (cl_max_clean + delta_cl_landing) * k_hl_ldg

        outputs["data:aerodynamics:aircraft:landing:CL_max"] = cl_max_landing

