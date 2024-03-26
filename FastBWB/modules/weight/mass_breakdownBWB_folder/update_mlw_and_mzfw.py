"""
MLW and MZFW computation
-----------------------------------------------------------
This file is in charge of computing the maximum landing weight and
the max zero fuel weight from the OWE and the PL_max. 
"""

import numpy as np
from openmdao.core.explicitcomponent import ExplicitComponent


class UpdateMLWandMZFW(ExplicitComponent):
    """
    Computes Maximum Landing Weight and Maximum Zero Fuel Weight from
    Overall Empty Weight and Maximum Payload.
    """

    def setup(self):
        self.add_input("data:weight:aircraft:OWE", val=np.nan, units="kg")
        self.add_input("data:weight:aircraft:max_payload", val=np.nan, units="kg")

        self.add_output("data:weight:aircraft:MZFW", units="kg")
        self.add_output("data:weight:aircraft:MLW", units="kg")

    def setup_partials(self):
        self.declare_partials("*", "*", method="fd")

    def compute(self, inputs, outputs, discrete_inputs=None, discrete_outputs=None):
        owe = inputs["data:weight:aircraft:OWE"][0]
        max_pl = inputs["data:weight:aircraft:max_payload"][0]
        mzfw = owe + max_pl
        mlw = 1.06 * mzfw

        outputs["data:weight:aircraft:MZFW"] = mzfw
        outputs["data:weight:aircraft:MLW"] = mlw
