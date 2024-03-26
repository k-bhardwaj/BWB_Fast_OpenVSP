"""
Estimation of global center of gravity
------------------------------------------

"""

import openmdao.api as om
from fastoad.module_management.service_registry import RegisterSubmodel

from .compute_max_cg_ratio import ComputeMaxCGratio
from ..constantscg import SERVICE_EMPTY_AIRCRAFT_CG, SERVICE_GLOBAL_CG, SERVICE_LOAD_CASES_CG


@RegisterSubmodel(SERVICE_GLOBAL_CG, "fastoad.submodel.weight.cg.global.BWBtest.1")
class ComputeGlobalCG(om.Group):
    # TODO: Document equations. Cite sources
    """Global center of gravity estimation"""

    def setup(self):
        self.add_subsystem(
            "cg_ratio_empty",
            RegisterSubmodel.get_submodel(SERVICE_EMPTY_AIRCRAFT_CG),
            promotes=["*"],
        )
        self.add_subsystem(
            "cg_ratio_load_cases",
            RegisterSubmodel.get_submodel(SERVICE_LOAD_CASES_CG),
            promotes=["*"],
        )
        self.add_subsystem("cg_ratio_max", ComputeMaxCGratio(), promotes=["*"])
