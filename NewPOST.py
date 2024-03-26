import numpy as np

# Constants
g = 9.81
Mach = 0.8
rho = 0.41
u = 236
q = 0.5*rho*u*u
b = 36
c = 9.68
S = 276
m = 77743.345222
Iyy = 1338902.900300  # FROM MASS FILE
Ixx = 1797233.804828  # FROM MASS FILE
Izz = 3070922.548940  # FROM MASS FILE

# Longitudinal derivatives
Cz_alpha = float(values[19])
Cz_q = float(values[25])
Cm_alpha = float(values[61])
Cm_q = float(values[67])
CL = float(values[55])
CL_alpha = float(values[53])
CD = float(values[49])
CL_u = float(values[59])
CD_u = float(values[47])

# Lateral-Directional derivatives
Cy_beta = float(values[14])
Cy_p = float(values[16])
Cy_r = float(values[18])
Cl_beta = float(values[37])
Cl_p = float(values[39])
Cl_r = float(values[41])
Cn_beta = float(values[55])
Cn_p = float(values[57])
Cn_r = float(values[59])

# Output the extracted values
print("Longitudinal derivatives:")
print(f"Cz_alpha = {Cz_alpha}")
print(f"Cz_q = {Cz_q}")
print(f"Cm_alpha = {Cm_alpha}")
print(f"Cm_q = {Cm_q}")
print(f"CL = {CL}")
print(f"CL_alpha = {CL_alpha}")
print(f"CD = {CD}")
print(f"CL_u = {CL_u}")
print(f"CD_u = {CD_u}")

print("\nLateral-Directional derivatives:")
print(f"Cy_beta = {Cy_beta}")
print(f"Cy_p = {Cy_p}")
print(f"Cy_r = {Cy_r}")
print(f"Cl_beta = {Cl_beta}")
print(f"Cl_p = {Cl_p}")
print(f"Cl_r = {Cl_r}")
print(f"Cn_beta = {Cn_beta}")
print(f"Cn_p = {Cn_p}")
print(f"Cn_r = {Cn_r}")

# Phugoid mode response 
Xu = -(q*S/(m*u)) * (2*CD + CD_u)
Zu = -(q*S/(m*u)) * (2*CL + CL_u)
omega_ph = np.sqrt((-g * Zu) / u)
zeta_ph = -Xu / (2 * omega_ph)
T_ph = 2 * np.pi / omega_ph
 
# Short Period response
Z_alpha = -(q*S/m) * CL_alpha
M_alpha = (q*S*b*c/Iyy) * Cm_alpha
M_alphad = (q*S*b*(c**2)/(2*u*Iyy)) * 4 # Approximately the same
M_q = (q*S*b*(c**2)/(2*u*Iyy)) * Cm_q
omega_sp = np.sqrt(max(0, (Z_alpha * M_q / u) - M_alpha))  # Ensure expression inside sqrt is non-negative
if omega_sp == 0:  # If omega_sp is zero, set zeta_sp to -1 and skip calculation of T
    zeta_sp = -1
    T_sp = None
else:
    zeta_sp = -(M_q + M_alphad + (Z_alpha / u)) / (2 * omega_sp)
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
zeta_yw = -N_r / np.sqrt(N_beta)
T_yw = 2 * np.pi / omega_yw


