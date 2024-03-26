"""
    Estimation of center of gravity for load case 2
"""

from fastoad.module_management.service_registry import RegisterSubmodel

from .compute_cg_loadcase_base import ComputeCGLoadCase
from .compute_cg_loadcases import SERVICE_LOAD_CASE_CG_PREFIX

CASE_NUMBER = 2


@RegisterSubmodel(
    f"{SERVICE_LOAD_CASE_CG_PREFIX}.{CASE_NUMBER}",
    f"fastoad.submodel.weight.cg.load_cases.BWBtest.{CASE_NUMBER}",
)
class ComputeCGLoadCase2(ComputeCGLoadCase):
    """Center of gravity estimation for load case 3"""

    def setup(self):
        self.options["case_number"] = CASE_NUMBER
        self.options["mass_per_pax"] = 90.0
        self.options["mass_front_fret_per_pax"] = 20.0
        self.options["mass_rear_fret_per_pax"] = 20.0
        self.options["fuel_mass_variable"] = "data:weight:aircraft:MFW"
        return super().setup()
