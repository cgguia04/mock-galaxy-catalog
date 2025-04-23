import numpy as np
import matplotlib.pyplot as plt
import sys
import os
import matplotlib.cm as cm
import matplotlib.colors as mcolors

z_vals = ["0", "0.5", "1", "2", "3"]
full_cmap = cm.get_cmap("OrRd")
sliced_cmap = [full_cmap(i) for i in np.linspace(0.4, 1.0, len(z_vals))]
colormap = cm.get_cmap("OrRd", len(z_vals)) 
z_colors = {z: sliced_cmap[i] for i, z in enumerate(z_vals)}

def main():
    if len(sys.argv) < 2:
        print("Usage: python src/plot_power_spectrum.py output/[model_folder]")
        sys.exit(1)

    input_dir = sys.argv[1]
    if not os.path.isdir(input_dir):
        print(f"Directory not found: {input_dir}")
        sys.exit(1)

    # Initialize plot
    plt.figure(figsize=(10, 6))

    for idx, filename in enumerate(sorted(os.listdir(input_dir))):
        if filename.endswith(".txt"):
            input_path = os.path.join(input_dir, filename)
            
            # Extract redshift from filename (pk_model_zZ.txt)
            try:
                k, pk = np.loadtxt(input_path, unpack=True)
            except Exception as e:
                print(f"Skipping {filename}: {e}")
                continue

            z_part = filename.split("_z")[-1].replace(".txt", "")
            label = f"z = {z_part}"
            color = z_colors.get(z_part, "black")  # fallback is black
            plt.loglog(k, pk, label=label, color=color, linewidth=2)

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
    plt.ylabel(r"$P(k) \, [(\mathrm{Mpc}/h)^3]$")
    plt.title("Power Spectrum $P(k)$ Across Redshifts", pad=10)
    plt.legend()
    plt.grid(True, which="both", linestyle="--", linewidth=0.5, alpha=0.7)
    plt.tight_layout(pad=1.5)

    # Save plot to output folder
    model_name = os.path.basename(input_dir)
    output_path = os.path.join(input_dir, f"pk_{model_name}_multi_z.png")
    plt.savefig(output_path)
    print(f"Combined plot saved to {output_path}")
    plt.show()

if __name__ == "__main__":
    main()