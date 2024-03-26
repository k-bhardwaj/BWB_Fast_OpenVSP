"""
Estimation of engine weight - B1 component
---------------------------------------------
- Registered under the name "fastoad.submodel.weight.mass.propulsion.engine.BWBtest.1"
Computed analytically according to sea level thrust.

"""
import numpy as np
import openmdao.api as om
from fastoad.module_management.service_registry import RegisterSubmodel

from .constants import SERVICE_ENGINE_MASS_BWB


# TODO:  this is also provided by class RubberEngine
"""
    The registering of a class is done with::

        @RegisterSubmodel("my.service", "id.of.the.provider")
        class MyService:º
            ...

    Then the submodel can be instantiated and used with::

        submodel_instance = RegisterSubmodel.get_submodel("my.service")
        some_model.add_subsystem("my_submodel", submodel_instance, promotes=["*"])
        ...
    """
@RegisterSubmodel(SERVICE_ENGINE_MASS_BWB, "fastoad.submodel.weight.mass.propulsion.engine.BWBtest.1")
class EngineWeight(om.ExplicitComponent):
    """
    Engine weight estimation

    Uses model described in :cite:`roux:2005`, p.74
    """

    def setup(self):
        self.add_input("data:propulsion:MTO_thrust", val=np.nan, units="N")
        self.add_input("data:geometry:propulsion:engine:count", val=np.nan)
        self.add_input("tuning:weight:propulsion:engine:mass:k", val=1.0)
        self.add_input("tuning:weight:propulsion:engine:mass:offset", val=0.0, units="kg")

        self.add_output("data:weight:propulsion:engine:mass", units="kg")

    def setup_partials(self):
        self.declare_partials("*", "*", method="fd")

    def compute(self, inputs, outputs, discrete_inputs=None, discrete_outputs=None):
        sea_level_thrust = inputs["data:propulsion:MTO_thrust"]
        n_engines = inputs["data:geometry:propulsion:engine:count"]
        k_b1 = inputs["tuning:weight:propulsion:engine:mass:k"]
        offset_b1 = inputs["tuning:weight:propulsion:engine:mass:offset"]

        if sea_level_thrust < 80000:
            temp_b1 = 22.2e-3 * sea_level_thrust
        else:
            temp_b1 = 14.1e-3 * sea_level_thrust + 648

        temp_b1 *= n_engines * 1.55
        outputs["data:weight:propulsion:engine:mass"] = k_b1 * temp_b1 + offset_b1
