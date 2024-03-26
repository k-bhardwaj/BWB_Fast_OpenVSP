"""
This file contains one component: "calculo_coeficiente_reynolds" that computes
the reynolds coefficient at either low speed or cruise conditions. The 
execution of one of these two cases is determined by the option 
"low_speed_aero".

The component takes as inputs the TLAR mach number and the cruise altitude.
"""


import numpy as np
from fastoad.module_management.service_registry import RegisterSubmodel
from openmdao.core.explicitcomponent import ExplicitComponent
from stdatm import AtmosphereSI

@RegisterSubmodel(
    "calculo_coeficiente_reynolds", "coeficiente_reynolds.2"
)
class ComputeReynolds(ExplicitComponent):
    """Computation of Reynolds number"""

    def initialize(self):
        self.options.declare("low_speed_aero", default=False, types=bool)

    def setup(self):
        if self.options["low_speed_aero"]:
            self.add_input("data:aerodynamics:aircraft:takeoff:mach", val=np.nan) 
            self.add_output("data:aerodynamics:wing:low_speed:reynolds") 
        else:
            self.add_input("data:TLAR:cruise_mach", val=np.nan) 
            self.add_input("data:mission:sizing:main_route:cruise:altitude", val=np.nan, units="m") 
            self.add_output("data:aerodynamics:wing:cruise:reynolds")

    def setup_partials(self):
        self.declare_partials("*", "*", method="fd")

    def compute(self, inputs, outputs, discrete_inputs=None, discrete_outputs=None):
        if self.options["low_speed_aero"]:
            mach = inputs["data:aerodynamics:aircraft:takeoff:mach"]
            altitude = 0.0
        else:
            mach = inputs["data:TLAR:cruise_mach"]
            altitude = inputs["data:mission:sizing:main_route:cruise:altitude"]

        atm = AtmosphereSI(altitude)
        atm.mach = mach
        reynolds = atm.unitary_reynolds

        if self.options["low_speed_aero"]:
            outputs["data:aerodynamics:wing:low_speed:reynolds"] = reynolds
        else:
            outputs["data:aerodynamics:wing:cruise:reynolds"] = reynolds
