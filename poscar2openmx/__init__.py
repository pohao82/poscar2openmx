"""
Convert VASP POSCAR to OpenMX input format.

    from poscar2openmx import convert
    text = convert('POSCAR', pol='nc', magmom='...', output='openmx.dat')
"""
from poscar2openmx.convert import convert, run_conversion
from poscar2openmx.defaults import DEFAULTS
from poscar2openmx.io.read_poscar import read_poscar
from poscar2openmx.utils.kgrid import auto_kgrid

__all__ = ['convert', 'run_conversion', 'DEFAULTS', 'read_poscar', 'auto_kgrid']
