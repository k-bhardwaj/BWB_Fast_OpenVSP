"""
This file contains one of the 4 aerodynamics groups. In this case the group is
named "aerodynamics.takeoff.2" and the main objective is the computation of
the "calculo_polar" component (last component called) that will compute the
drag polars, optimum L/D ratio, CL and CD values. In order to do so, all the
components that are called first are necessary as they contain outputs that 
will be used in "calculo_polar". 
Notice that the takeoff option is called just before "calculo_polar" by the
line: polar_type_option = {"polar_type": PolarType.TAKEOFF}.
"""

import openmdao.api as om
from fastoad.module_management.constants import ModelDomain # Not sure what this does
from fastoad.module_management.service_registry import RegisterOpenMDAOSystem, RegisterSubmodel


from .constants import PolarType, SERVICE_HIGH_LIFT, SERVICE_POLAR


@RegisterOpenMDAOSystem("aerodynamics.takeoff.2", domain=ModelDomain.AERODYNAMICS)
class AerodynamicsTakeoff(om.Group):

    def setup(self):
        landing_flag_option = {"landing_flag": False}
        self.add_subsystem(
            "delta_cl_cd",
            RegisterSubmodel.get_submodel("calculo_high_lift", landing_flag_option), 
            promotes=["*"],
        ) 

        polar_type_option = {"polar_type": PolarType.TAKEOFF}
        self.add_subsystem(
            "polar", RegisterSubmodel.get_submodel("calculo_polar", polar_type_option), promotes=["*"]
        ) 