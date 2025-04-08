import yaml
import sys
import numpy as np
from classy import Class
import os

def load_params(yaml_file):
    with open(yaml_file, 'r') as f: # read mode
        return yaml.safe_load(f)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python src/compute_power_spectrum.py config/[model].yaml")
        sys.exit(1)

    yaml_file = sys.argv[1]
    params = load_params(yaml_file)

    redshifts = params.get("z_pk", [0]) # default to [0] if z_pk isn't defined
    if isinstance(redshifts, list):
        params["z_pk"] = ' '.join(str(z) for z in redshifts)

    cosmo = Class() # CLASS instance
    cosmo.set(params)   # Set cosmological parameters 
    cosmo.compute() # CLASS calculations 

    ks = np.logspace(-3, 0, 256)
    base_name = os.path.splitext(os.path.basename(yaml_file))[0]
    output_subdir = os.path.join("output", base_name)
    os.makedirs(output_subdir, exist_ok=True)

    for z in redshifts: #compute P(k) at z for each k
        pk_z = np.array([cosmo.pk(k, float(z)) for k in ks])
        output_txt = os.path.join(output_subdir, f"pk_{base_name}_z{z}.txt")
        np.savetxt(output_txt, np.column_stack([ks, pk_z]), header="k [h/Mpc]    P(k) [(Mpc/h)^3]")
        print(f"Saved P(k) to {output_txt}")

    cosmo.struct_cleanup()  # Free memory