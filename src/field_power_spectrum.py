import numpy as np
import os
import sys
import matplotlib.pyplot as plt
from scipy.stats import binned_statistic

def extract_redshift(filename):
    try:
        base = os.path.splitext(filename)[0]
        parts = base.split("_z")
        z_str = parts[-1].split("_")[0]
        return float(z_str)
    except:
        return None

def compute_power_spectrum(field, box_size):
    field_k = np.fft.fftn(field)    # real space to Fourier space: δ(k)
    power = np.abs(field_k)**2  # P(k) = |δ(k)|^2

    # k-grid
    n_grid = field.shape[0] 
    kf = 2 * np.pi / box_size  #Fundamental mode
    k = np.fft.fftfreq(n_grid, d=1.0 / n_grid) * kf
    kx, ky, kz = np.meshgrid(k, k, k, indexing='ij')
    k_mag = np.sqrt(kx**2 + ky**2 + kz**2).flatten() #turn into 1D array
    power = power.flatten()

    # Bin power spectrum by |k| to get P(k)
    # Mask out zero k
    k_mag_nonzero = k_mag[k_mag > 0]
    power_nonzero = power[k_mag > 0]

    # Define log-spaced bins safely

    '''
    Shannon Sampling Theorem: If a function f(t) contains no frequencies
    higher than W cps, it is completely determined by giving
    its ordinates at a series of points spaced 1/2W seconds
    apart.

    k_nyq = 2π / λ = 2π / (2 * Δx) where Δx = box_size / n_grid
    '''

    k_min = k_mag_nonzero.min()
    k_max = np.pi * n_grid / box_size  # Nyquist frequency
    k_bins = np.logspace(np.log10(k_min), np.log10(k_max), num=6)


    # Bin power spectrum by |k| to get P(k)
    Pk, bin_edges, _ = binned_statistic(k_mag_nonzero, power_nonzero, bins=k_bins, statistic='mean')
    k_centers = 0.5 * (bin_edges[:-1] + bin_edges[1:])
    valid = (Pk > 0) & (~np.isnan(Pk))

    return k_centers[valid], Pk[valid]

def main():
    if len(sys.argv) < 2:
        print("Usage: python src/field_power_spectrum.py output/[model]/gaussian_field")
        sys.exit(1)

    input_dir = sys.argv[1]
    if not os.path.isdir(input_dir):
        print(f"Directory not found: {input_dir}")
        sys.exit(1)

    box_size = 500.0    #like in generate_gaussian_field.py
    files_with_z = []
    for filename in os.listdir(input_dir):  #iterate over .npy files
        if filename.endswith(".npy"):
            z = extract_redshift(filename)
            if z is not None:
                files_with_z.append((z, filename))

    if not files_with_z:
        print("No suitable .npy files found.")
        sys.exit(1)

    files_with_z.sort()

    plt.figure(figsize=(10, 6))
    for z, filename in files_with_z:
        field = np.load(os.path.join(input_dir, filename))
        
        # Print mean and variance for this redshift
        print(f"z = {z:.2f}: Mean = {np.mean(field):.5f}, Variance = {np.var(field):.5f}")

        k_vals, pk_vals = compute_power_spectrum(field, box_size)
        plt.loglog(k_vals, pk_vals, label=f"z = {z}")

    plt.xlabel(r"$k \, [h/\mathrm{Mpc}]$")
    plt.ylabel(r"$P(k)$ (arbitrary units)")
    plt.title("Power Spectrum")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()

    # Save figure in the same directory
    output_path = os.path.join(input_dir, "field_power_spectrum.png")
    plt.savefig(output_path)
    print(f"Saved plot to: {output_path}")
    plt.close()

if __name__ == "__main__":
    main()
