"""
Computation of total system components mass - All C components
---------------------------------------------
- Registered under the name "fastoad.submodel.weight.mass.systems.BWBtest.1"
C = C11 + C12 + C13 + C21 + C22 + C23 + C24 + C25 + C26 + C27 + C3 + C4 + C51 + C52 + C6

 """

from fastoad.module_management.service_registry import RegisterSubmodel
from openmdao import api as om

from .constants import (
    SERVICE_FIXED_OPERATIONAL_SYSTEMS_MASS,
    SERVICE_FLIGHT_KIT_MASS,
    SERVICE_LIFE_SUPPORT_SYSTEMS_MASS,
    SERVICE_NAVIGATION_SYSTEMS_MASS,
    SERVICE_POWER_SYSTEMS_MASS,
    SERVICE_TRANSMISSION_SYSTEMS_MASS,
)
from ..constants import SERVICE_SYSTEMS_MASS


@RegisterSubmodel(SERVICE_SYSTEMS_MASS, "fastoad.submodel.weight.mass.systems.BWBtest.1")
class SystemsWeight(om.Group):
    """
    Computes mass of systems.
    """

    def setup(self):
        self.add_subsystem(
            "power_systems_weight",
            RegisterSubmodel.get_submodel(SERVICE_POWER_SYSTEMS_MASS),
            promotes=["*"],
        )
        self.add_subsystem(
            "life_support_systems_weight",
            RegisterSubmodel.get_submodel(SERVICE_LIFE_SUPPORT_SYSTEMS_MASS),
            promotes=["*"],
        )
        self.add_subsystem(
            "navigation_systems_weight",
            RegisterSubmodel.get_submodel(SERVICE_NAVIGATION_SYSTEMS_MASS),
            promotes=["*"],
        )
        self.add_subsystem(
            "transmission_systems_weight",
            RegisterSubmodel.get_submodel(SERVICE_TRANSMISSION_SYSTEMS_MASS),
            promotes=["*"],
        )
        self.add_subsystem(
            "fixed_operational_systems_weight",
            RegisterSubmodel.get_submodel(SERVICE_FIXED_OPERATIONAL_SYSTEMS_MASS),
            promotes=["*"],
        )
        self.add_subsystem(
            "flight_kit_weight",
            RegisterSubmodel.get_submodel(SERVICE_FLIGHT_KIT_MASS),
            promotes=["*"],
        )

        weight_sum = om.AddSubtractComp()
        weight_sum.add_equation(
            "data:weight:systems:mass",
            [
                "data:weight:systems:power:auxiliary_power_unit:mass",
                "data:weight:systems:power:electric_systems:mass",
                "data:weight:systems:power:hydraulic_systems:mass",
                "data:weight:systems:life_support:insulation:mass",
                "data:weight:systems:life_support:air_conditioning:mass",
                "data:weight:systems:life_support:de-icing:mass",
                "data:weight:systems:life_support:cabin_lighting:mass",
                "data:weight:systems:life_support:seats_crew_accommodation:mass",
                "data:weight:systems:life_support:oxygen:mass",
                "data:weight:systems:life_support:safety_equipment:mass",
                "data:weight:systems:navigation:mass",
                "data:weight:systems:transmission:mass",
                "data:weight:systems:operational:radar:mass",
                "data:weight:systems:operational:cargo_hold:mass",
                "data:weight:systems:flight_kit:mass",
            ],
            units="kg",
            desc="Mass of aircraft systems",
        )

        self.add_subsystem("systems_weight_sum", weight_sum, promotes=["*"])
