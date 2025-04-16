# Generating Mock Galaxy Catalogs to Recover Cosmological Parameters
 
 This project computes the matter power spectrum $P(k, z)$ using CLASS (via `classy`) for multiple cosmological models — including Planck 2018 ΛCDM and a DESI DR2–inspired $w_0w_a$ dark energy model. It outputs power spectra across redshifts and visualizes how structure grows over time.
 
 ---
 
 ## Project Structure
```
 mock-galaxy-catalog/ 
 ├── config/ # YAML files for cosmological models 
 │ ├── planck_lcdm.yaml # Planck 2018 ΛCDM model 
 │ └── wowa.yaml # DESI-inspired w₀wₐCDM model 
 ├── src/ # Source code 
 │ ├── compute_power_spectrum.py 
 │ ├── plot_power_spectrum.py 
 │ ├── generate_gaussian_field.py 
 │ ├── apply_log_normal.py 
 │ └── plot_field.py 
 ├── output/ # Model-specific outputs 
 │ ├── planck_lcdm/ │ 
 │ │ └── pk/ # Power spectrum txt files 
 │ │ └── gaussian_field/ # Gaussian density fields 
 │ │ └── lognormal_field/ # Log-normal transformed fields 
 │ └── wowa/ 
 │ │ └── pk/ 
 │ │ └── gaussian_field/ 
 │ │ └── lognormal_field/ 
 ├── requirements.txt 
 └── README.md
```
 ---
 
 ## Setup
 
 Install required Python packages (after activating your virtual environment):
 
 ```bash
 pip install -r requirements.txt
 ```
 ---
 
 ## Usage
 1. Compute the Power Spectrum

 To generate $P(k,z)$ from a YAML cosmology file:
 ```bash
 python src/compute_power_spectrum.py config/planck_lcdm.yaml
 ```
 
 Output files like:

 ``
 output/planck_lcdm/pk/pk_planck_lcdm_z0.txt
``

``
 output/planck_lcdm/pk/pk_planck_lcdm_z1.txt
``
 
 2. Plot Combined Spectra

 To plot all redshift power spectra for a given model:
 ```bash
 python src/plot_power_spectrum.py output/planck_lcdm/pk
 ```
 
 Saves to:

 ``
 output/planck_lcdm/pk/pk_planck_lcdm_multi_z.png
 ``
 
 3. Generate Gaussian fields

 To transform each $P(k,z)$ into a real-space Gaussian field:
  ```bash
  python src/generate_gaussian_field.py output/planck_lcdm/pk
  ```
  
  Saves to:

 ``
 output/planck_lcdm/gaussian_field/pk_planck_lcdm_z0.npy
 ``

 4. Apply Log-Normal Transformation

 To convert Gaussian fields into realistic, positively-defined density fields:
  ```bash
  python src/apply_log_normal.py output/planck_lcdm/gaussian_field
  ```

  Saves to:
  ``
  output/planck_lcdm/lognormal_field/pk_planck_lcdm_z0_lognormal.npy
 ``

 5. Visualize Fields
 
 To generate a grid of 2D slices:
  ```bash
 python src/plot_field.py output/planck_lcdm/gaussian_field
 ```

 or

 ```bash
 python src/plot_field.py output/planck_lcdm/lognormal_field
 ```

 The first one saves to:
 
 ``
 output/planck_lcdm/gaussian_field/field_grid.png
 ``

 ---
 
 ## Included models
 ``
 planck_lcdm.yaml
 ``
 
 Planck 2018 base ΛCDM model with:
 - $H_0 = 67.36$
 - $\Omega_b h^2 = 0.00237$
 - $\Omega_c h^2 = 0.12$
 
 ``
 w0wa.yaml
 ``
 
 DESI DR2–inspired evolving dark energy model:
 - $w_0 = -0.838$
 - $w_a = -0.1$ (adjusted from DESI’s best-fit to avoid CLASS instability)
 - `use_ppf: yes` to safely evolve through the phantom divide
 
 ---
 
 ## Notes
 - Redshifts are defined in YAML with `z_pk: [0, 0.5, 1, 2, 3]`
 - CLASS expects `z_pk` as a space-separated string — this is handled automatically in Python
 - Each model’s results are saved in `output/[model_name]`
 
 ---
 
 ## What's next
 The next stage will involve:s
 - Using galaxy bias expansion to create a galaxy field
 - Constructing mock galaxy catalogs with Poisson sampling
 
 ---
 
 ## Author
 Carl Audric Guia