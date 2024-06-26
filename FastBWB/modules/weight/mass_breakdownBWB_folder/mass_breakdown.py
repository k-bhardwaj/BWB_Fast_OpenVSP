"""
Addition of all mass_breakdown components and OWE computation
-----------------------------------------------------------
This file is in charge of computing analytically the mass 
of each part of the aircraft, and the resulting sum, the 
Overall Weight Empty (OWE).
Two submodels are created: 
1. MassBreakdown
	- It is registered under the name "fastoad.submodel.weight.mass.BWBtest.1". 
2. OperatingWeightEmpty
	- It is registered under the name "fastoad.submodel.weight.mass.owe.BWBtest.1"
It estimates the OWE by aggregating all the masses from all components of the aircraft.
(propulsion, systems, airframe, furniture and crew). 

"""

import openmdao.api as om
from fastoad.module_management.service_registry import RegisterSubmodel

from .constants import (
    SERVICE_AIRFRAME_MASS,
    SERVICE_CREW_MASS,
    SERVICE_FURNITURE_MASS,
    SERVICE_OWE,
    SERVICE_PAYLOAD_MASS,
    SERVICE_PROPULSION_MASS,
    SERVICE_SYSTEMS_MASS,
)
from .update_mlw_and_mzfw import UpdateMLWandMZFW
from ..constants import SERVICE_MASS_BREAKDOWN
from ..constants2 import PAYLOAD_FROM_NPAX


@RegisterSubmodel(SERVICE_MASS_BREAKDOWN, "fastoad.submodel.weight.mass.BWBtest.1")
class MassBreakdown(om.Group):
    """
    Computes analytically the mass of each part of the aircraft, and the resulting sum,
    the Overall Weight Empty (OWE).

    Some models depend on MZFW (Max Zero Fuel Weight), MLW (Max Landing Weight) and
    MTOW (Max TakeOff Weight), which depend on OWE.

    This model cycles for having consistent OWE, MZFW and MLW.

    Options:
    - payload_from_npax: If True (default), payload masses will be computed from NPAX, if False
                         design payload mass and maximum payload mass must be provided.
    """

    def initialize(self):
        self.options.declare(PAYLOAD_FROM_NPAX, types=bool, default=True)

    def setup(self):
        if self.options[PAYLOAD_FROM_NPAX]:
            self.add_subsystem(
                "payload", RegisterSubmodel.get_submodel(SERVICE_PAYLOAD_MASS), promotes=["*"]
            )
        self.add_subsystem("owe", RegisterSubmodel.get_submodel(SERVICE_OWE), promotes=["*"])
        self.add_subsystem("update_mzfw_and_mlw", UpdateMLWandMZFW(), promotes=["*"])

        # Solvers setup
        self.nonlinear_solver = om.NonlinearBlockGS()
        self.nonlinear_solver.options["iprint"] = 0
        self.nonlinear_solver.options["maxiter"] = 50

        self.linear_solver = om.LinearBlockGS()
        self.linear_solver.options["iprint"] = 0


@RegisterSubmodel(SERVICE_OWE, "fastoad.submodel.weight.mass.owe.BWBtest.1")
class OperatingWeightEmpty(om.Group):
    """Operating Empty Weight (OEW) estimation.

    This group aggregates weight from all components of the aircraft.
    """

    def setup(self):
        # Propulsion should be done before airframe, because it drives pylon mass.
        self.add_subsystem(
            "propulsion_weight",
            RegisterSubmodel.get_submodel(SERVICE_PROPULSION_MASS),
            promotes=["*"],
        )
        self.add_subsystem(
            "airframe_weight", RegisterSubmodel.get_submodel(SERVICE_AIRFRAME_MASS), promotes=["*"]
        )
        self.add_subsystem(
            "systems_weight", RegisterSubmodel.get_submodel(SERVICE_SYSTEMS_MASS), promotes=["*"]
        )
        self.add_subsystem(
            "furniture_weight",
            RegisterSubmodel.get_submodel(SERVICE_FURNITURE_MASS),
            promotes=["*"],
        )
        self.add_subsystem(
            "crew_weight", RegisterSubmodel.get_submodel(SERVICE_CREW_MASS), promotes=["*"]
        )

        weight_sum = om.AddSubtractComp()
        weight_sum.add_equation(
            "data:weight:aircraft:OWE",
            [
                "data:weight:airframe:mass",
                "data:weight:propulsion:mass",
                "data:weight:systems:mass",
                "data:weight:furniture:mass",
                "data:weight:crew:mass",
            ],
            units="kg",
            desc="Mass of crew",
        )

        self.add_subsystem("OWE_sum", weight_sum, promotes=["*"])
