import numpy as np
import pytest

from poscar2openmx.utils.parse_magmom import parse_magmom_string
from poscar2openmx.utils.expand_basis import expand_basis
from poscar2openmx.utils.coordinate_transform import cartesian_to_spherical
from poscar2openmx.utils.kgrid import auto_kgrid


class TestParseMagmom:
    def test_collinear_with_repeat(self):
        m = parse_magmom_string('MAGMOM = -1 1 3*0', 5, sqa=0)
        assert m.shape == (5, 3)
        assert m[:, 0].tolist() == [-1, 1, 0, 0, 0]
        assert not m[:, 1:].any()

    def test_collinear_sqa_z(self):
        m = parse_magmom_string('2*5', 2, sqa=2)
        assert m.tolist() == [[0, 0, 5], [0, 0, 5]]

    def test_noncollinear(self):
        m = parse_magmom_string('3*0 1 2 3', 2)
        assert m.tolist() == [[0, 0, 0], [1, 2, 3]]

    def test_wrong_count(self):
        with pytest.raises(ValueError, match='Invalid number of moments'):
            parse_magmom_string('1 2 3 4', 3)


class TestExpandBasis:
    def test_expand(self):
        assert expand_basis('s2p1d1') == '1s 0 2s 0 1p 0 1d 0'

    def test_values(self):
        assert expand_basis('s1d2f1', {'1f': 7.0}) == '1s 0 1d 0 2d 0 1f 7.0'


class TestSpherical:
    def test_along_z(self):
        assert cartesian_to_spherical([0, 0, 2]) == pytest.approx([2, 0, 0])

    def test_along_minus_y(self):
        assert cartesian_to_spherical([0, -3, 0]) == pytest.approx([3, 90, -90])

    def test_zero(self):
        assert cartesian_to_spherical([0, 0, 0]) == [0, 0, 0]


class TestAutoKgrid:
    def test_cubic_exact_multiple(self):
        # 35 / 3.5 = 10 exactly, must not round up to 11
        assert auto_kgrid(np.eye(3) * 3.5) == [10, 10, 10]

    def test_orthorhombic(self):
        assert auto_kgrid(np.diag([21.23, 12.26, 4.18])) == [2, 3, 9]

    def test_kspacing(self):
        assert auto_kgrid(np.eye(3) * 4.0, kspacing=20) == [5, 5, 5]

    def test_minimum_one(self):
        assert auto_kgrid(np.diag([4.0, 4.0, 100.0]))[2] == 1

    def test_uses_plane_spacing_for_oblique_cell(self):
        # hexagonal a=3: plane spacing is a*sqrt(3)/2 = 2.598, not 3
        a = 3.0
        hexagonal = np.array([[a, 0, 0], [-a / 2, a * np.sqrt(3) / 2, 0], [0, 0, 10.0]])
        assert auto_kgrid(hexagonal) == [14, 14, 4]
