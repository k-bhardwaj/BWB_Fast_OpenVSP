import subprocess
import os
import all_func
import shutil

current_wd = os.getcwd()
python_fast = "E:/KSHITIJ/FastOAD/Fastenvk1/Scripts"
python_vsp = "D:/Anaconda/Directory/envs/vsppytools"

output_name = "output_Model.log"
error_name = "error_Model.log"
output_log = os.path.join(current_wd,output_name)
error_log = os.path.join(current_wd,error_name)

input_param = "parameters_RUNTEST.json"
input_param_path = os.path.join("Inputs",input_param)
testcase_name = os.path.splitext(os.path.basename(input_param_path))[0]

vsp_input = "BWB.vsp3"
vsp_input_path = os.path.join("Inputs",vsp_input)
VSP_model_name = os.path.splitext(os.path.basename(vsp_input_path))[0]

vsp_run_folder = f"{VSP_model_name}_{testcase_name}"
VSP_Folder = all_func.create_dir("VSP_RUNS")
vsp_run_dir = os.path.join(VSP_Folder,vsp_run_folder)
all_func.empty_out_dir(vsp_run_dir)
shutil.copy(input_param_path,vsp_run_dir)
shutil.copy(vsp_input_path,vsp_run_dir)

VSP_Run_Script = "VSP_Run_Script.py"
path_args = [vsp_run_dir, input_param, vsp_input]
print("VSP_Run- Running")
with open(output_log, "w") as f_out, open(error_log, "w") as f_err:
    subprocess.run([f"{python_vsp}/python", VSP_Run_Script] + path_args, shell=True,stdout=f_out, stderr=f_err)

VSP_Post_Script = "VSP_Post.py"
path_args = [vsp_run_dir, input_param, VSP_model_name]
print("VSP_Post- Running")
with open(output_log, "a") as f_out, open(error_log, "a") as f_err:
    subprocess.run([f"{python_vsp}/python", VSP_Post_Script] + path_args, shell=True,stdout=f_out, stderr=f_err)

