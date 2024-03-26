#!/usr/bin/env python
# coding: utf-8

# <div class="row">
#   <div class="column">
#     <img src="./img/logo-ISAE_SUPAERO.png" width="200">
#   </div>
# </div>

# # [TUTORIAL] FAST-OAD with BWB integrated architecture
# #### Sandra MUÑOZ 
# #### Justo RODRÍGUEZ
# #### Miguel VALADAS
# 
# Latest update: 26 March 2023
# 
# ------------------
# 
# This objective of this notebook is to provide the user with a general overview of a typical run of FAST-OAD with BWB integrated architecture. In short, it imports the libraries, generates the inputs, evaluates the problem and shows the outputs list, as well as the XDSM and the N2 diagrams.
# 

# ## 1. Import libraries

# In[1]:


# Check if all packages are installed. If not, the program will automatically install the missing ones. 

import importlib.util
import sys
import subprocess
# Packages list
package_names = ['numpy', 'os.path','openmdao.api','logging','shutil','fastoad.api','math','matplotlib.pyplot','plotly.graph_objects','array','time','sys','pandas','qgrid','yaml']
num_packages = len(package_names)

# Function to install package
def install(package):
    #subprocess.check_call([sys.executable, '-m', 'pip', 'install', package])
    print("install commented out")
# Test libraries: 
for i in range(num_packages):
    spec = importlib.util.find_spec(package_names[i])
    if spec is None:
        print("-----------ERROR-----------: Package '" + package_names[i] +"'  is not installed.")
        # Install package: 
        install(package_names[i])
        print("-----------UPDATE-----------: Package '" + package_names[i] +"'  is now correctly installed.")
        
    else:
        print("Package '" + package_names[i] + "' is correctly installed.")
        
# Import packages once all of them are correctly installed: 
import openmdao.api as om
from fastoad.module_management.constants import ModelDomain
from fastoad.module_management.service_registry import RegisterOpenMDAOSystem, RegisterSubmodel
import logging
import shutil
import fastoad.api as oad
import os.path as pth
import os
import yaml
from ruamel.yaml import YAML
import matplotlib.pyplot as plt
from IPython.display import Javascript, display, Image, HTML
import numpy as np
import math
import plotly.graph_objects as go
import array
import time
import sys
import pandas as pd
import qgrid


# ## 2. Directory set up 

# In[2]:


# # Print the current working directory
directory = "{0}".format(os.getcwd())
print('Directory: ', directory)

# Assign data and work folder paths: 
DATA_FOLDER_PATH = "data"
WORK_FOLDER_PATH = "workspace"

# Print data and work folder paths: 
print('- Data folder path is: ',directory +'\data')
print('- Work folder path is: ',directory +'\workspace')


# ## 3. Initialization

# In[3]:


# For having log messages on screen
# logging.basicConfig(level=logging.INFO, format="%(levelname)-8s: %(message)s")

##################################################################################


# BWB CONFIFURATION: 
CONFIGURATION_FILE_BWB = pth.join(WORK_FOLDER_PATH, "BWB_configuration.yml")
SOURCE_FILE_BWB = pth.join(DATA_FOLDER_PATH, "BWB_inputs.xml")
# oad.generate_configuration_file(CONFIGURATION_FILE_tubeWing, overwrite=True)


print('Problem initialized correctly')


# ## 4. Generate inputs

# In[4]:


# Change inputs and outputs file names in the configuration file:
yaml = YAML()
yaml.preserve_quotes = True
with open(CONFIGURATION_FILE_BWB) as f:
    test = yaml.load(f)
test['input_file'] = './problem_inputs_BWB.xml'
test['output_file'] = './problem_outputs_BWB.xml'
with open(CONFIGURATION_FILE_BWB, 'wb') as f:
    yaml.dump(test, f)

# Generate inputs - default simulation:
inputsBWB = oad.generate_inputs(CONFIGURATION_FILE_BWB, SOURCE_FILE_BWB, overwrite=True)
print(' - BWB inputs directory is:\n', inputsBWB)

# Visualize list of inputs: 
oad.variable_viewer(inputsBWB)


# ## 5. Evaluate problem

# In[5]:


BWB_problem = oad.evaluate_problem(CONFIGURATION_FILE_BWB, overwrite=True)


# ## 6. Visualize output variables  

# In[6]:


oad.variable_viewer(pth.join(WORK_FOLDER_PATH, "problem_outputs_BWB.xml"))


# ## 7. Plot XDSM and N2 diagrams

# In[7]:


# XDSM FILE
XDSM_FILE = pth.join(WORK_FOLDER_PATH, 'xdsm.html')
oad.write_xdsm(CONFIGURATION_FILE_BWB, XDSM_FILE, overwrite=True)
from IPython.display import IFrame
IFrame(src=XDSM_FILE, width='100%', height='500px')


# In[8]:


# N2 FILE
N2_FILE = pth.join(WORK_FOLDER_PATH, "n2.html")
oad.write_n2(CONFIGURATION_FILE_BWB, N2_FILE, overwrite=True)
from IPython.display import IFrame
#ADD THE LINE BELOW, IT IS MISSING ON THE TEAMS VERSION
IFrame(src=N2_FILE, width='100%', height='500px')


# In[ ]:




