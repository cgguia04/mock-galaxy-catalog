
import numpy as np
import os
import sys
from scipy.interpolate import interp1d

def generate_gaussian_field(pk_file, box_size=1000.0, n_grid=256): #Box size in Mpc/h; 128^3 grid points
    data = np.loadtxt(pk_file)  # Load P(k)
    k_vals, pk_vals = data[:, 0], data[:, 1]

    # Interpolation: don't crash outside k_vals range but assume P(k)=0
    pk_interp = interp1d(k_vals, pk_vals, bounds_error=False, fill_value=0) 
    kf = 2 * np.pi / box_size   #fundamental mode (smallest k, longest wavelength)

    # FFT: transform from density at each point to Fourier space
    grid = np.fft.fftfreq(n_grid, d=1.0 / n_grid) * kf  #1d array of Fourier mode indices; correct scaling with d=1.0
    kx, ky, kz = np.meshgrid(grid, grid, grid, indexing='ij')  #assign kx,ky,kz to each grid point
    k_mag = np.sqrt(kx**2 + ky**2 + kz**2)

    # Assuming Gaussian perturbations at early times
    random_real = np.random.normal(0, 1, (n_grid, n_grid, n_grid))
    random_imag = np.random.normal(0, 1, (n_grid, n_grid, n_grid))
    noise = random_real + 1j * random_imag  #δ(k) = A(k) + iB(k)

    # Recall P(k) = ⟨∣δ(k)∣²⟩ = ⟨A²⟩ + ⟨B²⟩ = 2σ²
    amplitude = np.sqrt(pk_interp(k_mag) / 2.0)
    field_k = noise * amplitude #correctly scaled noise
    
    field_k[0, 0, 0] = 0.0  # Set zero mode to 0 (remove biased background)
    field_real = np.fft.ifftn(field_k).real # Inverse FFT to get real-space field

    return field_real

def main():
    if len(sys.argv) < 2:
        print("Usage: python src/generate_gaussian_field.py output/[model_folder]")
        sys.exit(1)

    folder = sys.argv[1]
    if not os.path.isdir(folder):
        print(f"Directory not found: {folder}")
        sys.exit(1)

    # Define the output folder for Gaussian fields
    parent_folder = os.path.dirname(folder)
    gaussian_field_dir = os.path.join(parent_folder, "gaussian_field")
    os.makedirs(gaussian_field_dir, exist_ok=True)

    # Loop through .txt files inside the folder called
    for filename in sorted(os.listdir(folder)):
        if filename.endswith(".txt"):
            pk_path = os.path.join(folder, filename)
            base_name = os.path.splitext(filename)[0]
            npy_path = os.path.join(gaussian_field_dir, f"{base_name}.npy")

            print(f"Generating Gaussian field from: {filename}")
            field = generate_gaussian_field(pk_path)
            np.save(npy_path, field)
            print(f"Saved field to: {npy_path}")


if __name__ == "__main__":
    main()
