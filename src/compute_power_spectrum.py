import yaml                
import sys                 
import numpy as np         
from classy import Class   

def load_params(yaml_file):
    with open(yaml_file, 'r') as f:                 # read mode
        return yaml.safe_load(f)                    # parse into a Python dictionary

if __name__ == "__main__":                          # runs ONLY if this file is called directly
    if len(sys.argv) < 2:                           # sys.argv[0] is the script name, sys.argv[1] should be the YAML file
        print("Usage: python src/generate_mock_catalog.py config/planck_lcdm.yaml")
        sys.exit(1)                                 # exit if user didn’t provide a YAML file

    yaml_file = sys.argv[1]              
    params = load_params(yaml_file)      

    cosmo = Class()                                 # CLASS instance
    cosmo.set(params)                               # Set cosmological parameters from YAML
    cosmo.compute()                                 # CLASS calculations 

    ks = np.logspace(-3, 0, 256)
    pk = np.array([cosmo.pk(k, 0) for k in ks])     #compute P(k) at z=0 for each k

    np.savetxt("output/pk_planck_lcdm_z0.txt", np.column_stack([ks, pk]), 
               header="k [h/Mpc]    P(k) [(Mpc/h)^3]")

    print("Saved P(k) to output/pk_planck_lcdm_z0.txt")

    cosmo.struct_cleanup()                          # Free memory