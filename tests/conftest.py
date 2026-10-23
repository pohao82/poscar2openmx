import os
import pytest

EXAMPLES = os.path.join(os.path.dirname(__file__), '..', 'poscar2openmx', 'examples')
HO_DIR = os.path.join(EXAMPLES, 'HoAgGe_3x2')
V_DIR = os.path.join(EXAMPLES, 'V2Se2O')

HO_CART = os.path.join(HO_DIR, 'hoagge.poscar.cart')
HO_FRAC = os.path.join(HO_DIR, 'hoagge.poscar.frac')
V_POSCAR = os.path.join(V_DIR, 'V2Se2O.cube_1F.vasp')

# noncollinear MAGMOM for the 54-atom HoAgGe cell (from commandline_examples.txt)
HO_MAGMOM = ('108*0 0 5.5  0 -0 -5.5  0 -0 -5.5  0 0  5.5  0 0  5.5  0 0  5.5  '
             '0 4.7631  2.75  0 4.7631  2.75  0 -4.7631 -2.75  0 -4.7631 -2.75  '
             '0 4.7631  2.75  0 4.7631  2.75  0 4.7631 -2.75  0 -4.7631  2.75  '
             '0 -4.7631  2.75  0 -4.7631  2.75  0 -4.7631  2.75  0 4.7631 -2.75  0')
V_MAGMOM = '-1 1 3*0'


def atom_lines(text):
    """Lines of the <Atoms.SpeciesAndCoordinates block, split into fields."""
    block = text.split('<Atoms.SpeciesAndCoordinates\n')[1].split('Atoms.SpeciesAndCoordinates>')[0]
    return [line.split() for line in block.strip().splitlines()]


def keyword(text, key):
    """Value fields of a one-line OpenMX keyword (comment stripped)."""
    for line in text.splitlines():
        if line.split()[:1] == [key]:
            return line.split('#')[0].split()[1:]
    raise KeyError(key)


@pytest.fixture
def in_tmp(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    return tmp_path
