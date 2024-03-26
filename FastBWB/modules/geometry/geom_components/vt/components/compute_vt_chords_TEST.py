import math
import numpy as np
import openmdao.api as om


"""
    Estimation of vertical tail chords and span
"""

class ComputeVTChords(om.ExplicitComponent):
    # TODO: Document equations. Cite sources
    """Vertical tail chords and span estimation
    Inputs: VT aspect ratio, VT area, VT taper ratio, VT sweep 25
    Outputs: VT span, VT root chord, VT tip chord."""

    def setup(self):
        self.add_input("data:geometry:vertical_tail:aspect_ratio", val=np.nan)
        self.add_input("data:geometry:vertical_tail:area", val=np.nan, units="m**2")
        self.add_input("data:geometry:vertical_tail:taper_ratio", val=np.nan)
        self.add_input("data:geometry:vertical_tail:sweep_25", val=np.nan, units="deg")

        self.add_output("data:geometry:vertical_tail:span", units="m")
        self.add_output("data:geometry:vertical_tail:root:chord", units="m")
        self.add_output("data:geometry:vertical_tail:tip:chord", units="m")

    def setup_partials(self):
        self.declare_partials(
            "data:geometry:vertical_tail:span",
            ["data:geometry:vertical_tail:aspect_ratio", "data:geometry:vertical_tail:area"],
            method="fd",
        )
        self.declare_partials("data:geometry:vertical_tail:root:chord", "*", method="fd")
        self.declare_partials("data:geometry:vertical_tail:tip:chord", "*", method="fd")

    def compute(self, inputs, outputs):
        s_v = inputs["data:geometry:vertical_tail:area"]
        taper_v = inputs["data:geometry:vertical_tail:taper_ratio"]
        # BWB:
        sweep_25_vt = inputs["data:geometry:vertical_tail:sweep_25"] + 10. # VT Sweep @25% chord.
        lambda_vt = 2.6 * math.cos(sweep_25_vt / 180. * math.pi)**2 # Vertical tail taper ratio.
    
        b_v = math.sqrt(lambda_vt * s_v) # vertical tail span.
        root_chord = s_v * 2 / (1 + taper_v) / b_v # VT Root chord.
        tip_chord = root_chord * taper_v # VT tip chord.

        outputs["data:geometry:vertical_tail:span"] = b_v
        outputs["data:geometry:vertical_tail:root:chord"] = root_chord
        outputs["data:geometry:vertical_tail:tip:chord"] = tip_chord
        
        
        
