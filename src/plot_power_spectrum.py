import numpy as np
import matplotlib.pyplot as plt
import sys
import os

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

    for filename in sorted(os.listdir(input_dir)):
        if filename.endswith(".txt"):
            input_path = os.path.join(input_dir, filename)
            
            # Extract redshift from filename (pk_model_zZ.txt)
            try:
                k, pk = np.loadtxt(input_path, unpack=True)
            except Exception as e:
                print(f"⚠️ Skipping {filename}: {e}")
                continue

            z_part = filename.split("_z")[-1].replace(".txt", "")
            label = f"z = {z_part}"
            plt.loglog(k, pk, label=label)

    plt.xlabel(r"$k \, [h/\mathrm{Mpc}]$")
    plt.ylabel(r"$P(k) \, [(\mathrm{Mpc}/h)^3]$")
    plt.title("Matter Power Spectrum at Different Redshifts")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()

    # Save plot to output folder
    model_name = os.path.basename(input_dir)
    output_path = os.path.join(input_dir, f"pk_{model_name}_multi_z.png")
    plt.savefig(output_path)
    print(f"Combined plot saved to {output_path}")
    plt.show()

if __name__ == "__main__":
    main()
