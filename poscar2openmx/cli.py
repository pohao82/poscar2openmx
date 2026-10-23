#!/usr/bin/env python3
"""
Script to convert VASP POSCAR to OpenMX .dat input format

    Check the conversions between Ang and Frac 
    To-do 
       * wrap bandstructure section into a wraper so that vasp can also use it.

    usage:
    python poscar2openmx POSCAR 
    or 
    ./poscar2openmx.py POSCAR 

"""
import argparse
import logging
import os
import shutil
import sys
from poscar2openmx.convert import convert
from poscar2openmx.defaults import DEFAULTS as D, CHOICES, normalize_choice

EXAMPLES_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'examples')
# bundled example copied to the current folder when run without arguments
EXAMPLE_SRC = 'HoAgGe_3x2'
EXAMPLE_DEST = 'input_example_HoAgGe'

NO_INPUT_MESSAGE = f"""No input file given.

  poscar2openmx POSCAR       convert a POSCAR file
  poscar2openmx --example    copy an example to ./{EXAMPLE_DEST}
  poscar2openmx --help       list all options
"""

STANDARD_USAGE = f"""
Standard cases (HoAgGe, 54 atoms, noncollinear):

  cd {EXAMPLE_DEST}
  poscar2openmx hoagge.poscar.cart                                           # default parameters
  poscar2openmx hoagge.poscar.cart --parameter_file params_file              # parameters from a file
  poscar2openmx hoagge.poscar.cart --pol nc --magmom "$(cat magmom_string)"  # moments from a VASP MAGMOM string

More examples: {EXAMPLE_DEST}/commandline_examples.txt
Full option list: poscar2openmx --help
"""


def copy_examples(dest='.'):
    """Copy the bundled example into dest, unless it already exists."""
    target = os.path.join(dest, EXAMPLE_DEST)
    if os.path.exists(target):
        print(f"Skipped {target} (already exists)")
    else:
        shutil.copytree(os.path.join(EXAMPLES_DIR, EXAMPLE_SRC), target)
        print(f"Copied example {target}")
    print(STANDARD_USAGE)


def choice_type(key):
    """argparse type: case-insensitive choice (first letter only for coord_system/basis_prec)"""
    def convert_choice(value):
        try:
            return normalize_choice(key, value)
        except ValueError as e:
            raise argparse.ArgumentTypeError(str(e))
    return convert_choice


def input_parser(argv=None):

    parser = argparse.ArgumentParser(description='Convert VASP POSCAR to OpenMX input format')
    parser.add_argument('poscar', nargs='?', help='POSCAR file to convert')
    parser.add_argument('--example', action='store_true', help=f'copy an example input to ./{EXAMPLE_DEST} and show how to run it')
    # optional arguments read from file will overwrite commandline
    parser.add_argument('--parameter_file', help='read input parameters from a file.', default=None)
    # optional arguments
    parser.add_argument('--xc', help='functionals, case-insensitive (default: GGA-PBE)', type=choice_type('xc'), default=D['xc'], choices=CHOICES['xc'])
    parser.add_argument('--pol', help='spin polarization type, case-insensitive (default: on)', type=choice_type('pol'), default=D['pol'], choices=CHOICES['pol'])
    parser.add_argument('-o', '--output', help='Output OpenMX file name (default: openmx_input.dat)', default=D['output'])
    parser.add_argument('-c','--coord_system', help='output coordinate system (F)raction/Direct or (C)artesian, first letter, case-insensitive (default=F)', type=choice_type('coord_system'), default=D['coord_system'], choices=CHOICES['coord_system'])
    parser.add_argument('-v','--basis_ver', help='basis set ver.', type=str, default=D['basis_ver'])
    parser.add_argument('-p','--basis_prec', help='basis accuracy/size, first letter, case-insensitive (default: Quick)', type=choice_type('basis_prec'), default=D['basis_prec'], choices=CHOICES['basis_prec'])
    parser.add_argument('-b','--band', help='band structure, case-insensitive', type=choice_type('band'), default=D['band'], choices=CHOICES['band'])

    # k-point grid for SCF
    parser.add_argument('--kspacing', type=float, default=D['kspacing'],
                        help='automatic k-grid, n_i = ceil(kspacing / d_i) with d_i the lattice-plane spacing in Ang (default: 35)')
    parser.add_argument('--kgrid', type=int, nargs=3, default=D['kgrid'], metavar=('N1', 'N2', 'N3'),
                        help='explicit k-grid, overrides --kspacing')

    # should allow user define k-point path?
    # place holder for now
    parser.add_argument('--element_order',
                    nargs='*',  # Expect zero or more arguments
                    type=str,   # Each argument should be a string
                    default = D['element_order'],
                    help='A list of element symbols (e.g., O La Fe Se), defines how elements will be sorted')

    # input moments
    parser.add_argument('--magmom', help='vasp MAGMOM string', type=str, default=D['magmom'])
    parser.add_argument('--vector_file', help='file that stores the vector as a natoms-by-3 array', default=D['vector_file'])

    args = parser.parse_args(argv)
    if args.poscar is None and not args.example:
        parser.error('the POSCAR file is required (poscar2openmx --example copies an example)')
    return args


def main(argv=None):
    if argv is None:
        argv = sys.argv[1:]
    if not argv:
        print(NO_INPUT_MESSAGE)
        return
    logging.basicConfig(level=logging.INFO, format='%(message)s')
    args = input_parser(argv)
    if args.example:
        copy_examples()
        return
    params = vars(args)
    params.pop('example')
    poscar = params.pop('poscar')
    parameter_file = params.pop('parameter_file')
    try:
        # parameter file values override the command line
        convert(poscar, parameter_file=parameter_file, **params)
    except (ValueError, FileNotFoundError) as e:
        sys.exit(f"Error: {e}")


if __name__ == "__main__":
    main()
