"""
This file contains one component called "cd_compressibility" that computes the
compressibility drag coefficient at cruise. It takes as inputs the cruise CL 
and the TLAR Mach number.
"""


import numpy as np
import math
import openmdao.api as om
from fastoad.module_management.service_registry import RegisterSubmodel


@RegisterSubmodel(
    "cd_compressibility", "cd_comp.2"
)
class CdCompressibility(om.ExplicitComponent):


    def setup(self):

        self.add_input("data:TLAR:cruise_mach", val=np.nan) 
        self.add_input("data:aerodynamics:aircraft:cruise:CL", shape_by_conn=True, val=np.nan) 
        self.add_output(
            "data:aerodynamics:aircraft:cruise:CD:compressibility",
            copy_shape="data:aerodynamics:aircraft:cruise:CL",
        )

    def setup_partials(self):
        self.declare_partials("*", "*", method="fd")

    def compute(self, inputs, outputs, discrete_inputs=None, discrete_outputs=None):
        cl = inputs["data:aerodynamics:aircraft:cruise:CL"]
        m = inputs["data:TLAR:cruise_mach"]

        m_charac_comp = np.empty_like(cl)
        cd_comp = np.empty_like(cl) 
        
        for i in range(cl.size):
            m_charac_comp[i] = - 0.5 * cl[i] ** 2 + 0.35 * cl[i] + 0.765  

        for i in range(m_charac_comp.size):
            cd_comp[i] = 0.002 * math.exp(42.58 * (m - m_charac_comp[i]))

        outputs["data:aerodynamics:aircraft:cruise:CD:compressibility"] = cd_comp