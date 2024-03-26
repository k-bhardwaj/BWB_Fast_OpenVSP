"""
Estimation of control surfaces center of gravity
------------------------------------------------------

"""
import numpy as np
import openmdao.api as om
from fastoad.module_management.service_registry import RegisterSubmodel
from scipy.interpolate import interp1d

from ..constantscg import SERVICE_FLIGHT_CONTROLS_CG


@RegisterSubmodel(
    SERVICE_FLIGHT_CONTROLS_CG, "fastoad.submodel.weight.cg.wing.control_surfaces.BWBtest.1"
)
class ComputeControlSurfacesCG(om.ExplicitComponent):
    # TODO: Document equations. Cite sources
    """Control surfaces center of gravity estimation"""

    def setup(self):
        self.add_input("data:geometry:wing:MAC:at25percent:x", val=np.nan, units="m")
        self.add_input("data:geometry:wing:MAC:leading_edge:x:local", val=np.nan, units="m")
        self.add_input("data:geometry:wing:MAC:length", val=np.nan, units="m")
        self.add_input("data:geometry:wing:MAC:y", val=np.nan, units="m")
        self.add_input("data:geometry:wing:root:chord", val=np.nan, units="m")
        self.add_input("data:geometry:wing:root:y", val=np.nan, units="m")
        self.add_input("data:geometry:wing:kink:chord", val=np.nan, units="m")
        self.add_input("data:geometry:wing:kink:leading_edge:x:local", val=np.nan, units="m")
        self.add_input("data:geometry:wing:kink:y", val=np.nan, units="m")
        self.add_input("data:geometry:wing:tip:chord", val=np.nan, units="m")
        self.add_input("data:geometry:wing:tip:leading_edge:x:local", val=np.nan, units="m")
        self.add_input("data:geometry:wing:tip:y", val=np.nan, units="m")

        self.add_output("data:weight:airframe:flight_controls:CG:x", units="m")

    def setup_partials(self):
        self.declare_partials("*", "*", method="fd")

    def compute(self, inputs, outputs, discrete_inputs=None, discrete_outputs=None):
        # TODO: build generic functions to estimate the chord, leading edge,
        #  control CG is assumed located at trailing edge with respect to MAC span wise position
        y_values = np.squeeze(
            [
                inputs["data:geometry:wing:root:y"],
                inputs["data:geometry:wing:kink:y"],
                inputs["data:geometry:wing:tip:y"],
            ]
        )
        x_values = np.squeeze(
            [
                [0.0],
                inputs["data:geometry:wing:kink:leading_edge:x:local"],
                inputs["data:geometry:wing:tip:leading_edge:x:local"],
            ]
        )
        l_values = np.squeeze(
            [
                inputs["data:geometry:wing:root:chord"],
                inputs["data:geometry:wing:kink:chord"],
                inputs["data:geometry:wing:tip:chord"],
            ]
        )

        x_interp = interp1d(y_values, x_values)
        x_leading_edge = x_interp(inputs["data:geometry:wing:MAC:y"])
        l_interp = interp1d(y_values, l_values)
        l_cg_control = l_interp(inputs["data:geometry:wing:MAC:y"])
        x_cg_control = x_leading_edge + l_cg_control

        outputs["data:weight:airframe:flight_controls:CG:x"] = (
            inputs["data:geometry:wing:MAC:at25percent:x"]
            - 0.25 * inputs["data:geometry:wing:MAC:length"]
            - inputs["data:geometry:wing:MAC:leading_edge:x:local"]
            + x_cg_control
        )
