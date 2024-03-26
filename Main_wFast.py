import subprocess
import os
import all_func
import shutil

current_wd = os.getcwd()
python_fast = "E:/KSHITIJ/FastOAD/Fastenvk1/Scripts"
python_vsp = "D:/Anaconda/Directory/envs/vsppytools"

fast_BWB_file = "FAST-OAD-BWB_Tutorial.py"
fast_BWB_folder = "FastBWB"
fast_output_file = "problem_outputs_BWB.xml"
fast_output_subfolder = "workspace"
input_param = "parameters_RUNTEST_FAST.json"
input_folder = "Inputs"
airfoil_file = "NACA63A012.af"

output_name = "output_FAST.log"
error_name = "error_FAST.log"
output_log = os.path.join(current_wd,output_name)
error_log = os.path.join(current_wd,error_name)

fast_BWB_path = os.path.join(fast_BWB_folder,fast_BWB_file)
fast_output_path = os.path.join(fast_BWB_folder,fast_output_subfolder,fast_output_file)

os.chdir(os.path.join(current_wd,fast_BWB_folder))
print("FAST-OAD - Running")
with open(output_log, "w") as f_out, open(error_log, "w") as f_err:
    subprocess.run([f"{python_fast}/python", fast_BWB_file], shell=True,stdout=f_out, stderr=f_err)
os.chdir(current_wd)
print("FAST-OAD - Ended")
shutil.copy(fast_output_path,input_folder)

input_xml_path = os.path.join(input_folder,fast_output_file)
airfoil_path = os.path.join(input_folder,airfoil_file)

input_param_path = os.path.join(input_folder,input_param)
testcase_name = os.path.splitext(os.path.basename(input_param_path))[0]

vsp_run_folder = f"{os.path.splitext(fast_BWB_file)[0]}_{testcase_name}"
VSP_Folder = all_func.create_dir("VSP_RUNS")
vsp_run_dir = os.path.join(VSP_Folder,vsp_run_folder)
all_func.empty_out_dir(vsp_run_dir)
shutil.copy(input_xml_path,vsp_run_dir)
shutil.copy(airfoil_path,vsp_run_dir)

VSP_Create_Script = "VSP_Create.py"
VSP_model_name = f"{os.path.splitext(fast_BWB_file)[0]}_{os.path.splitext(airfoil_file)[0]}"
path_args = [vsp_run_dir, fast_output_file, airfoil_file, VSP_model_name]
print("VSP_Create - Running")
with open(output_log, "a") as f_out, open(error_log, "a") as f_err:
    subprocess.run([f"{python_vsp}/python", VSP_Create_Script] + path_args, shell=True,stdout=f_out, stderr=f_err)

vsp_input = f"{VSP_model_name}.vsp3"
shutil.copy(input_param_path,vsp_run_dir)

VSP_Run_Script = "VSP_Run_Script.py"
path_args = [vsp_run_dir, input_param, vsp_input]
print("VSP_Run - Running")
with open(output_log, "a") as f_out, open(error_log, "a") as f_err:
    subprocess.run([f"{python_vsp}/python", VSP_Run_Script] + path_args, shell=True,stdout=f_out, stderr=f_err)

VSP_Post_Script = "VSP_Post.py"
path_args = [vsp_run_dir, input_param, VSP_model_name]
print("VSP_Post - Running")
with open(output_log, "a") as f_out, open(error_log, "a") as f_err:
    subprocess.run([f"{python_vsp}/python", VSP_Post_Script] + path_args, shell=True,stdout=f_out, stderr=f_err)
