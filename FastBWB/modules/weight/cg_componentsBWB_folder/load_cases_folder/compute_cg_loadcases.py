"""
1. Computes and aggregates CG ratios for load cases.
---------------------------------------------
2. Computes maximum center of gravity ratio from load cases.

"""
from itertools import count

import numpy as np
from fastoad.module_management.exceptions import FastNoSubmodelFoundError
from fastoad.module_management.service_registry import RegisterSubmodel
from openmdao import api as om

from ...constantscg import SERVICE_LOAD_CASES_CG

SERVICE_LOAD_CASE_CG_PREFIX = "service.cg.load_cases.BWBtest"


@RegisterSubmodel(SERVICE_LOAD_CASES_CG, "fastoad.submodel.weight.cg.load_cases.BWBtest.1.1")
class CGRatiosForLoadCases(om.Group):
    """Aggregation of CG ratios from load case calculations."""

    def setup(self):

        # We add in our group all the components for declared services that provide CG ratio
        # for specific load_cases
        for load_case_count in count():
            try:
                system = RegisterSubmodel.get_submodel(
                    f"{SERVICE_LOAD_CASE_CG_PREFIX}.{load_case_count + 1}"
                )
            except FastNoSubmodelFoundError:
                break
            self.add_subsystem(f"cg_ratio_lc{load_case_count + 1}", system, promotes_inputs=["*"])

        cg_ratio_aggregator = self.add_subsystem(
            "cg_ratio_aggregator",
            om.MuxComp(vec_size=load_case_count),
            promotes=["data:weight:aircraft:load_cases:CG:MAC_position"],
        )

        # This part aggregates all CG ratios values in one vector variable.
        cg_ratio_aggregator.add_var(
            "data:weight:aircraft:load_cases:CG:MAC_position", shape=(1,), axis=0
        )
        for i in range(load_case_count):
            self.connect(
                f"cg_ratio_lc{i + 1}.data:weight:aircraft:load_case_{i + 1}:CG:MAC_position",
                f"cg_ratio_aggregator.data:weight:aircraft:load_cases:CG:MAC_position_{i}",
            )

        self.add_subsystem("compute_max", MaxCGRatiosForLoadCases(), promotes=["*"])


class MaxCGRatiosForLoadCases(om.ExplicitComponent):
    """Maximum center of gravity ratio from load cases."""

    def setup(self):
        self.add_input(
            "data:weight:aircraft:load_cases:CG:MAC_position", val=np.nan, shape_by_conn=True
        )

        self.add_output("data:weight:aircraft:load_cases:CG:MAC_position:maximum")

    def setup_partials(self):
        self.declare_partials("*", "*", method="fd")

    def compute(self, inputs, outputs, discrete_inputs=None, discrete_outputs=None):
        outputs["data:weight:aircraft:load_cases:CG:MAC_position:maximum"] = (
            np.nanmax(inputs["data:weight:aircraft:load_cases:CG:MAC_position"]),
        )
