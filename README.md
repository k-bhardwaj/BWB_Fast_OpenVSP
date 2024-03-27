**Project Overview**  
This project encompasses the development of a stability assessment tool and framework integrated in-line with FAST-OAD, a rapid Overall Aircraft Design Tool, using OpenVSP, a parametric aircraft geometry tool. The primary focus lies in conducting a comprehensive analysis of static and dynamic stability characteristics for Blended Wing Body (BWB) aircraft to aid in rapid design.

**Contributors - Kshitij Bhardwaj and Nagaraj Ganesh Prabhu**  
Note: The "FastBWB" folder included in this repository and its contents were developed by Sandra Muñoz San José, Justo Antonio Rodríguez, and Miguel Valadas of ISAE-SUPAERO during a previous project. Their script was directly used as an input to Main_wFast.py.

**Description**  
FAST-OAD offers multi-disciplinary analysis and optimization capabilities, leveraging the OpenMDAO framework. It allows seamless switching between models within the same discipline and facilitates addition, removal, or development of models to align with specific study requirements.

OpenVSP serves as the parametric aircraft geometry tool, enabling the creation of 3D aircraft models based on standard engineering parameters. These models are then processed into formats suitable for engineering analysis. It offers numerous benefits with regards to stability analyses.

**Integration Process**  
The integration involves employing OpenVSP through its Python API to analyze the static and dynamic stability of BWB aircraft. Validation tests were conducted using the Swept_Wing_API example to ensure consistency between results obtained via the API and the OpenVSP GUI. 

**Tool Structure**  
The tool's architecture is organized into several functional scripts:

>**Main Scripts:**  
>Main_wFast.py: Integrates with FastOAD environment to execute BWB script within FastOAD, facilitating seamless analysis.  
>Main_wModel.py: Operates without FastOAD integration, directly performing OpenVSP analysis.  

>**Additional Scripts:**  
>VSP_Create.py: Generates .vsp3 file from FastOAD outputs (used with Main_wFast.py).  
>VSP_Run_Script.py: Executes analysis based on .vsp3 file and parameters.json (common to both main scripts).  
>VSP_Post.py: Processes derivatives from previous analysis, conducts various checks, and generates output text files (common to both main scripts).  

**Prerequisites**    
Ensure the following prerequisites are met before running the tool:  
>Install OpenVSP API (VSP VERSION - OpenVSP-3.36.0-win64-Python3.9).  
>Install FastOAD.  

**Usage Instructions**  
>Before running the code, ensure the following are correct:  
>**Main_wFast.py:**  
>>python_fast = "E:/.../Scripts"  #specify the path of the directory of the python executable with fastoad installed  
>>python_vsp = "D:/Anaconda/Directory/envs/vsppytools"  #specify the path of the directory of python the executable with openvsp api installed  
>>input_param = JSON parameters filename   
>>fast_BWB_file = "FAST-OAD-BWB_Tutorial.py" #Fast BWB executable  
>>fast_BWB_folder = "FastBWB"  
>>input_folder = "Inputs"  
>>fast_output_file = "problem_outputs_BWB.xml" # standard, output by fast, automatically copied to correct directory by code  
>>fast_output_subfolder = "workspace" # this folder is inside FastBWB folder  
>>airfoil_file = # airfoil file in .af format with extension - to be placed in the inputs folder.   

>**Main_wModel.py:**  
>>Before running the code, ensure the following are correct:  
>>python_fast = "E:/.../Scripts"  #specify the path of the directory of the python executable with fastoad installed  
>>python_vsp = "D:/Anaconda/Directory/envs/vsppytools"  #specify the path of the directory of python the executable with openvsp api installed  
>>input_param = .JSON parameters filename with extension  
>>vsp_input = .vsp3 model filename with extension  

>**Parameters File**  
>Modify parameters in the parameters.json file, accounting for value types, while ensuring automatic updates based on calculations in VSP_Run_Script.py. Rest of the parameters should automatically be updated based on calculations in the VSP_Run_Script.py script, and the inertial values are pulled from the mass analysis executed just before this step in the same script. Then a new UPDATED parameter file with the same name is stored in the VSP_RUNS/(Run_Specific_Directory). The original parameters file in the inputs folder stays unmodified.   
>>**Parameters to be modified:**  
>>>  "analysis_method": "VORTEX_LATTICE" *note: will usually stay the same  
>>>    "stability_type": "STABILITY_DEFAULT" *note: will usually stay the same  
>>>    "RefFlag" *note: Important to pull geometry parameters from the model  
>>>    "CGGeomSet" *note: will usually stay the same  
>>>    "GeomSet" *note: will usually stay the same  
>>>    "cruise_aoa"  
>>>    "altitude"  
>>>    "Alpha_Start"  
>>>    "Alpha_End"  
>>>    "AlphaNpts"  
>>>    "Beta_Start"  
>>>    "BetaNpts"  
>>>    "Mach_Start"  
>>>    "MachNpts"  
>>>    "ReCrefNpts"  
>>>    "KTCorrection" *note: will usually stay the same  

>**Note** :Output files and errors are logged in the base directory. For each run, files are saved in the automatically created VSP_RUNS folder. Ensure modifications in input file names to retain old results if necessary.  

Refer to the official documentation for further details on FAST-OAD and OpenVSP for installation of OpenVSP API and FastOAD.