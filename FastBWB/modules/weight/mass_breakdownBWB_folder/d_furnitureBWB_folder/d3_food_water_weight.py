"""
Estimation of food water weight - D3 component
---------------------------------------------
- Registered under the name "service.mass.furniture.food_water.BWBtest.1"

 """

import numpy as np
import openmdao.api as om
from fastoad.module_management.service_registry import RegisterSubmodel

from .constants import SERVICE_FOOD_WATER_MASS


@RegisterSubmodel(SERVICE_FOOD_WATER_MASS, "service.mass.furniture.food_water.BWBtest.1")
class FoodWaterWeight(om.ExplicitComponent):
    """
    Weight estimation for food and water

    Includes trolleys, trays, cutlery...

    Based on :cite:`supaero:2014`, mass contribution D3
    """

    def setup(self):
        self.add_input("data:TLAR:NPAX", val=np.nan)
        self.add_input("tuning:weight:furniture:food_water:mass:k", val=1.0)
        self.add_input("tuning:weight:furniture:food_water:mass:offset", val=0.0, units="kg")

        self.add_output("data:weight:furniture:food_water:mass", units="kg")

    def setup_partials(self):
        self.declare_partials("*", "*", method="fd")

    def compute(self, inputs, outputs, discrete_inputs=None, discrete_outputs=None):
        npax = inputs["data:TLAR:NPAX"]
        k_d3 = inputs["tuning:weight:furniture:food_water:mass:k"]
        offset_d3 = inputs["tuning:weight:furniture:food_water:mass:offset"]

        temp_d3 = 8.75 * npax
        outputs["data:weight:furniture:food_water:mass"] = k_d3 * temp_d3 + offset_d3
