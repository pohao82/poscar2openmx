import pytest

from poscar2openmx import convert
from poscar2openmx.cli import main
from poscar2openmx.defaults import normalize_choice
from conftest import V_POSCAR, keyword


@pytest.mark.parametrize('key, value, expected', [
    ('basis_prec', 'quick', 'Quick'),
    ('basis_prec', 'S', 'Standard'),
    ('basis_prec', 'PRECISE', 'Precise'),
    ('basis_prec', 'p', 'Precise'),
    ('coord_system', 'f', 'F'),
    ('coord_system', 'cartesian', 'C'),
    ('coord_system', 'Direct', 'F'),
    ('xc', 'gga-pbe', 'GGA-PBE'),
    ('xc', 'lsda-ca', 'LSDA-CA'),
    ('pol', 'NC', 'nc'),
    ('pol', 'Off', 'off'),
    ('band', 'ON', 'on'),
])
def test_normalize(key, value, expected):
    assert normalize_choice(key, value) == expected


@pytest.mark.parametrize('key, value', [
    ('basis_prec', 'x'),
    ('coord_system', ''),
    ('xc', 'PBE'),     # full word needed: LDA / LSDA-* share letters
    ('pol', 'o'),      # on / off
])
def test_invalid(key, value):
    with pytest.raises(ValueError, match=key):
        normalize_choice(key, value)


def test_api_lowercase_same_as_canonical():
    assert (convert(V_POSCAR, basis_prec='standard', coord_system='c', xc='lda', pol='NC')
            == convert(V_POSCAR, basis_prec='Standard', coord_system='C', xc='LDA', pol='nc'))


def test_parameter_file_lowercase(tmp_path):
    f = tmp_path / 'params'
    f.write_text('[settings]\nbasis_prec = precise\ncoord_system = c\nxc = lda\n')
    assert (convert(V_POSCAR, parameter_file=str(f))
            == convert(V_POSCAR, basis_prec='Precise', coord_system='C', xc='LDA'))


def test_cli_lowercase(in_tmp):
    main([V_POSCAR, '-p', 's', '-c', 'c', '--xc', 'lda', '--pol', 'NC', '-b', 'OFF', '-o', 'x.dat'])
    text = (in_tmp / 'x.dat').read_text()
    assert keyword(text, 'Atoms.SpeciesAndCoordinates.Unit') == ['Ang']
    assert keyword(text, 'scf.XcType') == ['LDA']
    assert keyword(text, 'scf.SpinPolarization') == ['nc']


def test_cli_invalid(capsys):
    with pytest.raises(SystemExit) as e:
        main([V_POSCAR, '-p', 'x'])
    assert e.value.code == 2
    assert "invalid basis_prec 'x'" in capsys.readouterr().err


def test_parameter_file_invalid(tmp_path):
    f = tmp_path / 'params'
    f.write_text('[settings]\npol = yes\n')
    with pytest.raises(ValueError, match="invalid pol 'yes'"):
        convert(V_POSCAR, parameter_file=str(f))
