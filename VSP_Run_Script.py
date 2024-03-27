import openvsp as vsp
from enum import Enum
import json
import sys
import os
import all_func
import re
import numpy as np

#SET ANALYSIS INPUTS OBTAINED FROM JSON FILE. (UPDATED AND CALCULATED MODEL SPECIFIC VALUES STORED IN PARAMS DICT - LOOK AT all_func.params_from_json)
def set_analysis_inputs_vsp(params_dict):
    vsp.SetIntAnalysisInput(myAnalysis, "AnalysisMethod", params_dict['analysis_method'])
    vsp.SetIntAnalysisInput(myAnalysis, "UnsteadyType", params_dict['stability_type']) 
    vsp.SetIntAnalysisInput(myAnalysis, "RefFlag", params_dict['RefFlag']) #USER DEFINED
    vsp.SetIntAnalysisInput(myAnalysis, "GeomSet", params_dict['GeomSet']) #USER DEFINED
    vsp.SetIntAnalysisInput(myAnalysis, "CGGeomSet", params_dict['CGGeomSet']) #USER DEFINED
    #vsp.SetDoubleAnalysisInput(myAnalysis, "Sref", params_dict['Sref']) #autoassigned  - see refflag in params, vsp.SetVSPAERORefWingID in VSP_create.py
    #vsp.SetDoubleAnalysisInput(myAnalysis, "bref", params_dict['bref']) #autoassigned  - see refflag in params, vsp.SetVSPAERORefWingID in VSP_create.py
    #vsp.SetDoubleAnalysisInput(myAnalysis, "cref", params_dict['cref']) #autoassigned  - see refflag in params, vsp.SetVSPAERORefWingID in VSP_create.py
    vsp.SetDoubleAnalysisInput(myAnalysis, "Xcg", params_dict['Xcg']) #assigned from mass analysis output
    vsp.SetDoubleAnalysisInput(myAnalysis, "Ycg", params_dict['Ycg']) #assigned from mass analysis output
    vsp.SetDoubleAnalysisInput(myAnalysis, "Zcg", params_dict['Zcg']) #assigned from mass analysis output
    vsp.SetDoubleAnalysisInput(myAnalysis, "AlphaStart", params_dict['Alpha_Start']) #USER DEFINED
    vsp.SetDoubleAnalysisInput(myAnalysis, "AlphaEnd", params_dict['Alpha_End']) #USER DEFINED
    vsp.SetIntAnalysisInput(myAnalysis, "AlphaNpts", params_dict['AlphaNpts']) #USER DEFINED
    vsp.SetDoubleAnalysisInput(myAnalysis, "BetaStart", params_dict['Beta_Start']) #USER DEFINED
    vsp.SetIntAnalysisInput(myAnalysis, "BetaNpts", params_dict['BetaNpts']) #USER DEFINED
    vsp.SetDoubleAnalysisInput(myAnalysis, "MachStart", params_dict['Mach_Start']) #USER DEFINED 
    vsp.SetIntAnalysisInput(myAnalysis, "MachNpts", params_dict['MachNpts']) #USER DEFINED 
    vsp.SetDoubleAnalysisInput(myAnalysis, "ReCref", params_dict['ReCref']) #ASSIGNED FROM CALCULATIONS
    vsp.SetIntAnalysisInput(myAnalysis, "ReCrefNpts", params_dict['ReCrefNpts']) #USER DEFINED
    vsp.SetDoubleAnalysisInput(myAnalysis, "Vinf", params_dict['Vinf']) #ASSIGNED FROM CALCULATIONS
    vsp.SetDoubleAnalysisInput(myAnalysis, "Rho", params_dict['Rho']) #ASSIGNED FROM CALCULATIONS
    vsp.SetIntAnalysisInput(myAnalysis, "KTCorrection",params_dict['KTCorrection']) #USER DEFINED
    vsp.Update()

print("VSP_Run_Script - Running") #output dump 
current_wd = os.getcwd()

vsp_run_dir = sys.argv[1]
input_param = sys.argv[2]
vsp_input = sys.argv[3]

global_vsp_run_dir = os.path.join(current_wd,vsp_run_dir)

os.chdir(global_vsp_run_dir) #change dir to vsp run directory

#constants
R = 287.05  # Specific gas constant for air in J/(kg*K)
T0 = 288.15  # Sea level standard temperature in K
p0 = 101325  # Sea level standard pressure in Pa
g = 9.80665  # Acceleration due to gravity in m/s^2
L = 0.0065  # Temperature lapse rate in K/m

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
params_dict_calc = all_func.params_from_json(input_param) # JSON FILE AS DICT

#CALL USER DEFINED PARAMS
h = params_dict_calc['altitude']
Mach = params_dict_calc['Mach_Start']
c = params_dict_calc['cref']

#CALCULTIONS FOR PARAMS TO BE ASSIGNED
rho = 1.225 * (1 - 22.558 * 10**(-6) * h) ** 4.2559
T = 288.15-0.0065*h
vinf = np.sqrt(1.4*R*T)*float(Mach[0]) 
Re = rho*vinf*float(c[0])/(14*10**(-6))

#WRITE PARAMS TO JSON FILE
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


# Write the JSON string to the file (UPDATES THE JSON FILE IN THE VSP_RUN - RUN SPECIFIC DIRECTORY)
with open(input_param, 'w') as f:
    json.dump(data_param, f, indent=2,separators=(',', ':'))

#Alpha Sweep analysis using VSPAero
myAnalysis = "VSPAEROSweep"
vsp.SetAnalysisInputDefaults(myAnalysis)
# Call the function to set parameters from the JSON file
params_dict = all_func.params_from_json(input_param)  #RE-CALL THE NEW UPDATED PARAMS FILE TO DICTIONARY 
set_analysis_inputs_vsp(params_dict) #SET PARAMS FROM DICT

vsp.PrintAnalysisInputs(myAnalysis) #PRINT ANALYSIS INPUTS TO CHECK IN OUTPUT DUMP
#Run analysis and write results to CSV file
allResults = vsp.ExecAnalysis(myAnalysis) #EXECUTE ANALYSIS
vsp.WriteResultsCSVFile(allResults, "Results.csv") #WRITE RESULTS

os.chdir(current_wd)
print("VSP_Run_Script - Ended")