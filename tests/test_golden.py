"""
Compare full output files against tests/golden/*.dat.

After an intended change to the output, regenerate with
    UPDATE_GOLDEN=1 pytest tests/test_golden.py
and review the diff before committing.
"""
import os
import pytest

from poscar2openmx import convert
from conftest import HO_CART, HO_FRAC, HO_DIR, V_POSCAR, V_MAGMOM, HO_MAGMOM

GOLDEN_DIR = os.path.join(os.path.dirname(__file__), 'golden')

CASES = {
    'ho_default': (HO_CART, {}),
    'ho_nc_vecfile_cart': (HO_FRAC, dict(coord_system='C', pol='nc', element_order=['Ag', 'Ge', 'Ho'],
                                         vector_file=os.path.join(HO_DIR, 'vec_file'))),
    'ho_nc_magmom': (HO_CART, dict(pol='nc', magmom=HO_MAGMOM)),
    'v2se2o_magmom': (V_POSCAR, dict(magmom=V_MAGMOM)),
    'v2se2o_standard_lda': (V_POSCAR, dict(basis_prec='Standard', xc='LDA', pol='off')),
}


@pytest.mark.parametrize('name', CASES)
def test_golden(name):
    poscar, params = CASES[name]
    text = convert(poscar, **params)
    path = os.path.join(GOLDEN_DIR, f'{name}.dat')
    if os.environ.get('UPDATE_GOLDEN'):
        with open(path, 'w') as f:
            f.write(text)
    with open(path) as f:
        assert text == f.read()
