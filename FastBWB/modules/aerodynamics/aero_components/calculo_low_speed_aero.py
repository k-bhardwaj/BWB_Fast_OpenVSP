"""
This file contains the component "calculo_low_speed_aero" that computes the
CL_alpha in takeoff configuration. The component contains only one class named
ComputeAerodynamicsLowSpeed.
It takes as inputs the fuselage maximum
height and width, as well as the wing's geometry.
Moreover it fixes a value for the aircraft's CL at null angle of attack and in
clean configuration. A solution for this should be found for tool improvement.
"""

import numpy as np
import openmdao.api as om
from fastoad.module_management.service_registry import RegisterSubmodel


@RegisterSubmodel("calculo_low_speed_aero", "calculo_low_speed.2")
class ComputeAerodynamicsLowSpeed(om.ExplicitComponent):
    """
    Computes CL gradient and CL at low speed.

    CL gradient from :cite:`raymer:1999` Eq 12.6
    """

    def setup(self):
        self.add_input("data:geometry:fuselage:maximum_width", val=np.nan, units="m") 
        self.add_input("data:geometry:fuselage:maximum_height", val=np.nan, units="m") 
        self.add_input("data:geometry:wing:span", val=np.nan, units="m") 
        self.add_input("data:geometry:wing:aspect_ratio", val=np.nan) 
        self.add_input("data:geometry:wing:root:chord", val=np.nan, units="m") 
        self.add_input("data:geometry:wing:sweep_25", val=np.nan, units="deg") 
        self.add_input("data:geometry:wing:tip:chord", val=np.nan, units="m") 
        self.add_input("data:geometry:wing:area", val=np.nan, units="m**2") 
        self.add_input("data:geometry:wing:tip:thickness_ratio", val=np.nan) 

        self.add_output("data:aerodynamics:aircraft:takeoff:CL_alpha", units="1/rad")
        self.add_output("data:aerodynamics:aircraft:takeoff:CL0_clean")

    def setup_partials(self):
        self.declare_partials("*", "*", method="fd")

    def compute(self, inputs, outputs, discrete_inputs=None, discrete_outputs=None):
        width_max = inputs["data:geometry:fuselage:maximum_width"]
        height_max = inputs["data:geometry:fuselage:maximum_height"]
        span = inputs["data:geometry:wing:span"]
        lambda_wing = inputs["data:geometry:wing:aspect_ratio"]
        l2_wing = inputs["data:geometry:wing:root:chord"]
        l4_wing = inputs["data:geometry:wing:tip:chord"]
        el_ext = inputs["data:geometry:wing:tip:thickness_ratio"]
        sweep_25 = inputs["data:geometry:wing:sweep_25"]
        wing_area = inputs["data:geometry:wing:area"]

        mach = 0.2 # FIXME: Mach should not be defined like this

        beta = np.sqrt(1 - mach**2)
        d_f = np.sqrt(width_max * height_max)
        fuselage_lift_factor = 1.07 * (1 + d_f / span) ** 2
        lambda_wing_eff = lambda_wing * (1 + 1.9 * l4_wing * el_ext / span)
        cl_alpha_wing_low = (
            2
            * np.pi
            * lambda_wing_eff
            / (
                2
                + np.sqrt(
                    4
                    + lambda_wing_eff**2
                    * beta**2
                    / 0.95**2
                    * (1 + (np.tan(sweep_25 / 180.0 * np.pi)) ** 2 / beta**2)
                )
            )
            * (wing_area - l2_wing * width_max)
            / wing_area
            * fuselage_lift_factor
        )

        outputs["data:aerodynamics:aircraft:takeoff:CL_alpha"] = cl_alpha_wing_low
        outputs["data:aerodynamics:aircraft:takeoff:CL0_clean"] = 0.2  # FIXME: hard-coded value