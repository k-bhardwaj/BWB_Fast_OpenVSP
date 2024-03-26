"""Component not used as there is no horizontal tail."""

import math
import numpy as np
import openmdao.api as om
from fastoad.module_management.service_registry import RegisterSubmodel

@RegisterSubmodel(
    "calculo_cd0_horizontal_tail", "cd0_horizontal_tail_2")
class Cd0HorizontalTail(om.ExplicitComponent):
    """
    Computation of form drag for Horizontal Tail Plane.

    See :meth:`~fastoad_cs25.models.aerodynamics.components.utils.cd0_lifting_surface`
    for used method.
    """

    def initialize(self):
        self.options.declare("low_speed_aero", default=False, types=bool)

    def setup(self):
        self.add_input("data:geometry:horizontal_tail:MAC:length", val=np.nan, units="m") # Checked
        self.add_input("data:geometry:horizontal_tail:el", val=np.nan) # Checked
        self.add_input("data:geometry:horizontal_tail:sweep_25", val=np.nan, units="deg") # Checked
        self.add_input("data:geometry:horizontal_tail:wetted_area", val=np.nan, units="m**2") # Checked
        self.add_input("data:geometry:wing:area", val=np.nan, units="m**2") # Checked
        self.add_input("data:geometry:configuration", val=np.nan) # Checked

        if self.options["low_speed_aero"]:
            self.add_input("data:aerodynamics:wing:low_speed:reynolds", val=np.nan) # Checked
            self.add_input("data:aerodynamics:aircraft:takeoff:mach", val=np.nan) # Checked
            self.add_output("data:aerodynamics:horizontal_tail:low_speed:CD0") # Checked
        else:
            self.add_input("data:aerodynamics:wing:cruise:reynolds", val=np.nan) # Checked
            self.add_input("data:TLAR:cruise_mach", val=np.nan) # Checked
            self.add_output("data:aerodynamics:horizontal_tail:cruise:CD0") # Checked

    def setup_partials(self):
        self.declare_partials("*", "*", method="fd")

    def compute(self, inputs, outputs, discrete_inputs=None, discrete_outputs=None):

        wing_area = inputs["data:geometry:wing:area"]
        el_ht = inputs["data:geometry:horizontal_tail:el"]
        sweep_25_ht = inputs["data:geometry:horizontal_tail:sweep_25"]
        configuration = inputs["data:geometry:configuration"]
        ht_length = inputs["data:geometry:horizontal_tail:MAC:length"]
        wet_area_ht = inputs["data:geometry:horizontal_tail:wetted_area"]
        if self.options["low_speed_aero"]:
            mach = inputs["data:aerodynamics:aircraft:takeoff:mach"]
            reynolds = inputs["data:aerodynamics:wing:low_speed:reynolds"]
        else:
            mach = inputs["data:TLAR:cruise_mach"]
            reynolds = inputs["data:aerodynamics:wing:cruise:reynolds"]
        
        ki_arrow_cx0 = 0.04
        
        if configuration == 1:
            cf_ht_hs = 0.455 / ((1 + 0.126 * mach ** 2) * (math.log10(reynolds * ht_length)) ** (2.58))
        else:
            cf_ht_hs = 0.
            
        # CX0 Horizontal Tailplane
        ke_cx0_ht = 4.688 * el_ht ** 2 + 3.146 * el_ht
        k_phi_cx0_ht = 1 - 0.000178 * \
            (sweep_25_ht) ** 2 - 0.0065 * (sweep_25_ht)  # sweep_25 in degrees
        cx0_ht_hs = (ke_cx0_ht * k_phi_cx0_ht + ki_arrow_cx0 / 4 + 1) * \
            cf_ht_hs * wet_area_ht / wing_area

        if self.options["low_speed_aero"]:
            outputs["data:aerodynamics:horizontal_tail:low_speed:CD0"] = cx0_ht_hs
        else:
            outputs["data:aerodynamics:horizontal_tail:cruise:CD0"] = cx0_ht_hs