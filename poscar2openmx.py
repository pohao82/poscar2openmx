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
from core.read_poscar import read_poscar
from core.write_openmx_str import write_openmx_str
from core.parameter_reader import input_parameter_reader
from core.parse_magmom import parse_magmom_string
from core.utils import cartesian_to_spherical

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


def parse_input_moments(pol, natoms=None, magmom_str=None, vector_file=None):
    # Need natoms for magmom_string parsing

    # double check just to be safe
    if magmom_str is not None and vector_file is not None: 
        print("Vector source conflict! magmom and vector_file can not be both specified")
        raise ValueError("either --magmom or --vector_file, pick one!")

    # Red from file
    elif vector_file:
        print('read in vector file')
        vec_data = np.loadtxt(vector_file)

        # if file contains 1d array, make it N-by-3 for compatibility
        if vec_data.ndim == 1:
            N = len(vec_data)
            zero_col = np.zeros((N, 1))
            vec_x = vec_data.reshape(N, 1)
            vec_array = np.hstack((vec_x, zero_col, zero_col))
        else:
            vec_array = vec_data

    # Read from magmom string
    elif magmom_str:
        print('magmom string specified')
        # magmom also return N-by-3 (only 1st column filled)
        vec_array = parse_magmom_string(magmom_str, natoms, sqa=0)

    # Nohting specified
    else:
        print('No moment specified, use default')
        vec_array = None

    # If noncollinear (pol=nc) Convert to spherical coordinate (|M|, theta, phi) 
    if pol.lower()=='nc' and vec_array is not None:
        vec_array_sph = np.zeros(vec_array.shape)
        for i, vec in enumerate(vec_array):
            vec_array_sph[i,:] = cartesian_to_spherical(vec) 
        return vec_array_sph

    # assign directly if collinear
    else: 
        return vec_array


def poscar2openmx():

    # cli parameters from commandline
    args = input_parser()

    # If the external file exist
    args_dict = {}
    if args.parameter_file:
        args_file = input_parameter_reader(args.parameter_file)
        print(f"parameters specified in the input file {args_file.keys()}")
        print(args_file)
        # add the parameters specified from file
        for key in args_file.keys():
            setattr(args, key, args_file[key])

    # Convert to dict more flexible
    args_dict = vars(args)

    # Read POSCAR file
    structure = read_poscar(args.poscar)

    # ------------------------------------------------------
    #   Magmom stuff (either from magmom string or a file)
    # ------------------------------------------------------
    natoms = sum(structure['atom_counts']) # need this for magmom string parsing
    args_dict['magmom'] = parse_input_moments(args_dict['pol'], natoms, args.magmom, args.vector_file)

    # get input as strings
    full_input_str = write_openmx_str(structure, args_dict)

    # write strings into a file
    output_filename = args.output
    with open(output_filename, 'w') as f:
        f.write(full_input_str)

    print(f"Converted {args.poscar} to OpenMX format: {args.output}")
    print(f"input parameters {args}")

if __name__ == "__main__":
    poscar2openmx()
