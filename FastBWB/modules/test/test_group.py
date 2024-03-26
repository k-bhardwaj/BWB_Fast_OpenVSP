"""
This file contains one of the 4 aerodynamics groups. In this case the group is
named "aerodinamica.highspeed.2" and the main objective is the computation of
the "calculo_polar" component (last component called) that will compute the
drag polars, optimum L/D ratio, CL and CD values. In order to do so, all the
components that are called first are necessary as they contain outputs that 
will be used in "calculo_polar".
"""

import openmdao.api as om
from fastoad.module_management.constants import ModelDomain
from fastoad.module_management.service_registry import RegisterOpenMDAOSystem, RegisterSubmodel



@RegisterOpenMDAOSystem("test_new_group.2")
class TestClass(om.Group):
  

    def setup(self):
        self.add_subsystem(
            "name_component_test",
            RegisterSubmodel.get_submodel("component_test"),
            promotes=["*"],
        )
       
        
        
