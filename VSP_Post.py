import numpy as np
import re
import csv
import pandas
import os
import shutil
import json
import all_func
import sys
import openvsp as vsp


#output_file_stab = os.path.join(output_dir, 'BWB_CleanedFile.stab')
#output_file_csv = os.path.join(output_dir, 'BWB_Data.csv')


def round4(value):
    # Convert to float and round to 4 decimal places
    val = float(value)
    if abs(val) < 0.0001:
        return 0.0
    else:
        return round(val, 4)

def empty_out_dir(output_dir):
    if os.path.exists(output_dir):
        shutil.rmtree(output_dir)
        os.makedirs(output_dir)
    else:
        os.makedirs(output_dir)

def clean_stab(input_file, output_file):
    with open(input_file, 'r') as file:
        content = file.read()
        #clean file for processing
        cleaned_content = re.sub(r'^\*.*\n|#.*\n', '', content, flags=re.MULTILINE)
        cleaned_content = re.sub(r'(SM|Coef)', r'\n\1', cleaned_content)   #hard-coded line due to lack of options to process section neatly
    with open(output_file, 'w') as out_file:
        out_file.write(cleaned_content)
    return cleaned_content

def AoA_data(sections):    
    num = len(sections)
    #print(num)
    linesfirst = sections[0].split('\n')
    #print(sections[0])
    lineslast = sections[num-4].split('\n')
    #print(lineslast)
    aoa_first_line = None
    aoa_last_line = None
    for lines in linesfirst:
        if "AoA_" in lines:
            aoa_first_line = lines
    for lines in lineslast:
        #print(lines)
        if "AoA_" in lines:
            aoa_last_line = lines  
    if aoa_first_line and aoa_last_line:
        # Extract the value of AoA from the line
        aoa_value_start = float(aoa_first_line.split()[1])
        aoa_value_end = float(aoa_last_line.split()[1])
        # Calculate the number of sections
        n = num/4
        return aoa_value_start, aoa_value_end, n,num
    else:
        print("No lines containing 'AoA_' found.")
        return None

def csv_stab(cleaned_content,output_file_csv):
    sections = re.split(r'\n\s*\n', cleaned_content)
    aoa_start, aoa_end, n_iter, num_sections = AoA_data(sections)
    n_iter = int(n_iter)
    angle_range = np.linspace(aoa_start,aoa_end,n_iter)
    csv_dict_nested = {}
    #csv_dict={}
    angle_counter = 0
    header = []
    for section_number,section in enumerate(sections):
        #coef_data = {}
        #sm_np_data = {}
        if section_number%2==0 and section_number%4!=0:
            angle = angle_range[angle_counter]
            #print(section_number)
            sectioncoef_data = sections[section_number]  # Section data
            sectionnext_data = sections[section_number+1] # next section data 
            lines_coef = sectioncoef_data.split('\n')
            lines_next = sectionnext_data.split('\n')
            csv_dict={}
            for line in lines_coef[1:]:  # Skip the header line
                columns = line.split()
                if columns: 
                    coef_name = columns[0]
                    for i, value in enumerate(columns[1:], start=1):
                        key = f"{coef_name}_{lines_coef[0].split()[i]}"
                        csv_dict[key] = round4(value)
            for line in lines_next:
                columns = line.split()
                if columns: 
                    key = columns[0]
                    csv_dict[key] = round4(columns[1])
            if not header:
                header.insert(0,'angle')
                header.extend(csv_dict.keys())
            csv_dict_nested[angle] = csv_dict 
            #print(angle_counter)
            angle_counter+=1       
        #print(csv_dict_nested)
    # Write header (keys)
    with open(output_file_csv, 'w', newline='') as csvfile:
        csvwriter = csv.writer(csvfile)
        csvwriter.writerow(header)
    # Write data (values)
        for angle in list(csv_dict_nested.keys()):
            row = [angle] + list(csv_dict_nested[angle].values())
            csvwriter.writerow(row)       
    return csv_dict_nested




