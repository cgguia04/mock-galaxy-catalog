import numpy as np
import os
import sys

'''
Coles & Jones (1990) Eq. (4)
Y(r) = exp[X(r)] where X(r) is a Gaussian random field

Physics 212 Lecture 16 Eq. (1)
δ(x,t) = (ρ(x,t)/ρ̄) - 1 with mean zero
'''

def apply_log_normal(field):
    sigma2 = np.var(field)
    rho_ln = np.exp(field - 0.5 * sigma2)  #rho must have mean 1 by definition
    return rho_ln

def main():
    if len(sys.argv) < 2:
        print("Usage: python src/apply_log_normal.py output/[model]/gaussian_field/")
        sys.exit(1)

    input_dir = sys.argv[1]

    if not os.path.isdir(input_dir):
        print(f"Directory not found: {input_dir}")
        sys.exit(1)

    # Determine the model's parent folder (e.g., output/w0wa/)
    model_folder = os.path.dirname(input_dir)
    lognormal_dir = os.path.join(model_folder, "lognormal_field")
    os.makedirs(lognormal_dir, exist_ok=True)

    for filename in sorted(os.listdir(input_dir)):
        if filename.endswith(".npy") and not filename.endswith("_lognormal.npy"):
            field_path = os.path.join(input_dir, filename)
            base_name = os.path.splitext(filename)[0]
            output_path = os.path.join(lognormal_dir, f"{base_name}_lognormal.npy")

            print(f"Transforming {filename} → log-normal")
            field = np.load(field_path)
            rho_ln = apply_log_normal(field)
            np.save(output_path, rho_ln)
            print(f"Saved log-normal field to: {output_path}")

if __name__ == "__main__":
    main()
