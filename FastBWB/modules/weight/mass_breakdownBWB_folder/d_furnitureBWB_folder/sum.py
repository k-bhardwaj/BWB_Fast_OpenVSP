"""
Estimation of total furniture components weight - Sum of all D components
---------------------------------------------
furniture_mass = paxSeats_mass + foodwater_mass + securityKit_mass + toilets
D  = D1 + D2 + D3 + D4 + D5
 """

from fastoad.module_management.service_registry import RegisterSubmodel
from openmdao import api as om

from .constants import (
    SERVICE_FOOD_WATER_MASS,
    SERVICE_PASSENGER_SEATS_MASS,
    SERVICE_SECURITY_KIT_MASS,
    SERVICE_TOILETS_MASS,
)
from ..constants import SERVICE_FURNITURE_MASS


@RegisterSubmodel(
    SERVICE_FURNITURE_MASS, "fastoad.submodel.weight.mass.furniture.cargo_configuration.BWBtest.1"
)
class FurnitureWeight(om.Group):
    """
    Computes mass of furniture.
    """

    def setup(self):
        self.add_subsystem(
            "passenger_seats_weight",
            RegisterSubmodel.get_submodel(SERVICE_PASSENGER_SEATS_MASS),
            promotes=["*"],
        )
        self.add_subsystem(
            "food_water_weight",
            RegisterSubmodel.get_submodel(SERVICE_FOOD_WATER_MASS),
            promotes=["*"],
        )
        self.add_subsystem(
            "security_kit_weight",
            RegisterSubmodel.get_submodel(SERVICE_SECURITY_KIT_MASS, ""),
            promotes=["*"],
        )
        self.add_subsystem(
            "toilets_weight", RegisterSubmodel.get_submodel(SERVICE_TOILETS_MASS), promotes=["*"]
        )

        weight_sum = om.AddSubtractComp()
        weight_sum.add_equation(
            "data:weight:furniture:mass",
            [
                "data:weight:furniture:passenger_seats:mass",
                "data:weight:furniture:food_water:mass",
                "data:weight:furniture:security_kit:mass",
                "data:weight:furniture:toilets:mass",
            ],
            units="kg",
            desc="Mass of aircraft furniture",
        )

        self.add_subsystem("furniture_weight_sum", weight_sum, promotes=["*"])
