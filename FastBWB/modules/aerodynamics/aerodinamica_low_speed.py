"""
This file contains one of the 4 aerodynamics groups. In this case the group is
named "aerodinamica.lowspeed.2" and the main objective is the computation of
the "calculo_polar" component (last component called) that will compute the
drag polars, optimum L/D ratio, CL and CD values. In order to do so, all the
components that are called first are necessary as they contain outputs that 
will be used in "calculo_polar". 
Notice that the low speed option is called just before "calculo_polar" by the
line: polar_type_option = {"polar_type": PolarType.LOW_SPEED}.
"""

import openmdao.api as om
from fastoad.module_management.constants import ModelDomain
from fastoad.module_management.service_registry import RegisterOpenMDAOSystem, RegisterSubmodel

from .constants import (
    PolarType,
    SERVICE_CD0,
    SERVICE_CD_TRIM,
    SERVICE_INDUCED_DRAG_COEFFICIENT,
    SERVICE_INITIALIZE_CL,
    #SERVICE_LOW_SPEED_CL_AOA,
    SERVICE_OSWALD_COEFFICIENT,
    SERVICE_POLAR,
    SERVICE_REYNOLDS_COEFFICIENT,
)

@RegisterOpenMDAOSystem("aerodinamica.lowspeed.2", domain=ModelDomain.AERODYNAMICS)
class AerodynamicsLowSpeed(om.Group):
    """
    Models for low speed aerodynamics
    """
    
    def setup(self):
        low_speed_option = {"low_speed_aero": True}


        self.add_subsystem(
            "calculo_low_speed_aerodynamics",
            RegisterSubmodel.get_submodel("calculo_low_speed_aero"),
            promotes=["*"],
        ) 
        ivc = om.IndepVarComp("data:aerodynamics:aircraft:takeoff:mach", val=0.2) 
        self.add_subsystem("mach_low_speed", ivc, promotes=["*"])

        self.add_subsystem(
            "calculo_coeficiente_oswald",
            RegisterSubmodel.get_submodel("calculo_oswald", low_speed_option),
            promotes=["*"],
        )
        
        self.add_subsystem(
            "compute_induced_drag_coeff",
            RegisterSubmodel.get_submodel("calculo_induced_drag_coefficient", low_speed_option),
            promotes=["*"],
        )
        
        self.add_subsystem(
            "comp_re",
            RegisterSubmodel.get_submodel("calculo_coeficiente_reynolds", low_speed_option),
            promotes=["*"],
        )

        self.add_subsystem(
            "initialize_cl",
            RegisterSubmodel.get_submodel("inicializar_cl", low_speed_option),
            promotes=["*"],
        )
        
        self.add_subsystem(
            "cd0_wing", RegisterSubmodel.get_submodel("cd0", low_speed_option), promotes=["*"]
        )
        
        self.add_subsystem(
            "cd_trim",
            RegisterSubmodel.get_submodel("calculo_cd_equilibrio", low_speed_option),
            promotes=["*"],
        )
        
        polar_type_option = {"polar_type": PolarType.LOW_SPEED}
        self.add_subsystem(
            "get_polar",
            RegisterSubmodel.get_submodel("calculo_polar", polar_type_option),
            promotes=["*"],
        )
        
