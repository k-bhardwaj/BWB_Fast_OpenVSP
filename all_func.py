import os
import shutil
import re
import json


def empty_out_dir(output_dir):
    if os.path.exists(output_dir):
        shutil.rmtree(output_dir)
        os.makedirs(output_dir)
    else:
        os.makedirs(output_dir)
    return output_dir

def create_dir(output_dir):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    return output_dir

def round4(value):
    # Convert to float and round to 4 decimal places
    val = float(value)
    if abs(val) < 0.0001:
        return 0.0
    else:
        return round(val, 4)
    
def round2(value):
    # Convert to float and round to 3 decimal places
    val = float(value)
    if abs(val) < 0.01:
        return 0.0
    return round(val, 3)

def read_mass_file(mass_file):
    dict = {}
    try:
        with open(mass_file, 'r') as file:
            lines = file.readlines()
            for line in lines:
                if line.startswith("Totals"):  # Check if the line starts with "Totals"
                    parts = re.split(r'\s+', line.strip())
                    if len(parts) >= 12:  # Ensure there are enough parts to unpack
                        dict["Name"], dict["Mass"], dict["cgX"], dict["cgY"], dict["cgZ"], dict["Ixx"], dict["Iyy"], dict["Izz"], dict["Ixy"], dict["Ixz"], dict["Iyz"], dict["Volume"] = parts[0], *map(round4, parts[1:])
                        break  # Stop reading after finding the totals
    except FileNotFoundError:
        print(f"Error: File not found at path '{mass_file}'")
        exit()
    return dict

def params_from_json(json_file):
    import openvsp as vsp
    # Read parameters from JSON file
    with open(json_file, 'r') as f:
        parameters = json.load(f)

    analysis_method = [getattr(vsp, parameters["analysis_method"])]
    stability_type = [getattr(vsp, parameters["stability_type"])]  
    altitude = parameters["altitude"]
    Sref = parameters["Sref"]
    bref = parameters["bref"]
    cref = parameters["cref"]
    Xcg = parameters["Xcg"]
    Ycg = parameters["Ycg"]
    Zcg = parameters["Zcg"]
    Alpha_Start = parameters["Alpha_Start"]
    Alpha_End = parameters["Alpha_End"]
    AlphaNpts = parameters["AlphaNpts"]
    Beta_Start = parameters["Beta_Start"]
    BetaNpts = parameters["BetaNpts"]
    Mach_Start = parameters["Mach_Start"]
    MachNpts = parameters["MachNpts"]
    ReCref = parameters["ReCref"]
    ReCrefNpts = parameters["ReCrefNpts"]
    KTCorrection = parameters["KTCorrection"]
    RefFlag = parameters["RefFlag"]
    cruise_aoa = parameters["cruise_aoa"]
    CGGeomSet = parameters["CGGeomSet"]
    GeomSet = parameters["GeomSet"]
    Vinf = parameters["Vinf"]
    Rho = parameters["Rho"]

    params_dict = {
        "analysis_method": analysis_method,
        "stability_type": stability_type,
        "altitude": altitude,
        "Sref": Sref,
        "bref": bref,
        "cref": cref,
        "Xcg": Xcg,
        "Ycg": Ycg,
        "Zcg": Zcg,
        "Alpha_Start": Alpha_Start,
        "Alpha_End": Alpha_End,
        "AlphaNpts": AlphaNpts,
        "Beta_Start": Beta_Start,
        "BetaNpts": BetaNpts,
        "Mach_Start": Mach_Start,
        "MachNpts": MachNpts,
        "ReCref": ReCref,
        "ReCrefNpts": ReCrefNpts,
        "Vinf" : Vinf,
        "Rho" : Rho,
        "KTCorrection": KTCorrection,
        "RefFlag": RefFlag,
        "cruise_aoa": cruise_aoa,
        "CGGeomSet": CGGeomSet,
        "GeomSet": GeomSet
    }
    return params_dict