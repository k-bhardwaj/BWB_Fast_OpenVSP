"""
This file contains one component: "calculo_cd0_nacelles_pylons" which computes 
the nacelles' and pylons' form drag for cruise or low speed conditions, 
depending on whether the "low_speed_aero" option is activated or not. 
This component is called by the "cd0" group.
It takes as inputs the Reynolds, the Mach and the CL, as well as the nacelles'
and pylons' geometry.
"""

import math
import numpy as np
import openmdao.api as om
from fastoad.module_management.service_registry import RegisterSubmodel


@RegisterSubmodel(
    "calculo_cd0_nacelles_pylons", "cd0_nacelles_pylons_2"
)
class Cd0NacellesAndPylons(om.ExplicitComponent):
    """Computation of form drag for nacelles and pylons."""

    def initialize(self):
        self.options.declare("low_speed_aero", default=False, types=bool)

    def setup(self):
        if self.options["low_speed_aero"]:
            self.add_input("data:aerodynamics:wing:low_speed:reynolds", val=np.nan)
            self.add_input("data:aerodynamics:aircraft:takeoff:mach", val=np.nan)
            self.add_output("data:aerodynamics:nacelles:low_speed:CD0")
            self.add_output("data:aerodynamics:pylons:low_speed:CD0")
        else:
            self.add_input("data:aerodynamics:wing:cruise:reynolds", val=np.nan)
            self.add_input("data:TLAR:cruise_mach", val=np.nan)
            self.add_output("data:aerodynamics:nacelles:cruise:CD0")
            self.add_output("data:aerodynamics:pylons:cruise:CD0")

        self.add_input("data:geometry:propulsion:pylon:length", val=np.nan, units="m")
        self.add_input("data:geometry:propulsion:nacelle:length", val=np.nan, units="m")
        self.add_input("data:geometry:propulsion:pylon:wetted_area", val=np.nan, units="m**2")
        self.add_input("data:geometry:propulsion:nacelle:wetted_area", val=np.nan, units="m**2")
        self.add_input("data:geometry:propulsion:engine:count", val=np.nan)
        self.add_input("data:geometry:propulsion:fan:length", val=np.nan, units="m")
        self.add_input("data:geometry:wing:area", val=np.nan, units="m**2")

    def setup_partials(self):
        self.declare_partials("*", "*", method="fd")

    def compute(self, inputs, outputs, discrete_inputs=None, discrete_outputs=None):
        n_engines = inputs["data:geometry:propulsion:engine:count"] 
        wing_area = inputs["data:geometry:wing:area"] 
        if self.options["low_speed_aero"]:
            mach = inputs["data:aerodynamics:aircraft:takeoff:mach"] 
            reynolds = inputs["data:aerodynamics:wing:low_speed:reynolds"] 
        else:
            mach = inputs["data:TLAR:cruise_mach"] 
            reynolds = inputs["data:aerodynamics:wing:cruise:reynolds"] 

        pylon_length = inputs["data:geometry:propulsion:pylon:length"] 
        wet_area_pylon = inputs["data:geometry:propulsion:pylon:wetted_area"] 
        nac_length = inputs["data:geometry:propulsion:nacelle:length"] 
        wet_area_nac = inputs["data:geometry:propulsion:nacelle:wetted_area"] 
        fan_length = inputs["data:geometry:propulsion:fan:length"] 
        
        e_fan = 0.22 

        cf_pylon_hs = 0.455 / ((1 + 0.126 * mach ** 2) * (math.log10(reynolds * pylon_length)) ** (2.58))
        cf_nac_hs = 0.455 / ((1 + 0.126 * mach ** 2) * (math.log10(reynolds * nac_length)) ** (2.58))
        
        # CX0 Pylon
        el_pylon = 0.06
        ke_cx0_pylon = 4.688 * el_pylon ** 2 + 3.146 * el_pylon
        cx0_pylon_hs = n_engines * \
            (1 + ke_cx0_pylon) * cf_pylon_hs * wet_area_pylon / wing_area
        
        # CX0 Nacelles
        kn_cx0_nac = 1 + 0.05 + 5.8 * e_fan / fan_length
        cx0_int_nac = 0.0002
        cx0_nac_hs = n_engines * (kn_cx0_nac * cf_nac_hs * wet_area_nac / wing_area + cx0_int_nac)
            
        if self.options["low_speed_aero"]:
            outputs["data:aerodynamics:pylons:low_speed:CD0"] = cx0_pylon_hs
            outputs["data:aerodynamics:nacelles:low_speed:CD0"] = cx0_nac_hs
        else:
            outputs["data:aerodynamics:pylons:cruise:CD0"] = cx0_pylon_hs
            outputs["data:aerodynamics:nacelles:cruise:CD0"] = cx0_nac_hs