def post_process(mass_input_file,stab_input_file,input_param,outtxt):
    input_file = stab_input_file
    mass_file = mass_input_file
    output_file_stab = input_file.replace(".stab","_CLEANED_POST.stab")
    output_file_csv = input_file.replace("DegenGeom.stab","_POST.csv")

    cleaned_data = clean_stab(input_file,output_file_stab)        
    nested_dict = csv_stab(cleaned_data,output_file_csv)
    param_dict = all_func.params_from_json(input_param)

    angle_of_attack = param_dict['cruise_aoa']

    coefficient_data_cruise = nested_dict[angle_of_attack]  

    with open(mass_file, 'r') as file:
        data = file.read()

    totals = {
        "Name": None,
        "Mass": None,
        "cgX": None,
        "cgY": None,
        "cgZ": None,
        "Ixx": None,
        "Iyy": None,
        "Izz": None,
        "Ixy": None,
        "Ixz": None,
        "Iyz": None,
        "Volume": None
    }

    try:
        with open(mass_file, 'r') as file:
            lines = file.readlines()
            for line in lines:
                if line.startswith("Totals"):  # Check if the line starts with "Totals"
                    parts = re.split(r'\s+', line.strip())
                    if len(parts) >= 12:  # Ensure there are enough parts to unpack
                        totals["Name"], totals["Mass"], totals["cgX"], totals["cgY"], totals["cgZ"], totals["Ixx"], totals["Iyy"], totals["Izz"], totals["Ixy"], totals["Ixz"], totals["Iyz"], totals["Volume"] = parts[0], *map(all_func.round2, parts[1:])
                        break  # Stop reading after finding the totals
    except FileNotFoundError:
        print(f"Error: File not found at path '{mass_file}'")
        exit()

    # Constants
    g = 9.81
    Mach = float(param_dict['Mach_Start'][0])
    rho = float(param_dict['Rho'][0])
    u = float(param_dict['Vinf'][0])
    q = 0.5*rho*u*u
    b = float(param_dict['bref'][0])
    c = float(param_dict['cref'][0])
    S = float(param_dict['Sref'][0])
    # Mach = 0.8
    # rho = 0.41
    # u = 236
    # q = 0.5*rho*u*u
    # b = 36
    # c = 9.68
    # S = 276

    m = totals['Mass']
    Iyy = totals['Iyy']  # FROM MASS FILE
    Ixx = totals['Ixx']  # FROM MASS FILE
    Izz = totals['Izz'] # FROM MASS FILE

    # Longitudinal derivatives
    Cz_alpha = coefficient_data_cruise['CFz_Alpha']
    Cz_q = coefficient_data_cruise['CFz_q']
    Cm_alpha = coefficient_data_cruise['CMm_Alpha']
    Cm_q = coefficient_data_cruise['CMm_q']
    CL = coefficient_data_cruise['CL_Total']
    CL_alpha = coefficient_data_cruise['CL_Alpha']
    CD = coefficient_data_cruise['CD_Total']
    CL_u = coefficient_data_cruise['CL_U']
    CD_u = coefficient_data_cruise['CD_U']

    # Lateral-Directional derivatives
    Cy_beta = coefficient_data_cruise['CFy_Beta']
    Cy_p = coefficient_data_cruise['CFy_p']
    Cy_r = coefficient_data_cruise['CFy_r']
    Cl_beta = coefficient_data_cruise['CMl_Beta']
    Cl_p = coefficient_data_cruise['CMl_p']
    Cl_r = coefficient_data_cruise['CMl_r']
    Cn_beta = coefficient_data_cruise['CMn_Beta']
    Cn_p = coefficient_data_cruise['CMn_p']
    Cn_r = coefficient_data_cruise['CMn_r']
    # Assuming values for demonstration
    Cz_dm = 0.02
    Cm_dm = -0.03
    Cy_dl = 0.005
    Cy_dn = 0.02
    Cl_dl = 0.015
    Cl_dn = -0.01
    Cn_dl = 0.006
    Cn_dn = -0.02

    # Phugoid mode response 
    Xu = -(q*S/(m*u)) * (2*CD + CD_u)
    Zu = -(q*S/(m*u)) * (2*CL + CL_u)
    omega_ph = np.sqrt((-g * Zu) / u)
    zeta_ph = -Xu / (2 * omega_ph)
    if zeta_ph>=1 or zeta_ph<0:
        T_ph = -1
    else:     
        T_ph = 2 * np.pi / (omega_ph*np.sqrt(1 - (zeta_ph ** 2)))
    
    # Short Period response
    Z_alpha = -(q*S/m) * CL_alpha
    M_alpha = (q*S*b*c/Iyy) * Cm_alpha
    M_alphad = (q*S*b*(c**2)/(2*u*Iyy)) * 4 # Approximately the same
    #M_alphad = (q*S*b*(c*2)/(2*u*Iyy)) * Cm_q * ((CL_alpha)/(np.pi*(b/c)))
    M_q = (q*S*b*(c**2)/(2*u*Iyy)) * Cm_q
    omega_sp = np.sqrt(max(0, (Z_alpha * M_q / u) - M_alpha))  # Ensure expression inside sqrt is non-negative
    if omega_sp == 0:  # If omega_sp is zero, set zeta_sp to -1 and skip calculation of T
        zeta_sp = -1
        T_sp = None
    else:
        zeta_sp = -(M_q + M_alphad + (Z_alpha / u)) / (2 * omega_sp)
        if zeta_sp>=1 or zeta_sp<0:
            T_sp = -1
        else:
            print(zeta_sp,omega_sp)    
            T_sp = 2 * np.pi / (omega_sp * np.sqrt(1 - (zeta_sp ** 2)))

    # Dutch roll response
    Y_beta = q*S*Cy_beta/m
    N_beta = q*S*b*Cn_beta/Izz
    Y_r = q*S*b*Cy_r/(2*m*u)
    N_r = q*S*b*b*Cn_r/(2*Izz*u)
    omega_dr = np.sqrt(max(0, (Y_beta*N_r - N_beta*Y_r + u*N_beta)/u))  # Ensure expression inside sqrt is non-negative

    if omega_dr == 0:  # If omega_dr is zero, set zeta_dr to -1 and skip calculation of T
        zeta_dr = -1
        T_dr = None
    else:
        zeta_dr = -((Y_beta/u) + N_r)/(2*omega_dr)
        if zeta_dr>=1 or zeta_dr<0:
            T_dr = -1
        else:    
            T_dr = 2 * np.pi / (omega_dr * np.sqrt(1 - (zeta_dr ** 2)))


    # Spiral Mode response
    L_beta = (q*S*b/Ixx)*Cl_beta
    N_beta = (q*S*b/Izz)*Cn_beta
    L_r = q*S*b*b*Cl_r/(2*Ixx)
    N_r = q*S*b*b*Cn_r/(2*Izz*u)
    lambda_spiral = (L_beta * N_r - L_r * N_beta) / L_beta


    # Pure roll response
    Lp = q*S*b*b*Cl_p/(Ixx*2*u)
    roll_time_constant = -1/Lp
    lambda_roll = Lp

    # Pure yaw mode (without feedback control)
    omega_yw = np.sqrt(N_beta)
    zeta_yw = -N_r / (2*np.sqrt(N_beta))
    if zeta_yw>=1 or zeta_yw<0:
        T_yw = -1
    else:    
        T_yw = 2 * np.pi / (omega_yw* np.sqrt(1 - (zeta_yw ** 2)))


    #Open a new text file for writing
    #with open('aerodynamic_checks.txt', 'w') as file:
    #    Write the header row
    #    file.write("Parameter\tCheck Passed\tComments\n")

    # Longitudinal Derivatives Checks
    checks = [
    ("\n\nLONGITUDINAL STABILITY",m>0,"# SECTION HEADING",""),     
    ("\nCz_alpha", Cz_alpha > 0 and np.abs(Cz_alpha) > 0.01, "Positive force gradient on increasing alpha", "Vertically downward force when alpha increases\nPotential Reason: Lift coefficient negative.\nPotential Fix: Check airfoil."),
    ("Cz_q", Cz_q > 0 and np.abs(Cz_q) > 0.01, "Pitch up rotation increases alpha and thus, upward force.", "Upward pitch rate produces downward force\nPotential Reason: Lift coefficient gradient is negative.\nPotential Fix: Check airfoil."),
    ("Cm_alpha", Cm_alpha < 0 and np.abs(Cm_alpha) > 0.01, "Positive damping in pitch due to alpha.", "Increasing alpha increases pitching moment.\nPotential Reason: Neutral point is ahead of the CG.\nPotential Fix: Check CG position."),
    ("Cm_q", Cm_q < 0 and np.abs(Cm_q) > 0.01, "Positive pitch damping.", "Negative pitch damping.\nPotential Reason: Neutral point is ahead of the CG.\nPotential Fix: Check CG position."),
    
    # Lateral-directional derivatives checks
    ("\n\nLATERAL STABILITY",m>0,"# SECTION HEADING",""),        
    ("\nCy_beta", Cy_beta < 0 and np.abs(Cy_beta) > 0.01, "Correct sideforce produced in sideslip.", "Incorrect sideforce produced in sideslip.\nPotential Reason: CG could be behind the vertical tail.\nPotential Fix: Check CG location and vertical tail placement."),
    ("Cy_p", np.abs(Cy_p) < 0.01, "Neutral stability in sideforce due to roll rate.", "Excessive sideforce due to roll rate.\nPotential Reason: Wing parameters like sweep and dihedral might be sub-optimal.\nPotential Fix: Adjust wing geometry."),
    ("Cy_r", Cy_r > 0 and np.abs(Cy_r) > 0.01, "Positive yaw damping.", "Negative yaw damping.\nPotential Reason: Inadequate vertical tail design.\nPotential Fix: Optimize vertical tail size or shape."),
    ("Cl_beta", Cl_beta < 0 and np.abs(Cl_beta) > 0.01, "Roll stability in sideslip - Dihedral Effect.", "Roll instability in sideslip.\nPotential Reason: Aerodynamic design does not promote roll stability.\nPotential Fix: Adjust wing geometry effecting dihedral like sweep and dihedral angle."),
    ("Cl_p", Cl_p < 0 and np.abs(Cl_p) > 0.01, "Positive roll damping.", "Negative or no roll damping.\nPotential Reason: Aerodynamic design does not promote roll damping.\nPotential Fix: Adjust wing geometry effecting dihedral like sweep and dihedral angle."),
    ("Cl_r", Cl_r > 0 and np.abs(Cl_r) > 0.01, "Yaw rate induces roll in the correct direction.", "Yaw rate induces roll in the incorrect direction.\nPotential Reason: Vertical tail and fuselage aerodynamics are misaligned.\nPotential Fix: Optimize vertical tail design and placement."),
    ("Cn_beta", Cn_beta > 0 and np.abs(Cn_beta) > 0.01, "Positive directional stability.", "Negative or no directional stability.\nPotential Reason: CG could be behind the vertical tail.\nPotential Fix: Check CG location and vertical tail placement."),
    ("Cn_p", Cn_p > 0 and np.abs(Cn_p) > 0.01, "Adverse yaw damping present.", "Lack of adverse yaw damping.\nPotential Reason: Wing aerodynamics not contributing to yaw damping.\nPotential Fix: Review and adjust wing design for better yaw damping."),
    ("Cn_r", Cn_r < 0 and np.abs(Cn_r) > 0.01, "Positive yaw damping.", "Negative or no yaw damping.\nPotential Reason: CG could be behind the vertical tail.\nPotential Fix: Check CG location and vertical tail placement."),
    
    # Dynamic Stability
    ("\n\nDYNAMIC STABILITY",m>0," # SECTION HEADING - If time period of any mode is -1, it means mode is overdamped with zeta >= 1 or < 0.",""),
    #("If time period of any mode is -1, it means mode is overdamped with zeta > 1."),
    ("\nShort period mode", zeta_sp > 0, f"Short period mode is convergent with time period: {T_sp} s and damping factor {zeta_sp}", f"Short period mode is divergent, zeta_sp={zeta_sp}."),
    ("Phugoid mode", zeta_ph > 0, f"Phugoid mode is convergent with time period: {T_ph} s and damping factor {zeta_ph}", f"Phugoid mode is divergent, zeta_ph={zeta_ph}."),
    ("Dutch Roll mode", zeta_dr > 0, f"Dutch Roll mode is convergent with time period: {T_dr} s and damping factor {zeta_dr}", f"Dutch Roll mode is divergent, zeta_dr{zeta_dr}."),
    ("Roll mode", lambda_roll < 0, f"Roll mode is convergent with characteristic time: {roll_time_constant} s", "Roll mode is divergent."),
    ("Pure yaw mode", N_beta > 0, f"Pure yaw mode is convergent with characteristic time: {T_yw} s", f"Pure yaw mode is divergent, zeta_yw={zeta_yw}."),
    ("Spiral mode", lambda_spiral < 0, f"Spiral mode is convergent", "Spiral mode is divergent."),

    # Control Derivatives
    ("\n\nCONTROL DERIVATIVES",m>0,"# SECTION HEADING",""), 
    ("\nCz_dm", Cz_dm > 0 and abs(Cz_dm) > 0.01, "Elevator effective in producing correct vertical force.", "Elevator produces opposite vertical force.\nPotential Reason: CG could be behind the elevator.\nPotential Fix: Check CG position. Check THS/elevator airfoil."),
    ("Cm_dm", Cm_dm < 0 and abs(Cm_dm) > 0.01, "Elevator deflection produces correct pitch response.", "Elevator deflection produces opposite pitch response.\nPotential Reason: CG could be behind the elevator.\nPotential Fix: Check CG position."),
    ("Cy_dl", np.abs(Cy_dl) < 0.01, "Ailerons produce minimal side force.", "|Cy_dl| >= 0.01. Ailerons produce non-negligible side force.\nPotential Reason: Location or size of ailerons.\nPotential Fix: Control surface design."),
    ("Cy_dn", Cy_dn > 0 and abs(Cy_dn) > 0.01, "Rudder deflection produces correct side force.", "Rudder deflection produces opposite side force.\nPotential Reason: Rudder size or effectiveness is insufficient.\nPotential Fix: Enhance rudder design or placement."),
    ("Cl_dl", Cl_dl < 0 and abs(Cl_dl) > 0.01, "Aileron deflection produces correct roll response.", "Aileron deflection produces opposite roll response.\nPotential Reason: Location or size of ailerons.\nPotential Fix: Check aileron design."),
    ("Cl_dn", Cl_dn > 0 and abs(Cl_dn) > 0.01, "Rudder effective in inducing roll moment.", "Rudder ineffective in inducing roll moment.\nPotential Reason: Rudder and aileron interplay is not optimized.\nPotential Fix: Review rudder-aileron effectiveness and adjust accordingly."),
    ("Cn_dl", np.abs(Cn_dl) < 0.01, "Ailerons produce minimal yawing moment.", "|Cn_dl| >= 0.01. Ailerons produce non-negligible yawing moment.\nPotential Reason: Location or size of ailerons.\nPotential Fix: Check aileron design."),
    ("Cn_dn", Cn_dn < 0 and abs(Cn_dn) > 0.01, "Rudder deflection produces correct yaw response.", "Rudder deflection produces opposite yaw response.\nPotential Reason: CG could be behind the vertical tail.\nPotential Fix: Check CG location and vertical tail placement.")
    ]

    filetxt = input_file.replace("DegenGeom.stab","POST_CHECKS.txt")
    # Open a new file to write the output
    with open(filetxt, "w") as file:
        # Write the header row
        file.write(f"{input_file}\n")
        file.write("Parameter\tCheck Result\tDetails\n")
        
        # Iterate through each check
        for check in checks:
            param, condition, pass_msg, fail_msg = check
            # Determine if the check passed or failed and format the message accordingly
            if condition:
                details = pass_msg
            else:
                details = fail_msg
            
            # Format the line with proper tab spacing and new lines
            details_cleaned = details.replace('\n', ' ').replace('\r', ' ')
            line = f"{param}\t{'Passed' if condition else 'Failed'}\t{details_cleaned}\n"

            
            # Write the line to the file
            file.write(line)

print("VSP_Post - Running")

current_wd = os.getcwd()

vsp_run_dir = sys.argv[1]
input_param = sys.argv[2]
vspmodel_name = sys.argv[3]
global_vsp_run_dir = os.path.join(current_wd,vsp_run_dir)

os.chdir(global_vsp_run_dir)


mass_file = f"{vspmodel_name}_MassProps.txt"    
stab_file = f"{vspmodel_name}_DegenGeom.stab"        
outputtxt = f"{vspmodel_name}_POST_Stability"
post_process(mass_file,stab_file,input_param,outputtxt)


os.chdir(current_wd)

print("VSP_Post - Ended")