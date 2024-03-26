"""
This file contains one component: "calculo_cd_equilibrio", which computes
the aditional drag penalties induced by the trim of the aircraft due to the 
wing vortexes influence behind the wing, It computes the CD_trim in low speed
and cruise conditions, depending on whether the "low_speed_aero" option is 
declared or not. It takes as inputs the initialized CL vector from init_cl.py
in either cruise or low speed conditions.
"""

import numpy as np
import openmdao.api as om
from fastoad.module_management.service_registry import RegisterSubmodel



@RegisterSubmodel("calculo_cd_equilibrio", "cd_equilibrio.2")
class CdTrim(om.ExplicitComponent):
    """Computation of trim drag."""

    def initialize(self):
        self.options.declare("low_speed_aero", default=False, types=bool)

    def setup(self):
        if self.options["low_speed_aero"]:
            self.add_input(
                "data:aerodynamics:aircraft:low_speed:CL", shape_by_conn=True, val=np.nan
            ) 
            self.add_output(
                "data:aerodynamics:aircraft:low_speed:CD:trim",
                copy_shape="data:aerodynamics:aircraft:low_speed:CL",
            )
        else:
            self.add_input("data:aerodynamics:aircraft:cruise:CL", shape_by_conn=True, val=np.nan)
            self.add_output(
                "data:aerodynamics:aircraft:cruise:CD:trim",
                copy_shape="data:aerodynamics:aircraft:cruise:CL",
            )

    def setup_partials(self):
        self.declare_partials("*", "*", method="fd")

    def compute(self, inputs, outputs, discrete_inputs=None, discrete_outputs=None):
        if self.options["low_speed_aero"]:
            cl = inputs["data:aerodynamics:aircraft:low_speed:CL"]
        else:
            cl = inputs["data:aerodynamics:aircraft:cruise:CL"]

        cd_trim = []

        for cl_val in cl:
            cd_trim.append(5.89 * pow(10, -4) * cl_val)

        if self.options["low_speed_aero"]:
            outputs["data:aerodynamics:aircraft:low_speed:CD:trim"] = cd_trim
        else:
            outputs["data:aerodynamics:aircraft:cruise:CD:trim"] = cd_trim