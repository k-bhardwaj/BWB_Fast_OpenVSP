"""
    Estimation of yawing moment due to sideslip
"""

#  This file is part of FAST-OAD_CS25
#  Copyright (C) 2022 ONERA & ISAE-SUPAERO
#  FAST is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <https://www.gnu.org/licenses/>.
import math

import fastoad.api as oad
import numpy as np
import openmdao.api as om
import os


# TODO: This belongs more to aerodynamics than geometry
@oad.RegisterSubmodel("fuselage.cnbeta.bwb", "fastoad.submodel.geometry.fuselage.cnbeta.bwb")
class ComputeCnBetaFuselage(om.ExplicitComponent):
    """Yawing moment due to sideslip estimation"""

    def setup(self):
        self.add_input("data:geometry:fuselage:length", val=np.nan, units="m")
        self.add_input("data:geometry:fuselage:maximum_width", val=np.nan, units="m")
        self.add_input("data:geometry:fuselage:maximum_height", val=np.nan, units="m")
        self.add_input("data:geometry:wing:root:chord", val=np.nan, units="m")
        self.add_input("data:geometry:wing:area", val=np.nan, units="m**2")
        self.add_input("data:geometry:wing:span", val=np.nan, units="m")

        self.add_output("data:aerodynamics:fuselage:cruise:CnBeta")

    def setup_partials(self):
        self.declare_partials("data:aerodynamics:fuselage:cruise:CnBeta", "*", method="fd")

    def compute(self, inputs, outputs):
        fus_length = inputs["data:geometry:fuselage:length"]
        rootchord = inputs["data:geometry:wing:root:chord"]
        width_max = inputs["data:geometry:fuselage:maximum_width"]
        height_max = inputs["data:geometry:fuselage:maximum_height"]
        wing_area = inputs["data:geometry:wing:area"]
        span = inputs["data:geometry:wing:span"]

        l_f = math.sqrt(width_max * height_max) ## Equivalent diameter of cabin. 

        # Estimation of fuselage volume
        full_path = os.path.realpath(__file__)
        full_path_dir = os.path.dirname(full_path)
        airf = full_path_dir + r'\airfoils\mh78.dat'
        with open(airf, 'r') as f:
            data = f.readlines()[1:]

        # Extract x and y coordinates from data
        x = []
        y = []
        for line in data:
            if not line.startswith('#'):
                row = line.split()
                x.append(float(row[0]))
                y.append(float(row[1]))

        # Define wing dimensions
        c_root = fus_length# root chord
        c_tip = rootchord# tip chord
        taper = c_tip / c_root # taper ratio
        theta = 45*np.pi/180 # sweep angle
        lambda_ = c_tip / c_root # wing sweep ratio

        # Define wing sections
        y_sections = np.linspace(-span/2, span/2, 100) # spanwise location of sections
        c_sections = c_root - (c_root - c_tip) / span * abs(y_sections) # chord at each section

        # Calculate volume of wing
        dV = 0
        for i in range(len(y_sections)-1):
            y1 = y_sections[i]
            y2 = y_sections[i+1]
            c1 = c_sections[i]
            c2 = c_sections[i+1]
            x1 = c1 * (1 - taper) / 2 + y1 * np.tan(theta) * lambda_ * (1 - taper) / 2
            x2 = c2 * (1 - taper) / 2 + y2 * np.tan(theta) * lambda_ * (1 - taper) / 2
            dA = (x1 + x2) / 2 * (y2 - y1)
            dV += dA

        volume_fus = dV

        # Equation from Raymer's book eqn. 16.47
        cn_beta_fus = -1.3 * volume_fus / wing_area / span * (l_f / width_max)

        outputs["data:aerodynamics:fuselage:cruise:CnBeta"] = cn_beta_fus
