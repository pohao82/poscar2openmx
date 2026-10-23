import numpy as np


def auto_kgrid(lattice, kspacing=35.0):
    """
    Monkhorst-Pack grid from the rule n_i * d_i >= kspacing.

    d_i is the spacing between lattice planes perpendicular to reciprocal vector b_i,
    d_i = 2*pi/|b_i|, which equals the lattice constant a_i for orthogonal cells.

    Args:
        lattice (3x3 array): lattice vectors as rows (Angstrom)
        kspacing (float): target n_i * d_i in Angstrom (default 35)

    Returns:
        list of 3 ints
    """
    lattice = np.asarray(lattice, dtype=float)
    # |b_i| / 2pi = row norms of inv(lattice).T
    inv_d = np.linalg.norm(np.linalg.inv(lattice).T, axis=1)
    # small tolerance so that e.g. 35/3.5 does not round up to 11
    return [max(1, int(np.ceil(kspacing * x - 1e-6))) for x in inv_d]
