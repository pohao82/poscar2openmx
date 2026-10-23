import numpy as np
import pytest

from poscar2openmx.io.read_poscar import read_poscar
from poscar2openmx.io.parameter_reader import input_parameter_reader
from conftest import HO_CART, HO_FRAC, V_POSCAR, V_DIR
import os


def test_read_poscar_direct():
    s = read_poscar(V_POSCAR)
    assert s['elements'] == ['V', 'Se', 'O']
    assert s['atom_counts'] == [2, 2, 1]
    assert s['direct']
    assert len(s['positions']) == 5
    assert s['positions'][2][0] == 'Se'


def test_cart_and_frac_poscar_agree():
    cart, frac = read_poscar(HO_CART), read_poscar(HO_FRAC)
    assert not cart['direct'] and frac['direct']
    np.testing.assert_allclose(cart['lattice'], frac['lattice'])
    for (el_c, pc), (el_f, pf) in zip(cart['positions'], frac['positions']):
        assert el_c == el_f
        np.testing.assert_allclose(np.dot(pf, frac['lattice']), pc, atol=1e-5)


def test_template_parameter_file():
    p = input_parameter_reader(os.path.join(V_DIR, 'params_file'))
    assert p['pol'] == 'on'
    assert p['magmom'] == '-1 1 3*0'
    assert p['element_order'] == ['V', 'Se', 'O']
    assert p['kspacing'] == 35.0
    assert p['basis_ver'] == '19'
    assert 'basis' not in p and 'kgrid' not in p


def write(tmp_path, text):
    f = tmp_path / 'params'
    f.write_text(text)
    return str(f)


def test_basis_and_kgrid(tmp_path):
    p = input_parameter_reader(write(tmp_path, "[settings]\nkgrid = 6 6 1\n"
                                               "basis = {'V':'V6.0-s3p2d1',\n  'O':'O6.0-s2p2'}\n"))
    assert p['kgrid'] == [6, 6, 1]
    assert p['basis'] == {'V': 'V6.0-s3p2d1', 'O': 'O6.0-s2p2'}


@pytest.mark.parametrize('text, match', [
    ("[other]\npol = on\n", 'no \\[settings\\]'),
    ("[settings]\nkgrid = 6 6\n", 'kgrid'),
    ("[settings]\nbasis = ['V']\n", 'not a valid dictionary'),
    ("[settings]\nbasis = {'V':\n", 'Error parsing'),
])
def test_bad_parameter_file(tmp_path, text, match):
    with pytest.raises(ValueError, match=match):
        input_parameter_reader(write(tmp_path, text))


def test_missing_parameter_file(tmp_path):
    with pytest.raises(FileNotFoundError):
        input_parameter_reader(str(tmp_path / 'nope'))
