"""
Computation of propulsion mass- Sum of all B components
---------------------------------------------
- Registered under the name "fastoad.submodel.weight.mass.propulsion.BWBtest.1"
propulsion_mass = engines_mass + fuellines_mass + unconsumables_mass
B = B1 + B2 + B3

"""

from fastoad.module_management.service_registry import RegisterSubmodel
from openmdao import api as om

from .constants import SERVICE_ENGINE_MASS_BWB, SERVICE_FUEL_LINES_MASS_BWB, SERVICE_UNCONSUMABLES_MASS_BWB
from ..constants import SERVICE_PROPULSION_MASS


@RegisterSubmodel(SERVICE_PROPULSION_MASS, "fastoad.submodel.weight.mass.propulsion.BWBtest.1")
class PropulsionWeight(om.Group):
    """
    Computes mass of propulsion.
    """

    def setup(self):
        # Engine have to be computed before pylons
        self.add_subsystem(
            "engines_weight", RegisterSubmodel.get_submodel(SERVICE_ENGINE_MASS_BWB), promotes=["*"]
        )
        self.add_subsystem(
            "fuel_lines_weight",
            RegisterSubmodel.get_submodel(SERVICE_FUEL_LINES_MASS_BWB),
            promotes=["*"],
        )
        self.add_subsystem(
            "unconsumables_weight",
            RegisterSubmodel.get_submodel(SERVICE_UNCONSUMABLES_MASS_BWB),
            promotes=["*"],
        )

        weight_sum = om.AddSubtractComp()
        weight_sum.add_equation(
            "data:weight:propulsion:mass",
            [
                "data:weight:propulsion:engine:mass",
                "data:weight:propulsion:fuel_lines:mass",
                "data:weight:propulsion:unconsumables:mass",
            ],
            units="kg",
            desc="Mass of the propulsion system",
        )

        self.add_subsystem("propulsion_weight_sum", weight_sum, promotes=["*"])
