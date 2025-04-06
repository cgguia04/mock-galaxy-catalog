from classy import Class

cosmo = Class()
cosmo.set({
    'output': 'mPk',
    'P_k_max_h/Mpc': 10,
    'h': 0.67,
    'omega_b': 0.0224,
    'omega_cdm': 0.12,
})
cosmo.compute()

print(f"P(k=0.1 h/Mpc, z=0) = {cosmo.pk(0.1, 0)}")

cosmo.struct_cleanup()

