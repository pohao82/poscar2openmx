import os
import numpy as np
import pytest

from poscar2openmx import convert, run_conversion
from conftest import HO_CART, HO_FRAC, V_POSCAR, V_DIR, V_MAGMOM, HO_MAGMOM, atom_lines, keyword


def test_defaults_return_text_without_writing(in_tmp):
    text = convert(V_POSCAR)
    assert os.listdir(in_tmp) == []
    assert keyword(text, 'scf.XcType') == ['GGA-PBE']
    assert keyword(text, 'scf.SpinPolarization') == ['on']
    assert keyword(text, 'Atoms.Number') == ['5']


def test_output_written(in_tmp):
    text = convert(V_POSCAR, output='out.dat')
    assert (in_tmp / 'out.dat').read_text() == text


def test_unknown_parameter():
    with pytest.raises(TypeError, match='polarization'):
        convert(V_POSCAR, polarization='nc')


def test_run_conversion_fills_defaults(in_tmp):
    outfn, text = run_conversion(V_POSCAR, {'output': 'x.dat', 'pol': 'off'})
    assert outfn == 'x.dat' and (in_tmp / 'x.dat').exists()
    assert keyword(text, 'scf.SpinPolarization') == ['off']


def test_parameter_file_overrides_keywords(in_tmp):
    # template sets pol=on, magmom and output
    text = convert(V_POSCAR, parameter_file=os.path.join(V_DIR, 'params_file'), pol='nc')
    assert keyword(text, 'scf.SpinPolarization') == ['on']
    assert (in_tmp / 'openmx_input_V2Se2O.dat').exists()


class TestMoments:
    def test_collinear_magmom(self):
        atoms = atom_lines(convert(V_POSCAR, magmom=V_MAGMOM))
        # V: 13 valence electrons, moments -1 / +1
        assert atoms[0][5:7] == ['6.00', '7.00']
        assert atoms[1][5:7] == ['7.00', '6.00']
        assert atoms[4][5:7] == ['3.00', '3.00']

    def test_default_moments(self):
        atoms = atom_lines(convert(V_POSCAR))
        # V-Zn start with +1 moment by default
        assert atoms[0][5:7] == ['7.50', '5.50']

    def test_array_equals_string(self):
        from_string = convert(V_POSCAR, magmom=V_MAGMOM)
        assert convert(V_POSCAR, magmom=[-1, 1, 0, 0, 0]) == from_string
        assert convert(V_POSCAR, magmom=np.array([[-1, 0, 0], [1, 0, 0]] + [[0, 0, 0]] * 3)) == from_string

    def test_vector_file_equals_magmom(self, tmp_path):
        vec = tmp_path / 'vec'
        vec.write_text('-1\n1\n0\n0\n0\n')
        assert convert(V_POSCAR, vector_file=str(vec)) == convert(V_POSCAR, magmom=V_MAGMOM)

    def test_noncollinear_angles(self):
        # after 108*0 the triplets are Ho1 = (0, 5.5, 0) ... Ho7 = (4.7631, 2.75, 0)
        atoms = atom_lines(convert(HO_CART, pol='nc', magmom=HO_MAGMOM))
        ho = [a for a in atoms if a[1] == 'Ho']
        assert [float(x) for x in ho[0][7:11]] == pytest.approx([90, 90, 90, 90])
        assert [float(x) for x in ho[6][7:11]] == pytest.approx([90, 30, 90, 30], abs=0.01)

    def test_conflict(self):
        with pytest.raises(ValueError, match='pick one'):
            convert(V_POSCAR, magmom=V_MAGMOM, vector_file='vec')

    def test_wrong_number_of_atoms(self):
        with pytest.raises(ValueError, match='expected \\(5, 3\\)'):
            convert(V_POSCAR, magmom=[1, 2, 3])


def test_element_order_moves_moments_with_atoms():
    atoms = atom_lines(convert(V_POSCAR, magmom=V_MAGMOM, element_order=['O', 'Se', 'V']))
    assert [a[1] for a in atoms] == ['O', 'Se', 'Se', 'V', 'V']
    assert atoms[3][5:7] == ['6.00', '7.00']
    assert atoms[4][5:7] == ['7.00', '6.00']


def test_element_order_mismatch():
    with pytest.raises(ValueError, match='element_order'):
        convert(V_POSCAR, element_order=['V', 'Se'])


def test_cartesian_output_matches_fractional_input():
    from_frac = atom_lines(convert(HO_FRAC, coord_system='C'))
    from_cart = atom_lines(convert(HO_CART, coord_system='C'))
    for a, b in zip(from_frac, from_cart):
        np.testing.assert_allclose([float(x) for x in a[2:5]], [float(x) for x in b[2:5]], atol=1e-5)


class TestKgrid:
    def test_auto(self):
        assert keyword(convert(V_POSCAR), 'scf.Kgrid') == ['10', '10', '6']

    def test_kspacing(self):
        assert keyword(convert(V_POSCAR, kspacing=20), 'scf.Kgrid') == ['6', '6', '4']

    def test_explicit(self):
        assert keyword(convert(V_POSCAR, kgrid=[6, 6, 1]), 'scf.Kgrid') == ['6', '6', '1']


class TestUnknownElement:
    @pytest.fixture
    def gd_poscar(self, tmp_path):
        text = open(V_POSCAR).read().replace('    V   Se    O', '   Gd   Se    O')
        path = tmp_path / 'gd.vasp'
        path.write_text(text)
        return str(path)

    def test_placeholders(self, gd_poscar, caplog):
        text = convert(gd_poscar, magmom='-7 7 3*0')
        assert 'Gd (Gd_PBE19) not found' in caplog.text
        assert ' Gd   Gd8.0-s2p2d2f1   Gd_PBE19   # placeholder' in text
        atoms = atom_lines(text)
        assert atoms[0][5:7] == ['X', 'X']
        assert '(valence - 7.00)/2 and (valence + 7.00)/2' in ' '.join(atoms[0])
        assert atoms[2][5:7] == ['3.00', '3.00']
        u_block = text.split('<Hubbard.U.values')[1].split('Hubbard.U.values>')[0]
        j_block = text.split('<Hubbard.J.values')[1].split('Hubbard.J.values>')[0]
        assert 'Gd   1s 0 2s 0 1p 0 2p 0 1d 0 2d 0 1f 7.0' in u_block
        assert '7.0' not in j_block

    def test_custom_basis_kept(self, gd_poscar):
        text = convert(gd_poscar, basis={'Gd': 'Gd9.0-s3p2d2f1', 'Se': 'Se7.0-s3p2d1', 'O': 'O6.0-s2p2'})
        assert ' Gd   Gd9.0-s3p2d2f1' in text
        assert atom_lines(text)[0][5:7] == ['X', 'X']
