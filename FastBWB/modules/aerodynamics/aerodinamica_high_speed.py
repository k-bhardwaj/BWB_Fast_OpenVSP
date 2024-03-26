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

from .constants import (
    SERVICE_CD0,
    SERVICE_CD_COMPRESSIBILITY,
    SERVICE_CD_TRIM,
    SERVICE_INDUCED_DRAG_COEFFICIENT,
    SERVICE_INITIALIZE_CL,
    SERVICE_OSWALD_COEFFICIENT,
    SERVICE_POLAR,
    SERVICE_REYNOLDS_COEFFICIENT,
)

@RegisterOpenMDAOSystem("aerodinamica.highspeed.2", domain=ModelDomain.AERODYNAMICS)
class AerodynamicsHighSpeed(om.Group):
    """
    Computes aerodynamic polar of the aircraft in cruise conditions.

    Drag contributions of each part of the aircraft are computed though analytical
    models.
    """

    def setup(self):
        self.add_subsystem(
            "calculo_coeficiente_oswald",
            RegisterSubmodel.get_submodel("calculo_oswald"),
            promotes=["*"],
        )
       
        self.add_subsystem(
            "compute_induced_drag_coeff",
            RegisterSubmodel.get_submodel("calculo_induced_drag_coefficient"),
            promotes=["*"],
        )
        self.add_subsystem(
            "comp_re", RegisterSubmodel.get_submodel("calculo_coeficiente_reynolds"), promotes=["*"]
        )
        self.add_subsystem(
            "initialize_cl", RegisterSubmodel.get_submodel("inicializar_cl"), promotes=["*"]
        )
        self.add_subsystem("cd0_wing", RegisterSubmodel.get_submodel("cd0"), promotes=["*"])
        
        self.add_subsystem(
            "cd_comp", RegisterSubmodel.get_submodel("cd_compressibility"), promotes=["*"]
        )
        self.add_subsystem(
            "cd_trim", RegisterSubmodel.get_submodel("calculo_cd_equilibrio"), promotes=["*"]
        )
        self.add_subsystem(
            "get_polar", RegisterSubmodel.get_submodel("calculo_polar"), promotes=["*"]
        )
        
