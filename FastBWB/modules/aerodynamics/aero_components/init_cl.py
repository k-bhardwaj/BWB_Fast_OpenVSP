"""
This file contains one component: "inicializar_cl". It creates a vector ranging
from 0 to 1.5 with a 0.01 step and names it CL. K factors are taken as inputs
to correct the CL values in the vector. This file should be studied and 
improved.
"""

import numpy as np
import openmdao.api as om
from fastoad.module_management.service_registry import RegisterSubmodel

@RegisterSubmodel("inicializar_cl", "init_cl.2")
class InitializeClPolar(om.ExplicitComponent):
    """Initialization of CL vector."""

    def initialize(self):
        self.options.declare("low_speed_aero", default=False, types=bool)

    def setup(self):
        self.add_input("tuning:aerodynamics:aircraft:cruise:CL:k", val=np.nan) 
        self.add_input("tuning:aerodynamics:aircraft:cruise:CL:offset", val=np.nan) 
        self.add_input("tuning:aerodynamics:aircraft:cruise:CL:winglet_effect:k", val=np.nan) 
        self.add_input("tuning:aerodynamics:aircraft:cruise:CL:winglet_effect:offset", val=np.nan) 

        if self.options["low_speed_aero"]:
            self.add_output("data:aerodynamics:aircraft:low_speed:CL", shape=150)
        else:
            self.add_output("data:aerodynamics:aircraft:cruise:CL", shape=150)

    def setup_partials(self):
        self.declare_partials("*", "*", method="fd")

    def compute(self, inputs, outputs, discrete_inputs=None, discrete_outputs=None):
        k_cl = inputs["tuning:aerodynamics:aircraft:cruise:CL:k"]
        offset_cl = inputs["tuning:aerodynamics:aircraft:cruise:CL:offset"]
        k_winglet_cl = inputs["tuning:aerodynamics:aircraft:cruise:CL:winglet_effect:k"]
        offset_winglet_cl = inputs["tuning:aerodynamics:aircraft:cruise:CL:winglet_effect:offset"]

        # FIXME: initialization of CL range should be done more directly, without these coefficients
        cl = np.arange(0.0, 1.5, 0.01) * k_cl * k_winglet_cl + offset_cl + offset_winglet_cl
        # MV: On the current xml file, the k's are 1 and the offsets are 0 so this just generates an array that goes form 0 t0
        # 1.5 with steps of 0.01
        if self.options["low_speed_aero"]:
            outputs["data:aerodynamics:aircraft:low_speed:CL"] = cl
        else:
            outputs["data:aerodynamics:aircraft:cruise:CL"] = cl