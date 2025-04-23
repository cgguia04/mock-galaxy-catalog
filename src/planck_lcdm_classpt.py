from classy import Class
import numpy as np
import matplotlib.pyplot as plt
import os
import sys
import matplotlib.cm as cm
import matplotlib.colors as mcolors

z_vals = ["0", "0.5", "1", "2", "3"]
full_cmap = cm.get_cmap("OrRd")
sliced_cmap = [full_cmap(i) for i in np.linspace(0.4, 1.0, len(z_vals))]
colormap = cm.get_cmap("OrRd", len(z_vals)) 
z_colors = {z: sliced_cmap[i] for i, z in enumerate(z_vals)}

# Extract model name from the script name
script_name = os.path.basename(sys.argv[0])
model_name = script_name.replace("_classpt.py", "")
outdir = os.path.join("output", model_name, "classpt")
output_filename = f"pk_{script_name}.png"

# Make sure the directory exists
os.makedirs(outdir, exist_ok=True)

# Redshifts to compute
z_vals = [0, 0.5, 1, 2, 3]
k = np.logspace(-3, 0, 200)

# Bias parameters
b1, b2, bG2, bGamma3 = 1.2, -0.405, -0.127, 0.0
cs0 = cs2 = cs4 = b4 = 0.0
Pshot = 1000.0

plt.figure(figsize=(8, 6))

for z in z_vals:
# Define cosmology
    cosmo = Class()
    cosmo.set({
        'A_s': 2.0989e-9,
        'n_s': 0.9649,
        'tau_reio': 0.0544,
        'omega_b': 0.02237,
        'omega_cdm': 0.12,
        'h': 0.6736,
        'output': 'mPk',
        'non linear': 'PT', #Perturbation Theory
        'IR resummation': 'No',
        'Bias tracers': 'Yes',  #Bias expansion
        'cb': 'Yes',    #CDM and baryons
        'AP': 'No', #Using fiducial cosmology
        'P_k_max_h/Mpc': 10,
        'z_pk': f'{z}',
    })
    cosmo.compute()
    cosmo.initialize_output(k, z, len(k))
    Pk_gg = cosmo.pk_gg_l0(b1, b2, bG2, bGamma3, cs0, Pshot, b4)
    
    # Save power spectrum as .txt
    fname_txt = os.path.join(outdir, f"pk_{model_name}_z{z}.txt")
    np.savetxt(fname_txt, np.column_stack((k, Pk_gg)), header="k [h/Mpc]   P(k) [(Mpc/h)^3]")
    print(f"Saved {fname_txt}")

    color = z_colors.get(str(z), "black")  # fallback is black
    plt.loglog(k, Pk_gg, label=f"z = {z}", color=color, linewidth=2)
    cosmo.struct_cleanup()
    cosmo.empty()

plt.rcParams.update({
    "text.usetex": True,  
    "font.family": "serif",
    "font.size": 14,
    "axes.labelsize": 16,
    "axes.titlesize": 17,
    "legend.fontsize": 13,
    "xtick.labelsize": 13,
    "ytick.labelsize": 13,
    "lines.linewidth": 2,
    })

plt.xlabel(r"$k \, [h/\mathrm{Mpc}]$")
plt.ylabel(r"$P_{gg}(k) \, [(\mathrm{Mpc}/h)^3]$")
plt.title("Galaxy Power Spectrum from CLASS-PT")
plt.grid(True, which="both", linestyle="--", linewidth=0.5, alpha=0.7)
plt.tight_layout(pad=1.5)
plt.legend()

# Save figure using script name
plot_path = os.path.join(outdir, f"pk_{model_name}_classpt.png")
plt.savefig(plot_path)
print(f"Saved plot to {plot_path}")