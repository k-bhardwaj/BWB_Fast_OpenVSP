"""
This file contains one group, not a component. The group is named "cd0". It
calls every component responsible for computing the form drag of one
part of the airplane, including "cd0_total" which will sum all the 
contributions from the previous components. The components are executed by the
order they appear.
"""

import openmdao.api as om
from fastoad.module_management.service_registry import RegisterSubmodel


@RegisterSubmodel("cd0", "cd0.2")
class CD0(om.Group):
    """
    Computation of form drag for whole aircraft.

    Computes and sums the drag coefficients of all components.
    Interaction drag is assumed to be taken into account at component level.
    """

    def initialize(self):
        self.options.declare("low_speed_aero", default=False, types=bool)

    def setup(self):
        low_speed_option = {"low_speed_aero": self.options["low_speed_aero"]}
        self.add_subsystem(
            "cd0_wing",
            RegisterSubmodel.get_submodel("calculo_cd0_asa", low_speed_option),
            promotes=["*"],
        )
        self.add_subsystem(
            "cd0_fuselage",
            RegisterSubmodel.get_submodel("calculo_form_drag_fuselagem", low_speed_option),
            promotes=["*"],
        )
        self.add_subsystem(
            "cd0_ht",
            RegisterSubmodel.get_submodel("calculo_cd0_horizontal_tail", low_speed_option),
            promotes=["*"],
        )
        self.add_subsystem(
            "cd0_vt",
            RegisterSubmodel.get_submodel("calculo_cd0_vertical_tail", low_speed_option),
            promotes=["*"],
        )
        self.add_subsystem(
            "cd0_nac_pylons",
            RegisterSubmodel.get_submodel("calculo_cd0_nacelles_pylons", low_speed_option),
            promotes=["*"],
        )
        self.add_subsystem(
            "cd0_total",
            RegisterSubmodel.get_submodel("soma_cd0", low_speed_option),
            promotes=["*"],
        )