#!/usr/bin/env python3
"""
Script to convert VASP POSCAR to OpenMX .dat input format

    Check the conversions between Ang and Frac 
    wrap bandstructure section into a wraper so that vasp can also use it.
    Reorder atomic species
    convert cell (should be done on poscar)

    usage:
    python poscar2openmx POSCAR 
    or 
    ./poscar2openmx.py POSCAR 

"""
import argparse
from core.read_poscar import read_poscar
from core.write_openmx import write_openmx
from core.parameter_reader import input_parameter_reader

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
    args = parser.parse_args()
    return args


def poscar2openmx():

    args = input_parser()
    # if the external file exist
    args_dict = {}
    if args.parameter_file:
        args_file, basis = input_parameter_reader(args.parameter_file)
        print(args_file)
        print(f"parameters specified in the input fiel {args_file.keys()}")
        for key in args_file.keys():
            setattr(args, key, args_file[key])
        args.basis = basis
        args_dict['basis'] = basis

    # convert to dict form more flexible
    args_dict = vars(args)
    print(args_dict)

    #print(args.__dict__['xc'])

    # other optional arguments
    #xc_type="PBE"
    #basis_ver="19"
    #coord_system = 'F'
    #specify spieces order move TM to the front
    #basis_accuracy = "Standard"
    #user-defined basis set is provided
    #custom_basis = {
    #                'Co':'2s2p1d'
    #                'Fe':'2s2p1d'
    #                }

    # Read POSCAR file
    structure = read_poscar(args.poscar)
    # Write OpenMX input file
    write_openmx(structure, args_dict)

    print(f"Converted {args.poscar} to OpenMX format: {args.output}")
    print(f"input parameters {args}")

if __name__ == "__main__":
    poscar2openmx()
