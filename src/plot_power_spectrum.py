import numpy as np
import matplotlib.pyplot as plt
import sys
import os

def main():
    if len(sys.argv) < 2:
        print("Usage: python src/plot_power_spectrum.py output/pk_planck_lcdm_z0.txt")
        sys.exit(1)

    input_file = sys.argv[1]

    if not os.path.exists(input_file):
        print(f"File not found: {input_file}")
        sys.exit(1)

    k, pk = np.loadtxt(input_file, unpack=True)

    plt.figure(figsize=(8, 6))
    plt.loglog(k, pk)
    plt.xlabel(r"$k \, [h/\mathrm{Mpc}]$")
    plt.ylabel(r"$P(k) \, [(\mathrm{Mpc}/h)^3]$")
    plt.title("Matter Power Spectrum at $z = 0$")
    plt.grid(True)
    plt.tight_layout()

    output_plot = "output/" + os.path.basename(input_file).replace(".txt", ".png")
    plt.savefig(output_plot)
    print(f"Plot saved to {output_plot}")

    plt.show()

if __name__ == "__main__":
    main()
