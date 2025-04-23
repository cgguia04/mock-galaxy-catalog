#!/bin/bash
set -e

echo "Running full pipeline"

echo "Compute mock power spectrum..."
python src/compute_power_spectrum.py config/planck_lcdm.yaml
python src/compute_power_spectrum.py config/w0wa.yaml

echo "Plot mock power spectrum..."
python src/plot_power_spectrum.py output/planck_lcdm/pk
python src/plot_power_spectrum.py output/w0wa/pk

echo "Generate Gaussian fields..."
python src/generate_gaussian_field.py output/planck_lcdm/pk
python src/generate_gaussian_field.py output/w0wa/pk

echo "Apply galaxy bias expansion..."
python src/galaxy_bias_expansion.py output/planck_lcdm/gaussian_field
python src/galaxy_bias_expansion.py output/w0wa/gaussian_field

echo "Compute field power spectra..."
python src/field_power_spectrum.py output/planck_lcdm/gaussian_field
python src/field_power_spectrum.py output/planck_lcdm/galaxy_field
python src/field_power_spectrum.py output/w0wa/gaussian_field
python src/field_power_spectrum.py output/w0wa/galaxy_field

echo "Plot fields..."
python src/plot_field.py output/planck_lcdm/gaussian_field
python src/plot_field.py output/planck_lcdm/galaxy_field
python src/plot_field.py output/w0wa/gaussian_field
python src/plot_field.py output/w0wa/galaxy_field

echo "Generate CLASS-PT predictions..."
python src/planck_lcdm_classpt.py
python src/w0wa_classpt.py

echo "Pipeline complete."