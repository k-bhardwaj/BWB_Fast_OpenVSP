import openvsp as vsp
from enum import Enum
import json
import sys
import os
import all_func
import re
import numpy as np

def params_from_json(json_file):
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

def set_analysis_inputs_vsp(params_dict):
    vsp.SetIntAnalysisInput(myAnalysis, "AnalysisMethod", params_dict['analysis_method'])
    vsp.SetIntAnalysisInput(myAnalysis, "UnsteadyType", params_dict['stability_type'])
    vsp.SetIntAnalysisInput(myAnalysis, "RefFlag", params_dict['RefFlag'])
    vsp.SetIntAnalysisInput(myAnalysis, "GeomSet", params_dict['GeomSet'])
    vsp.SetIntAnalysisInput(myAnalysis, "CGGeomSet", params_dict['CGGeomSet'])
    #vsp.SetDoubleAnalysisInput(myAnalysis, "Sref", params_dict['Sref'])
    #vsp.SetDoubleAnalysisInput(myAnalysis, "bref", params_dict['bref'])
    #vsp.SetDoubleAnalysisInput(myAnalysis, "cref", params_dict['cref'])
    vsp.SetDoubleAnalysisInput(myAnalysis, "Xcg", params_dict['Xcg'])
    vsp.SetDoubleAnalysisInput(myAnalysis, "Ycg", params_dict['Ycg'])
    vsp.SetDoubleAnalysisInput(myAnalysis, "Zcg", params_dict['Zcg'])
    vsp.SetDoubleAnalysisInput(myAnalysis, "AlphaStart", params_dict['Alpha_Start'])
    vsp.SetDoubleAnalysisInput(myAnalysis, "AlphaEnd", params_dict['Alpha_End'])
    vsp.SetIntAnalysisInput(myAnalysis, "AlphaNpts", params_dict['AlphaNpts'])
    vsp.SetDoubleAnalysisInput(myAnalysis, "BetaStart", params_dict['Beta_Start'])
    vsp.SetIntAnalysisInput(myAnalysis, "BetaNpts", params_dict['BetaNpts'])
    vsp.SetDoubleAnalysisInput(myAnalysis, "MachStart", params_dict['Mach_Start'])
    vsp.SetIntAnalysisInput(myAnalysis, "MachNpts", params_dict['MachNpts'])
    vsp.SetDoubleAnalysisInput(myAnalysis, "ReCref", params_dict['ReCref'])
    vsp.SetIntAnalysisInput(myAnalysis, "ReCrefNpts", params_dict['ReCrefNpts'])
    vsp.SetDoubleAnalysisInput(myAnalysis, "Vinf", params_dict['Vinf'])
    vsp.SetDoubleAnalysisInput(myAnalysis, "Rho", params_dict['Rho'])
    vsp.SetIntAnalysisInput(myAnalysis, "KTCorrection",params_dict['KTCorrection'])
    vsp.Update()

print("VSP_Run_Script - Running")
current_wd = os.getcwd()

vsp_run_dir = sys.argv[1]
input_param = sys.argv[2]
vsp_input = sys.argv[3]

global_vsp_run_dir = os.path.join(current_wd,vsp_run_dir)

os.chdir(global_vsp_run_dir)

#constants
R = 287.05  # Specific gas constant for air in J/(kg*K)
T0 = 288.15  # Sea level standard temperature in K
p0 = 101325  # Sea level standard pressure in Pa
g = 9.80665  # Acceleration due to gravity in m/s^2
L = 0.0065  # Temperature lapse rate in K/m

#vsp.ClearVSPModel()
#vsp.VSPRenew()
vsp.ReadVSPFile(vsp_input)
os.chdir(global_vsp_run_dir)

#Run CompGeom to generate geometry
compGeom = "VSPAEROComputeGeometry"
vsp.SetAnalysisInputDefaults(compGeom)
compGeom_results = vsp.ExecAnalysis(compGeom)

#compute mass 
Mass_Props = "MassProp"
vsp.SetAnalysisInputDefaults(Mass_Props)
compMass_results = vsp.ExecAnalysis(Mass_Props)
model_name = os.path.splitext(os.path.basename(vsp_input))[0]
mass_file = f"{model_name}_MassProps.txt"
mass_dict=all_func.read_mass_file(mass_file)
params_dict_calc = params_from_json(input_param)

h = params_dict_calc['altitude']
Mach = params_dict_calc['Mach_Start']
c = params_dict_calc['cref']

rho = 1.225 * (1 - 22.558 * 10**(-6) * h) ** 4.2559
T = 288.15-0.0065*h
vinf = np.sqrt(1.4*R*T)*float(Mach[0]) 
Re = rho*vinf*float(c[0])/(14*10**(-6))


with open(input_param, 'r') as f:
    data_param = json.load(f)
# Update the values of Xcg, Ycg, and Zcg
data_param['Xcg'] = [mass_dict["cgX"]]  # New value for Xcg
data_param['Ycg'] = [mass_dict["cgY"]]   # New value for Ycg
data_param['Zcg'] = [mass_dict["cgZ"]]  # New value for Zcg

# #UPDATE RHO, VINF, RECREF
data_param['Vinf'] = [vinf]
data_param['Rho'] = [rho]
data_param['ReCref'] = [Re]


# Write the JSON string to the file
with open(input_param, 'w') as f:
    json.dump(data_param, f, indent=2,separators=(',', ':'))

#Alpha Sweep analysis using VSPAero
myAnalysis = "VSPAEROSweep"
vsp.SetAnalysisInputDefaults(myAnalysis)
# Call the function to set parameters from the JSON file
params_dict = params_from_json(input_param)
set_analysis_inputs_vsp(params_dict)

vsp.PrintAnalysisInputs(myAnalysis)
#Run analysis and write results to CSV file
allResults = vsp.ExecAnalysis(myAnalysis)
vsp.WriteResultsCSVFile(allResults, "Results.csv")

os.chdir(current_wd)
print("VSP_Run_Script - Ended")