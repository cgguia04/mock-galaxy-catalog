import numpy as np
import os
import sys
from scipy.interpolate import RegularGridInterpolator

# Reference: Schmittfull et al. (2019)
def extract_redshift(filename):
    try:
        base = os.path.splitext(filename)[0]
        parts = base.split("_z")
        z_str = parts[-1].split("_")[0]
        return float(z_str)
    except:
        return None

def compute_psi1(delta_k, box_size, n_grid):    
    # Integrand of Eq (14): ψ1(k) = i k / k^2 δ1(k) 

    kf = 2 * np.pi / box_size
    k = np.fft.fftfreq(n_grid, d=1.0 / n_grid) * kf
    kx, ky, kz = np.meshgrid(k, k, k, indexing='ij')
    k_squared = kx**2 + ky**2 + kz**2
    k_squared[0, 0, 0] = 1  # avoid division by zero

    factor = 1j * np.stack([kx, ky, kz]) / k_squared # 4D array or 3D vector field
    psi_k = factor * delta_k[np.newaxis, :, :, :]  # shape (3, n, n, n)
    return psi_k  

def displace_field(field, psi1):
    """
    Displace a Lagrangian field O(q) to Eulerian space (where galaxies are observed):
    Implements the shifted operator (Eq. 17)
    Õ(x) where x = q + ψ1(q) (Eq. 16)
    Uses cloud-in-cell (CIC) interpolation for higher accuracy.
    """
    n_grid = field.shape[0] # size of x axis (same as y and z)
    grid = np.arange(n_grid)

    interpolator = RegularGridInterpolator((grid, grid, grid), field, bounds_error=False, fill_value=0)
    coords = np.indices((n_grid, n_grid, n_grid), dtype=float)  # shape (3, n, n, n)
    displaced = coords + psi1  # shape (3, n, n, n)
    for i in range(3):
        displaced[i] = np.mod(displaced[i], n_grid)  # Periodic boundaries: mod(n) wraps around

    points = np.stack([displaced[0].ravel(), displaced[1].ravel(), displaced[2].ravel()], axis=-1)  # shape (n^3, 3)
    values = interpolator(points).reshape((n_grid, n_grid, n_grid)) #gives O(x) and reshapes to 3D grid
    return values

def galaxy_bias_field(delta, box_size, b1, b2, bG2, n_bar):
    """
    Construct δh(x) = b1 * δ̃1(x) + b2 * δ̃2(x) + bG2 * G̃2(x) + ε(x)
    - δ̃1(x): shifted linear field
    - δ̃2(x): shifted version of (δ^2 - <δ^2>)
    - G̃2(x): shifted version of the tidal operator
    - ε(x): shot noise
    Based on Equation (16)
    """
    n_grid = delta.shape[0]

    # FFT and compute δ1(k)
    delta_k = np.fft.fftn(delta, norm="forward")
    
    # Equation (14): Zel’dovich displacement ψ1(q)
    psi_k = compute_psi1(delta_k, box_size, n_grid)
    psi1 = np.fft.ifftn(psi_k, axes=(1,2,3)).real  # shape (3, n, n, n)

    # Bias operators in Lagrangian space
    delta_squared = delta**2
    delta_squared -= np.mean(delta_squared) # Eq. 8 and 9 

    # Tidal operator G2
    kf = 2 * np.pi / box_size   
    k = np.fft.fftfreq(n_grid, d=1.0 / n_grid) * kf
    kx, ky, kz = np.meshgrid(k, k, k, indexing='ij')
    k_squared = kx**2 + ky**2 + kz**2
    k_squared[0, 0, 0] = 1

    # Poisson equation implicit in Eq. 10: ∇^2 φ(q) = δ(q)
    phi_k = -delta_k / k_squared    # gravitational potential
    phi = np.fft.ifftn(phi_k).real  # Inverse FFT to real space

    tidal_tensor = {} # Nested loop to define all tensor components
    for i, ki in enumerate([kx, ky, kz]):
        for j, kj in enumerate([kx, ky, kz]):
            Tij_k = -(ki * kj * phi_k) # second derivative in Fourier space w.r.t i, j
            Tij_x = np.fft.ifftn(Tij_k).real    # converts to real space
            tidal_tensor[(i, j)] = Tij_x    # stores in dictionary

    laplacian_phi = np.fft.ifftn(-k_squared * phi_k).real   # Trace of tidal tensor
    trace_squared = laplacian_phi**2    # Second term of Eq. 10
    tidal_squared = sum(tidal_tensor[(i, j)]**2 for i in range(3) for j in range(3))   #First term of Eq. 10
    G2 = tidal_squared - trace_squared  # Eq. 10
    G2 -= np.mean(G2)   # Theoretically, G2 has zero mean already at large scales (Footnote 3)

    # Shift fields from Lagrangian q to Eulerian x using ψ1
    delta_shifted = displace_field(delta, psi1)
    delta2_shifted = displace_field(delta_squared, psi1)
    G2_shifted = displace_field(G2, psi1)

    # Equation (16): bias expansion in real space
    delta_h = b1 * delta_shifted + b2 * delta2_shifted + bG2 * G2_shifted

    # Add shot noise term ε(x) ~ N(0, 1/n̄) if specified
    if n_bar is not None:
        volume = box_size**3
        voxel_volume = volume / n_grid**3
        noise_std = np.sqrt(1 / (n_bar * voxel_volume))  # Gaussian std per voxel
        epsilon = np.random.normal(loc=0.0, scale=noise_std, size=delta.shape)  # scale such that P(k) is 1/n_bar; 3d grid.
        delta_h += epsilon  # stochastic component

    return delta_h

def main():
    if len(sys.argv) < 2:
        print("Usage: python src/galaxy_bias_expansion.py output/[model]/gaussian_field")
        sys.exit(1)

    input_dir = sys.argv[1]
    if not os.path.isdir(input_dir):
        print(f"Directory not found: {input_dir}")
        sys.exit(1)

    model_dir = os.path.dirname(input_dir)
    output_dir = os.path.join(model_dir, "galaxy_field")
    os.makedirs(output_dir, exist_ok=True)

    box_size = 500.0
    b1, b2, bG2 = 1.5, 0.5, 0.5   #adjustable bias parameters
    n_bar = None

    for filename in sorted(os.listdir(input_dir)):
        if filename.endswith(".npy"):
            z = extract_redshift(filename)
            if z is None:
                continue

            field_path = os.path.join(input_dir, filename)
            delta = np.load(field_path)

            print(f"Computing δ_h for z = {z} using shifted operators (Eq. 16)")

            delta_h = galaxy_bias_field(delta, box_size, b1, b2, bG2, n_bar=n_bar)

            base = os.path.splitext(filename)[0]
            output_file = os.path.join(output_dir, f"{base}_galaxy.npy")
            np.save(output_file, delta_h)

            print(f"Saved to {output_file}")

if __name__ == "__main__":
    main()