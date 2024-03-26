
import numpy as np
from fastoad.module_management.service_registry import RegisterSubmodel
from openmdao.core.explicitcomponent import ExplicitComponent

@RegisterSubmodel("component_test", "component_test.2")
class ComponentClass(ExplicitComponent):
    """Computation of max CL in landing conditions."""

    def setup(self):
        self.add_input("data:New_Input:input_new", val=np.nan, units="m") 
        self.add_output("data:outputs_test:output") 

    def setup_partials(self):
        self.declare_partials("*", "*", method="fd")

    def compute(self, inputs, outputs):
        whatever_I_want = inputs["data:New_Input:input_new"]
        
        output_I_want = whatever_I_want * 2

        outputs["data:outputs_test:output"] = output_I_want