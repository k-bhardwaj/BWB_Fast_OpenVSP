"""
    Estimation of center of gravity for load case 4
"""

from fastoad.module_management.service_registry import RegisterSubmodel

from .compute_cg_loadcase_base import ComputeCGLoadCase
from .compute_cg_loadcases import SERVICE_LOAD_CASE_CG_PREFIX

CASE_NUMBER = 4


@RegisterSubmodel(
    f"{SERVICE_LOAD_CASE_CG_PREFIX}.{CASE_NUMBER}",
    f"fastoad.submodel.weight.cg.load_cases.BWBtest.{CASE_NUMBER}",
)
class ComputeCGLoadCase4(ComputeCGLoadCase):
    """Center of gravity estimation for load case"""

    def setup(self):
        self.options["case_number"] = CASE_NUMBER
        self.options["mass_per_pax"] = 90.0
        self.options["mass_front_fret_per_pax"] = 10.0
        self.options["mass_rear_fret_per_pax"] = 30.0
        return super().setup()
