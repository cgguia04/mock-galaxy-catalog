import numpy as np
import os
import sys
import matplotlib.pyplot as plt
from matplotlib import cm
from mpl_toolkits.axes_grid1 import make_axes_locatable

def extract_redshift(filename):
    try:
        # Assumes filename like pk_model_z0.npy or pk_model_z0_lognormal.npy
        base = os.path.splitext(filename)[0]
        parts = base.split("_z")
        z_str = parts[-1].split("_")[0] 
        return float(z_str)
    except:
        return None

def plot_field_slice(field):
    mid = field.shape[2] // 2   #midpoint of z axis
    return field[:, :, mid] #plots slize of xy plane at z=mid

def main():
    if len(sys.argv) < 2:
        print("Usage: python src/plot_field.py output/[model]/[field_type]/")
        sys.exit(1)

    input_dir = sys.argv[1]
    if not os.path.isdir(input_dir):
        print(f"Directory not found: {input_dir}")
        sys.exit(1)

    # Collect and sort all relevant .npy files by redshift
    files_with_z = []
    for filename in os.listdir(input_dir):
        if filename.endswith(".npy"):
            z = extract_redshift(filename)
            if z is not None:
                files_with_z.append((z, filename))

    if not files_with_z:
        print("No .npy field files with identifiable redshifts found.")
        sys.exit(1)

    files_with_z.sort()

    n_plots = len(files_with_z)
    n_cols = 3
    n_rows = (n_plots + n_cols - 1) // n_cols #floor operator to round up to nearest integer

    fig, axes = plt.subplots(n_rows, n_cols, figsize=(6 * n_cols, 5 * n_rows))
    axes = axes.flatten()

    all_slices = []
    for z, filename in files_with_z:
        field = np.load(os.path.join(input_dir, filename))
        slice_2d = plot_field_slice(field)
        all_slices.append(slice_2d)

    all_slices = np.array(all_slices)
    vmin, vmax = np.min(all_slices), np.max(all_slices)  # consistent color scale

    for i, (z,filename) in enumerate(files_with_z):
        im = axes[i].imshow(slice_2d, origin='lower', cmap='viridis', interpolation='none', vmin=vmin, vmax=vmax)
        axes[i].set_title(f"z = {z}", fontsize=12)
        axes[i].axis('off')

    # Create colorbar in last slot (axes[-1])
    divider = make_axes_locatable(axes[-1])
    cax = divider.append_axes("right", size="5%", pad=0.05)
    cbar = fig.colorbar(im, cax=cax)
    cbar.set_label("Density contrast", fontsize=12)

    # Turn off the actual image part of the last axis
    axes[-1].axis('off')


    fig.suptitle(f"Field Slices from {os.path.basename(input_dir)}", fontsize=16)
    fig.tight_layout(rect=[0, 0.03, 1, 0.95])

    # Save figure
    output_path = os.path.join(input_dir, "field_grid.png")
    fig.savefig(output_path)
    print(f"Saved plot to: {output_path}")
    plt.close()

if __name__ == "__main__":
    main()
