"""
This file contains the component "calculo_cl_landing" which contains one class
called compute_delta_cz_highlift. The main function of the class is subdivided
under two cases: landing or takeoff. It makes use of the option 
"landing_flag" to determine which case is carried out. The "landing_flag" is 
activated if it is called by the group "aerodinamica.landing.2" which is
defined in aerodinamica_landing.py, under the aerodynamics module.

Depending on the case, this component will call different inputs:
    - Flap and slat angles
    - Mach number
    - CL and CD of high lift surfaces
    
Regardless of the case, the component takes as input the wing, the flap and
the slats' geometry. 

The outputs are the increments in CL and CD due to high lift devices, either
in takeoff or landing configuration.
"""

import math
import numpy as np
import openmdao.api as om
from fastoad.module_management.service_registry import RegisterSubmodel
from importlib.resources import open_text
from scipy import interpolate

from . import resources

LIFT_EFFECTIVENESS_FILENAME = "interpolation of lift effectiveness.txt"


@RegisterSubmodel("calculo_high_lift", "high_lift.2")
class compute_delta_cz_highlift(om.ExplicitComponent):
    """Computation of CL and CD for whole aircraft."""
    
    def initialize(self):
        self.options.declare("landing_flag", default=False, types=bool)
    
    def setup(self):
        
        if self.options["landing_flag"]:
            self.add_input("data:mission:sizing:landing:flap_angle", val=np.nan, units="deg") 
            self.add_input("data:mission:sizing:landing:slat_angle", val=np.nan, units="deg") 
            self.add_input("data:aerodynamics:aircraft:landing:mach", val=np.nan) 
            self.add_output("data:aerodynamics:high_lift_devices:landing:CL") 
            self.add_output("data:aerodynamics:high_lift_devices:landing:CD") 
            
        else:
            self.add_input("data:mission:sizing:takeoff:flap_angle", val=np.nan, units="deg") 
            self.add_input("data:mission:sizing:takeoff:slat_angle", val=np.nan, units="deg") 
            self.add_input("data:aerodynamics:aircraft:takeoff:mach", val=np.nan) 
            self.add_output("data:aerodynamics:high_lift_devices:takeoff:CL") 
            self.add_output("data:aerodynamics:high_lift_devices:takeoff:CD") 
            
        self.add_input("data:geometry:flap:chord_ratio", val=np.nan) 
        self.add_input("data:geometry:flap:span_ratio", val=np.nan) 
        self.add_input("data:geometry:slat:chord_ratio", val=np.nan) 
        self.add_input("data:geometry:slat:span_ratio", val=np.nan) 
        self.add_input("data:geometry:wing:sweep_0", val=np.nan, units="deg") 
        self.add_input("data:geometry:wing:sweep_100_outer", val=np.nan, units="deg") 

    def compute(self, inputs, outputs, discrete_inputs=None, discrete_outputs=None):
        
        if self.options["landing_flag"]:
            flap_angle_landing = inputs["data:mission:sizing:landing:flap_angle"]
            slat_angle_landing = inputs["data:mission:sizing:landing:slat_angle"]
            mach_landing = inputs["data:aerodynamics:aircraft:landing:mach"]
        else:
            flap_angle_takeoff = inputs["data:mission:sizing:takeoff:flap_angle"]
            slat_angle_takeoff = inputs["data:mission:sizing:takeoff:slat_angle"]
            mach_takeoff = inputs["data:aerodynamics:aircraft:takeoff:mach"]

        flap_chord_ratio = inputs["data:geometry:flap:chord_ratio"]
        flap_span_ratio = inputs["data:geometry:flap:span_ratio"]
        slat_chord_ratio = inputs["data:geometry:slat:chord_ratio"]
        slat_span_ratio = inputs["data:geometry:slat:span_ratio"]
        le_angle = inputs["data:geometry:wing:sweep_0"]
        tl_angle = inputs["data:geometry:wing:sweep_100_outer"]
        
        cl_delta = 5.05503E-7 + 0.00666 * slat_chord_ratio + 0.23758 * \
            slat_chord_ratio**2 - 4.3639 * slat_chord_ratio**3 + \
            51.16323 * slat_chord_ratio**4 - 320.10803 * \
            slat_chord_ratio**5 + 1142.23033 * slat_chord_ratio**6 - \
            2340.75209 * slat_chord_ratio**7 + 2570.35947 * \
            slat_chord_ratio**8 - 1173.73465 * slat_chord_ratio**9
        
        
        if self.options["landing_flag"]:
            flap_angle_landing = flap_angle_landing / 180 * math.pi
            slat_angle_landing = slat_angle_landing / 180 * math.pi
            

            # 0.197 is from Ceras data,calculated the average chord of the flap
            ratio_c_flap = (1. + flap_chord_ratio * math.cos(flap_angle_landing))
            
            alpha_flap = self._compute_alpha_flap(
                flap_angle_landing *
                57.3,
                flap_chord_ratio)

            delta_cz_flap = 2. * math.pi / \
                math.sqrt(1 - mach_landing**2) * ratio_c_flap * alpha_flap * flap_angle_landing
            
            ratio_c_slat = (1. + slat_chord_ratio * math.cos(slat_angle_landing))

            delta_cz_slat = cl_delta * slat_angle_landing * 57.3 * ratio_c_slat
            delta_cz_total_landing = delta_cz_flap * flap_span_ratio * \
                math.cos(tl_angle) + delta_cz_slat * slat_span_ratio * \
                math.cos(le_angle)  

            outputs["data:aerodynamics:high_lift_devices:landing:CL"] = delta_cz_total_landing
            
            """
            Calculo delta_cd_highlift
            """
            
            cx0_flap_landing = (-0.01523 + 0.05145 * flap_angle_landing - 9.53201E-4 * flap_angle_landing**2 +
                        7.5972E-5 * flap_angle_landing**3) * flap_span_ratio / 100
                
            cx0_slat_landing = (-0.00266 + 0.06065 * slat_angle_landing - 0.03023 * slat_angle_landing**2 +
                        0.01055 * slat_angle_landing**3 - 0.00176 * slat_angle_landing**4 +
                        1.77986E-4 * slat_angle_landing**5 - 1.11754E-5 * slat_angle_landing**6 +
                        4.19082E-7 * slat_angle_landing**7 - 8.53492E-9 * slat_angle_landing**8 +
                        7.24194E-11 * slat_angle_landing**9) * slat_span_ratio / 100          
                
            delta_cx_total_landing = cx0_flap_landing + cx0_slat_landing
            
            outputs["data:aerodynamics:high_lift_devices:landing:CD"] = delta_cx_total_landing
        
        else:
            """
            takeoff
            """

            flap_angle_takeoff = flap_angle_takeoff / 180 * math.pi
            slat_angle_takeoff = slat_angle_takeoff / 180 * math.pi

        
            ratio_c_flap = (1. + flap_chord_ratio * math.cos(flap_angle_takeoff))
        
     
            alpha_flap = self._compute_alpha_flap(
                flap_angle_takeoff *
                57.3,
                flap_chord_ratio)
            
            delta_cz_flap = 2. * math.pi / \
                math.sqrt(1 - mach_takeoff**2) * ratio_c_flap * alpha_flap * flap_angle_takeoff
            
            ratio_c_slat = (1. + slat_chord_ratio * math.cos(slat_angle_takeoff))
   
            delta_cz_slat = cl_delta * slat_angle_takeoff * 57.3 * ratio_c_slat
            delta_cz_total_takeoff = delta_cz_flap * flap_span_ratio * \
                math.cos(tl_angle) + delta_cz_slat * slat_span_ratio * \
                    math.cos(le_angle)  # this equation is from ref Raymer book

            outputs["data:aerodynamics:high_lift_devices:takeoff:CL"] = delta_cz_total_takeoff
            
            """
            Calculo delta_cd_highlift
            """
            
            cx0_flap_takeoff = (-0.01523 + 0.05145 * flap_angle_takeoff - 9.53201E-4 * flap_angle_takeoff**2 +
                        7.5972E-5 * flap_angle_takeoff**3) * flap_span_ratio / 100
                
            cx0_slat_takeoff = (-0.00266 + 0.06065 * slat_angle_takeoff - 0.03023 * slat_angle_takeoff**2 +
                        0.01055 * slat_angle_takeoff**3 - 0.00176 * slat_angle_takeoff**4 +
                        1.77986E-4 * slat_angle_takeoff**5 - 1.11754E-5 * slat_angle_takeoff**6 +
                        4.19082E-7 * slat_angle_takeoff**7 - 8.53492E-9 * slat_angle_takeoff**8 +
                        7.24194E-11 * slat_angle_takeoff**9) * slat_span_ratio / 100          
                
            delta_cx_total_takeoff = cx0_flap_takeoff + cx0_slat_takeoff
            
            outputs["data:aerodynamics:high_lift_devices:takeoff:CD"] = delta_cx_total_takeoff
            
    def _compute_alpha_flap(self, flap_angle, ratio_cf_flap):
        temp_array = []
        with open_text(resources, LIFT_EFFECTIVENESS_FILENAME) as fichier:
            for line in fichier:
                temp_array.append([float(x) for x in line.split(",")])
        x1 = []
        y1 = []
        x2 = []
        y2 = []
        x3 = []
        y3 = []
        x4 = []
        y4 = []
        x5 = []
        y5 = []

        for arr in temp_array:
            x1.append(arr[0])
            y1.append(arr[1])
            x2.append(arr[2])
            y2.append(arr[3])
            x3.append(arr[4])
            y3.append(arr[5])
            x4.append(arr[6])
            y4.append(arr[7])
            x5.append(arr[8])
            y5.append(arr[9])

        tck1 = interpolate.splrep(x1, y1, s=0)
        tck2 = interpolate.splrep(x2, y2, s=0)
        tck3 = interpolate.splrep(x3, y3, s=0)
        tck4 = interpolate.splrep(x4, y4, s=0)
        tck5 = interpolate.splrep(x5, y5, s=0)
        ynew1 = interpolate.splev(flap_angle, tck1, der=0)
        ynew2 = interpolate.splev(flap_angle, tck2, der=0)
        ynew3 = interpolate.splev(flap_angle, tck3, der=0)
        ynew4 = interpolate.splev(flap_angle, tck4, der=0)
        ynew5 = interpolate.splev(flap_angle, tck5, der=0)
        zs = [0.15, 0.20, 0.25, 0.30, 0.40]
        y_final = [ynew1, ynew2, ynew3, ynew4, ynew5]
        tck6 = interpolate.splrep(zs, y_final, s=0)
        return interpolate.splev(ratio_cf_flap, tck6, der=0)     
        
        