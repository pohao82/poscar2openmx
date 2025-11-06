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
import numpy as np
from poscar2openmx.io.parameter_reader import input_parameter_reader
from poscar2openmx.convert import run_conversion

def input_parser():

    parser = argparse.ArgumentParser(description='Convert VASP POSCAR to OpenMX input format')
    parser.add_argument('poscar', help='POSCAR file to convert')
    # optional arguments read from file will overwrite commandline
    parser.add_argument('--parameter_file', help='read input parameters from a file.', default=None)
    # optional arguments
    parser.add_argument('--xc', help='functionals (default: GGA-PBE)', type=str, default='GGA-PBE',choices=['LDA','LSDA-CA','LSDA-PW','GGA-PBE'])
    parser.add_argument('--pol', help='spin polarization type', type=str, default='on',choices=['on','off','nc'])
    parser.add_argument('-o', '--output', help='Output OpenMX file name (default: openmx_input.dat)', default='openmx_input.dat')
    parser.add_argument('-c','--coord_system', help='output coordinate system (F)raction/Direct or (C)artesian (default=F)', type=str, default='F',choices=['F','C'])
    parser.add_argument('-v','--basis_ver', help='basis set ver.', type=str, default='19')
    parser.add_argument('-p','--basis_prec', help='basis accuracy/size (default: Quick)', type=str, default='Quick', choices=['Quick','Standard','Precise'])
    parser.add_argument('-b','--band', help='band structure', type=str, default='off', choices=['on','off'])

    # should allow user define k-point path?
    # place holder for now
    parser.add_argument('--element_order',
                    nargs='*',  # Expect zero or more arguments
                    type=str,   # Each argument should be a string
                    default = None,
                    help='A list of element symbols (e.g., O La Fe Se), defines how elements will be sorted')

    # input moments
    parser.add_argument('--magmom', help='vasp MAGMOM string', type=str, default=None)
    parser.add_argument('--vector_file', help='file that stores the vector as a natoms-by-3 array', default=None)

    args = parser.parse_args()
    return args


def main(argv=None):
    if argv is None:
        argv = None  # argparse will read from sys.argv
    args = input_parser()  # adapt input_parser to accept argv
    args_dict = vars(args)
    # allow parameter file overrides
    if args.parameter_file:
        file_args = input_parameter_reader(args.parameter_file)
        args_dict.update(file_args)
    outfn, _ = run_conversion(args.poscar, args_dict)
    print(f"Written {outfn}")


if __name__ == "__main__":
    main()