# Open a new text file for writing
with open('aerodynamic_checks.txt', 'w') as file:
    # Write the header row
    file.write("Parameter\tCheck Passed\tComments\n")

    # Longitudinal Derivatives Checks
    checks = [
        ("Cz_alpha", Cz_alpha > 0 and np.abs(Cz_alpha) > 0.01, "Positive force gradient on increasing alpha", "Vertically downward force when alpha increases\nPotential Reason: Lift coefficient negative.\nPotential Fix: Check airfoil."),
        ("Cz_q", Cz_q > 0 and np.abs(Cz_q) > 0.01, "Pitch up rotation increases alpha and thus, upward force.", "Upward pitch rate produces downward force\nPotential Reason: Lift coefficient gradient is negative.\nPotential Fix: Check airfoil."),
        ("Cm_alpha", Cm_alpha < 0 and np.abs(Cm_alpha) > 0.01, "Positive damping in pitch due to alpha.", "Increasing alpha increases pitching moment.\nPotential Reason: Neutral point is ahead of the CG.\nPotential Fix: Check CG position."),
        ("Cm_q", Cm_q < 0 and np.abs(Cm_q) > 0.01, "Positive pitch damping.", "Negative pitch damping.\nPotential Reason: Neutral point is ahead of the CG.\nPotential Fix: Check CG position."),
        
        # Lateral-directional derivatives checks
        ("Cy_beta", Cy_beta < 0 and np.abs(Cy_beta) > 0.01, "Correct sideforce produced in sideslip.", "Incorrect sideforce produced in sideslip.\nPotential Reason: CG could be behind the vertical tail.\nPotential Fix: Check CG location and vertical tail placement."),
        ("Cy_p", np.abs(Cy_p) < 0.01, "Neutral stability in sideforce due to roll rate.", "Excessive sideforce due to roll rate.\nPotential Reason: Wing parameters like sweep and dihedral might be sub-optimal.\nPotential Fix: Adjust wing geometry."),
        ("Cy_r", Cy_r > 0 and np.abs(Cy_r) > 0.01, "Positive yaw damping.", "Negative yaw damping.\nPotential Reason: Inadequate vertical tail design.\nPotential Fix: Optimize vertical tail size or shape."),
        ("Cl_beta", Cl_beta < 0 and np.abs(Cl_beta) > 0.01, "Roll stability in sideslip - Dihedral Effect.", "Roll instability in sideslip.\nPotential Reason: Aerodynamic design does not promote roll stability.\nPotential Fix: Adjust wing geometry effecting dihedral like sweep and dihedral angle."),
        ("Cl_p", Cl_p < 0 and np.abs(Cl_p) > 0.01, "Positive roll damping.", "Negative or no roll damping.\nPotential Reason: Aerodynamic design does not promote roll damping.\nPotential Fix: Adjust wing geometry effecting dihedral like sweep and dihedral angle."),
        ("Cl_r", Cl_r > 0 and np.abs(Cl_r) > 0.01, "Yaw rate induces roll in the correct direction.", "Yaw rate induces roll in the incorrect direction.\nPotential Reason: Vertical tail and fuselage aerodynamics are misaligned.\nPotential Fix: Optimize vertical tail design and placement."),
        ("Cn_beta", Cn_beta > 0 and np.abs(Cn_beta) > 0.01, "Positive directional stability.", "Negative or no directional stability.\nPotential Reason: CG could be behind the vertical tail.\nPotential Fix: Check CG location and vertical tail placement."),
        ("Cn_p", Cn_p > 0 and np.abs(Cn_p) > 0.01, "Adverse yaw damping present.", "Lack of adverse yaw damping.\nPotential Reason: Wing aerodynamics not contributing to yaw damping.\nPotential Fix: Review and adjust wing design for better yaw damping."),
        ("Cn_r", Cn_r > 0 and np.abs(Cn_r) > 0.01, "Positive yaw damping.", "Negative or no yaw damping.\nPotential Reason: CG could be behind the vertical tail.\nPotential Fix: Check CG location and vertical tail placement."),
        
        # Dynamic Stability
        ("Short period mode", zeta_sp > 0, f"Short period mode is convergent with time period: {T_sp} s and damping factor {zeta_sp}", "Short period mode is divergent."),
        ("Phugoid mode", zeta_ph > 0, f"Phugoid mode is convergent with time period: {T_ph} s and damping factor {zeta_ph}", "Phugoid mode is divergent."),
        ("Dutch Roll mode", zeta_dr > 0, f"Dutch Roll mode is convergent with time period: {T_dr} s and damping factor {zeta_dr}", "Dutch Roll mode is divergent."),
        ("Roll mode", lambda_roll < 0, f"Roll mode is convergent with characteristic time: {roll_time_constant} s", "Roll mode is divergent."),
        ("Pure yaw mode", N_beta > 0, f"Pure yaw mode is convergent with characteristic time: {T_yw} s", "Pure yaw mode is divergent.")
    ]


# Open a new file to write the output
with open("base.txt", "w") as file:
    # Write the header row
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