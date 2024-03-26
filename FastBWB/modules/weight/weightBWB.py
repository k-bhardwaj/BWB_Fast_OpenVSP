"""
Weight group computation (mass + CG)
----------------------------------------------
This file is the main group class and it is in charge of 
calling the mass_breakdown and the CG subgroups. The group 
is named "fastoad.weight.BWBtest.1". 

"""


import openmdao.api as om
import os
from fastoad.module_management.constants import ModelDomain
from fastoad.module_management.service_registry import RegisterOpenMDAOSystem, RegisterSubmodel

# Print the current working directory
# print("Current working directory: {0}".format(os.getcwd()))

# Change the current working directory to avoid errors
# os.chdir(r'C:\Users\Sandra\Documents\2. SUPAERO\MAE\3. RP\HWP5\4. FAST-OAD\BWB conversion\WeightCgAll\modules')


from .constants import SERVICE_CENTERS_OF_GRAVITY, SERVICE_MASS_BREAKDOWN
from .constants2 import PAYLOAD_FROM_NPAX

@RegisterOpenMDAOSystem("fastoad.weight.BWBtest.1", domain=ModelDomain.WEIGHT)
class Weight(om.Group):
    """
    Computes masses and Centers of Gravity for each part of the empty operating aircraft, among
    these 5 categories:
    airframe, propulsion, systems, furniture, crew

    This model uses MTOW as an input, as it allows to size some elements, but resulting OWE do
    not aim at being consistent with MTOW.

    Consistency between OWE and MTOW can be achieved by cycling with a model that computes MTOW
    from OWE, which should come from a mission computation that will assess needed block fuel.
    """

    def initialize(self):
        self.options.declare(
            PAYLOAD_FROM_NPAX,
            types=bool,
            default=True,
            desc="If True (default), payload masses will be computed from NPAX.\n"
            "If False, design payload mass and maximum payload mass must be provided.",
        )

    def setup(self):
        self.add_subsystem(
            "cg", RegisterSubmodel.get_submodel(SERVICE_CENTERS_OF_GRAVITY), promotes=["*"]
        )
        self.add_subsystem(
            "mass_breakdown",
            RegisterSubmodel.get_submodel(
                SERVICE_MASS_BREAKDOWN, {PAYLOAD_FROM_NPAX: self.options[PAYLOAD_FROM_NPAX]}
            ),
            promotes=["*"],
        )
