# Generating Mock Galaxy Catalogs
 
 This project computes the matter power spectrum $P(k, z)$ using CLASS (via `classy`) for two cosmological models — Planck 2018 ΛCDM and a DESI DR2–inspired $w_0w_a$ dark energy model. It outputs the power spectra of Gaussian fields and galaxy fields after bias expansion. These can respectively be compared with the standard power spectra from CLASS and CLASS-PT.
 
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
 │ ├── plot_field.py
 │ ├── field_power_spectrum.py
 │ ├── galaxy_bias_expansion.py 
 │ ├── planck_lcdm_classpt.py
 │ └── w0wa_classpt.py
 ├── output/ # Model-specific outputs 
 │ ├── planck_lcdm/ │ 
 │ │ ├── pk/ # Power spectrum txt files 
 │ │ ├── gaussian_field/ # Gaussian density fields 
 │ │ ├── galaxy_field/ # Galaxy bias expansion
 │ │ └── classpt/ #Perturbation theory prediction
 │ └── wowa/ 
 │ │ ├── pk/ 
 │ │ ├── gaussian_field/ 
 │ │ ├── galaxy_field/ 
 │ │ └── classpt/ 
 ├── requirements.txt 
 ├── run_pipeline.sh #Run all
 ├── writeup
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
 
 To plot a grid of 2D slices:

  ```bash
 python src/plot_field.py output/planck_lcdm/gaussian_field
 ```

Saves to:
 
 ``
 output/planck_lcdm/gaussian_field/field_grid.png
 ``

4. Plot Power Spectrum of Fields

```bash
python src/field_power_spectrum.py output/planck_lcdm/gaussian_field
```

Saves to:

``
 output/planck_lcdm/gaussian_field/field_power_spectrum.png
 ``

 and .txt files of the power spectra at each redshift. For example:

 ``
 output/planck_lcdm/gaussian_field/pk_planck_lcdm_z0.txt
 ``

 This also prints the means and variances of each field as a sanity check.

 5. Generate Galaxy Field via Bias Expansion

 ```bash
 python src/galaxy_bias_expansion.py output/planck_lcdm/gaussian_field
 ```

 Saves to:
 
 ``
 output/planck_lcdm/galaxy_field/pk_planck_lcdm_z0_galaxy.npy
 ``

 6. Compute Power Spectrum of Galaxy Field

 Same procedure as Step 4.
 

 7. Generate Perturbation Theory Predictions

```bash
python src/planck_lcdm_classpt.py
 ```

 Saves to:
 
 ``
 output/planck_lcdm/classpt/
 ``

  0. To Run the Full Pipeline, 

  ```bash
  ./run_pipeline.sh
  ```


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
 
``
 planck_lcdm_classpt.py
 ``
 
 ``
w0wa_classpt.py
 ``

 Calibrated to Planck 2018 and DESI DR2, respectively, with galaxy bias parameters and shot noise, excluding 1-loop corrections. 

 - $b_1 = 1.2$
 - $b_2 = -0.405$
 - $b_{G2} = -0.127$
 - $P_{\text{shot}} = 1000$
 - $c_{s0} = c_{s2} = c_{s4} = b_3 = b_4 = 0.0$

 ---
 
 ## Notes
 - Redshifts are defined in YAML with `z_pk: [0, 0.5, 1, 2, 3]`
 - CLASS expects `z_pk` as a space-separated string — this is handled automatically in Python
 - Each model’s results are saved in `output/[model_name]`
 
 ---
 
 ## What's next
 The next stage will involve:
 - Using galaxy bias expansion to create a galaxy field
 - Constructing mock galaxy catalogs with Poisson sampling
 
 ---
 
 ## Author
 Carl Audric Guia