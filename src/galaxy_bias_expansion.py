import numpy as np
import os
import sys

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
    We use nearest-grid-point (NGP) assignment, i.e. displaced field is assigned to the nearest grid point.
    """
    n_grid = field.shape[0] # size of x axis (same as y and z)
    coords = np.indices((n_grid, n_grid, n_grid), dtype=float)
    displaced = coords + psi1  # shape (3, n, n, n)
    for i in range(3):
        displaced[i] = np.mod(displaced[i], n_grid)  # Periodic boundaries: mod(n) wraps around

    displaced_idx = np.floor(displaced).astype(int)   # NGP: nearest grid point
    displaced_idx = np.clip(displaced_idx, 0, n_grid - 1) #index can't go below 0 and above n_gri-1
    x, y, z = displaced_idx
    shifted_field = np.zeros_like(field)    # field of zeros
    shifted_field[x, y, z] += field # Eq. 17 integral (numerical summation)
    return shifted_field

def galaxy_bias_field(delta, box_size, b1=1.5, b2=0.5):
    """
    Construct δh(x) = b1 * δ̃1(x) + b2 * δ̃2(x)
    - δ̃1(x): shifted linear field
    - δ̃2(x): shifted version of (δ^2 - <δ^2>)
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

    # Shift fields from Lagrangian q to Eulerian x using ψ1
    delta_shifted = displace_field(delta, psi1)
    delta2_shifted = displace_field(delta_squared, psi1)

    # Equation (16): bias expansion in real space
    delta_h = b1 * delta_shifted + b2 * delta2_shifted
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
    b1, b2 = 1.5, 0.5   #adjustable bias parameters

    for filename in sorted(os.listdir(input_dir)):
        if filename.endswith(".npy"):
            z = extract_redshift(filename)
            if z is None:
                continue

            field_path = os.path.join(input_dir, filename)
            delta = np.load(field_path)

            print(f"Computing δ_h for z = {z} using shifted operators (Eq. 16)")

            delta_h = galaxy_bias_field(delta, box_size, b1, b2)

            base = os.path.splitext(filename)[0]
            output_file = os.path.join(output_dir, f"{base}_galaxy.npy")
            np.save(output_file, delta_h)

            print(f"Saved to {output_file}")

if __name__ == "__main__":
    main()