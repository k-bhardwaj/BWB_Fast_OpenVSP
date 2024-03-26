import openvsp as vsp
from enum import Enum
import json
import sys
import os
import math
import xml.etree.ElementTree as ET

def xml_to_dict(element):
    """
    Recursively convert an ElementTree element to a dictionary.
    """
    # Initialize an empty dictionary
    element_dict = {}

    # Iterate over the element's children
    for child in element:
        # If the child has children, recursively call xml_to_dict
        if len(child):
            element_dict[child.tag] = xml_to_dict(child)
        else:
            # Otherwise, add the tag and text content to the dictionary
            element_dict[child.tag] = child.text.strip() if child.text else None

    return element_dict
print("VSP_Create - Running")
current_wd = os.getcwd()

vsp_run_dir = sys.argv[1]
fast_output_file = sys.argv[2]
airfoil_file = sys.argv[3]
VSP_model_name = f"{sys.argv[4]}.vsp3"

global_vsp_run_dir = os.path.join(current_wd,vsp_run_dir)
os.chdir(global_vsp_run_dir)

vsp.ClearVSPModel()

tree = ET.parse(fast_output_file)
root = tree.getroot()

data_geometry = root.find('./data/geometry')
sizing_dict = xml_to_dict(data_geometry)

data_weight = root.find('./data/weight')
weight_dict = xml_to_dict(data_weight)

fuselage_root = float(sizing_dict['fuselage']['length'])
fuselage_tip = float(sizing_dict['wing']['root']['chord'])
fuselage_halfspan = float(sizing_dict['fuselage']['maximum_width'])/2
fuselage_sweep_25 = float(sizing_dict['fuselage']['sweep_25_centerbody'])
fuselage_sweep_loc = 0

kink_wing_root = fuselage_tip
wing_halfspan_to_kink = float(sizing_dict['wing']['kink']['y']) - fuselage_halfspan
wing_kink_tip = float(sizing_dict['wing']['kink']['chord'])
kink_section_0sweep_rad = math.atan(float(sizing_dict['wing']['kink']['leading_edge']['x']['local'])/wing_halfspan_to_kink)
kink_section_0sweep_deg = math.degrees(kink_section_0sweep_rad)
kink_sweep_loc = 0

tip_section_root = float(wing_kink_tip)
tip_section_tip = float(sizing_dict['wing']['tip']['chord'])
tip_section_halfspan = float(sizing_dict['wing']['tip']['y'])-float(sizing_dict['wing']['kink']['y'])
tip_0sweep = float(sizing_dict['wing']['sweep_0'])
tip_sweep_loc = 0

dihedral = 0 # general_undefined_params
twist = 0 # general_undefined_params
twist_loc = 0 # general_undefined_params
wing_density = 250 #hardcoded value

# print(fuselage_halfspan,fuselage_root,fuselage_sweep_25,fuselage_tip)
# print(wing_root,wing_halfspan_to_kink,wing_kink_chord,kink_section_0sweep_deg)
# print(tip_section_root,tip_section_halfspan,tip_section_tip,tip_0sweep)
stdout = vsp.cvar.cstdout
errorMgr = vsp.ErrorMgrSingleton.getInstance()

# Setup Check
vsp.VSPCheckSetup()
errorMgr.PopErrorAndPrint(stdout)

fast_wing = vsp.AddGeom("WING")
vsp.SetGeomName(fast_wing,VSP_model_name)
vsp.SetParmVal(fast_wing, "Density", "Mass_Props", wing_density)


# Split wing into 3 Sections (2 splits)
# This produces 3 XSecs (cross sectional areas that define the wing)
for i in [1, 2]:
    vsp.InsertXSec(fast_wing, i, vsp.XS_SIX_SERIES)
    vsp.CopyXSec(fast_wing , i)

# Wing Section 1 "XSec_1" Body
vsp.SetParmValUpdate(fast_wing, "Span", "XSec_1",fuselage_halfspan)
vsp.SetParmValUpdate(fast_wing, "Root_Chord", "XSec_1", fuselage_root)
vsp.SetParmValUpdate(fast_wing, "Tip_Chord", "XSec_1", fuselage_tip)
vsp.SetParmValUpdate(fast_wing, "Sweep", "XSec_1", fuselage_sweep_25)
vsp.SetParmValUpdate(fast_wing, "Sweep_Location", "XSec_1", fuselage_sweep_loc)
vsp.SetParmValUpdate(fast_wing, "Twist", "XSec_1", twist)
vsp.SetParmValUpdate(fast_wing, "Twist_Location", "XSec_1", twist_loc)
vsp.SetParmValUpdate(fast_wing, "Dihedral", "XSec_1", dihedral)

# Wing Section 2 "XSec_2" Kinked Section
vsp.SetParmValUpdate(fast_wing, "Span", "XSec_2",wing_halfspan_to_kink)
vsp.SetParmValUpdate(fast_wing, "Root_Chord", "XSec_2", kink_wing_root)
vsp.SetParmValUpdate(fast_wing, "Tip_Chord", "XSec_2", wing_kink_tip)
vsp.SetParmValUpdate(fast_wing, "Sweep", "XSec_2", kink_section_0sweep_deg)
vsp.SetParmValUpdate(fast_wing, "Sweep_Location", "XSec_2", kink_sweep_loc)
vsp.SetParmValUpdate(fast_wing, "Twist", "XSec_2", twist)
vsp.SetParmValUpdate(fast_wing, "Twist_Location", "XSec_2", twist_loc)
vsp.SetParmValUpdate(fast_wing, "Dihedral", "XSec_2", dihedral)

# Wing Section 3 "XSec_3" Tip Section
vsp.SetParmValUpdate(fast_wing, "Span", "XSec_3", tip_section_halfspan)
vsp.SetParmValUpdate(fast_wing, "Root_Chord", "XSec_3", tip_section_root)
vsp.SetParmValUpdate(fast_wing, "Tip_Chord", "XSec_3", tip_section_tip)
vsp.SetParmValUpdate(fast_wing, "Sweep", "XSec_3", tip_0sweep)
vsp.SetParmValUpdate(fast_wing, "Sweep_Location", "XSec_3", tip_sweep_loc)
vsp.SetParmValUpdate(fast_wing, "Twist", "XSec_3", twist)
vsp.SetParmValUpdate(fast_wing, "Twist_Location", "XSec_3", twist_loc)
vsp.SetParmValUpdate(fast_wing, "Dihedral", "XSec_3", dihedral)


xsec_surf = vsp.GetXSecSurf(fast_wing, 0)
for i in [0,1,2,3]:
    vsp.ChangeXSecShape(xsec_surf, i, vsp.XS_FILE_AIRFOIL)
    xsec_id = f"xsec{i}"
    xsec_id = vsp.GetXSec(xsec_surf, i)
    vsp.ReadFileAirfoil(xsec_id, airfoil_file)

vsp.SetVSPAERORefWingID(fast_wing)
vsp.Update()


vsp.WriteVSPFile(VSP_model_name,vsp.SET_ALL)

geoms = vsp.FindGeoms()
errorMgr.PopErrorAndPrint(stdout)
os.chdir(current_wd)
vsp.ClearVSPModel()
print("VSP_Create - Ended")