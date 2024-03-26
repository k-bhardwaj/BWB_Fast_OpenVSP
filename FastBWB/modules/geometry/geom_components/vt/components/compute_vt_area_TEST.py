import math
import numpy as np
import openmdao.api as om


"""
    Estimation of vertical tail chords and span
"""

class ComputeVTArea(om.ExplicitComponent):
    # TODO: Document equations. Cite sources
    """Vertical tail area estimation"""

    def setup(self):
        self.add_input("data:geometry:wing:sweep_25", val=np.nan, units="deg")
        self.add_input("data:geometry:wing:sweep_0", val=np.nan, units="deg")
        self.add_input("data:geometry:fuselage:maximum_width", val=np.nan, units="m")
        self.add_input("data:TLAR:approach_speed", val=np.nan, units="m/s")
        self.add_input("data:geometry:propulsion:engine:y_ratio", val=np.nan)
        self.add_input("data:propulsion:MTO_thrust", val=np.nan, units="N")
        self.add_input("data:geometry:vertical_tail:n_vt", val=np.nan)
        self.add_input("data:geometry:wing:span", val=np.nan, units="m")

        self.add_output("data:geometry:vertical_tail:area", units="m**2")
        self.add_output("data:geometry:vertical_tail:MAC:at25percent:x:from_wingMAC25", units="m")

    def setup_partials(self):
        self.declare_partials(of="*", wrt="*", method="fd")

    def compute(self, inputs, outputs):
        sweep_25 = inputs["data:geometry:wing:sweep_25"]
        sweep_0 = inputs["data:geometry:wing:sweep_0"]
        fus_max_width = inputs["data:geometry:fuselage:maximum_width"]
        approach_speed = inputs["data:TLAR:approach_speed"]
        thrust_sl = inputs["data:propulsion:MTO_thrust"]
        n_vt = inputs["data:geometry:vertical_tail:n_vt"]
        y_ratio = inputs["data:geometry:propulsion:engine:y_ratio"]
        span = inputs["data:geometry:wing:span"]
        
        sweep_25_vt = sweep_25 + 10 # 10 degrees more than the wing's sweep @25% chord.
        lambda_vt = 2.6 * math.cos(sweep_25_vt / 180. * math.pi)**2 # Taper ratio.
        lp_vt = (span - fus_max_width) / 2. * math.tan(sweep_0*math.pi/180.) # Moment arm from vertical tail to wing.
        vmc_kts = approach_speed / 0.5144 # VMC speed (the speed below which aircraft control cannot be maintained if the critical engine fails under a specific set of circumstances) in knots.
        vmc = (1.3 * vmc_kts - 15)*0.5144 
        mach = vmc / 340 # Mach number
        yengine = y_ratio * span / 2. # Spanwise position of engines.
        delta_rudder = 25. * math.pi / 180. # Rudder deflection in radians.
        cy_beta = 2 * math.pi * lambda_vt / (2 + math.sqrt(4 + (1 + (math.tan(sweep_25_vt * math.pi / 180.))**2 - \
                                                                mach**2)*lambda_vt**2))
        cy_dr = cy_beta / 1.7
        s_v = 4 * thrust_sl * yengine / 1.225 / vmc**2 / lp_vt / cy_dr / delta_rudder # Total Vertical Tail surface.
        s_v = s_v / n_vt # Vertical tail area per tail (BWB has 2 V type vertical tails.)
        
        outputs["data:geometry:vertical_tail:area"] = s_v
        outputs["data:geometry:vertical_tail:MAC:at25percent:x:from_wingMAC25"] = lp_vt








