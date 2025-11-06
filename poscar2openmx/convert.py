import numpy as np
from poscar2openmx.io.read_poscar import read_poscar
from poscar2openmx.io.write_openmx_str import write_openmx_str
from poscar2openmx.utils.parse_magmom import parse_magmom_string
from poscar2openmx.utils.coordinate_transform import cartesian_to_spherical

def parse_input_moments(pol, natoms=None, magmom_str=None, vector_file=None):
    # Need natoms for magmom_string parsing

    # double check just to be safe
    if magmom_str is not None and vector_file is not None: 
        print("Vector source conflict! magmom and vector_file can not be both specified")
        raise ValueError("either --magmom or --vector_file, pick one!")

    # Red from file
    elif vector_file:
        print('read in vector file')
        print(vector_file)
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


def run_conversion(poscar_path, params):
    """
    Programmatic entry point.
    poscar_path: path to POSCAR file
    params: dict-like of parameters (same keys as argparse)
    returns: (output_filename, full_input_str)
    """
    structure = read_poscar(poscar_path)
    natoms = sum(structure['atom_counts'])
    params['magmom'] = parse_input_moments(params.get('pol','on'), natoms,
                                           params.get('magmom', None),
                                           params.get('vector_file', None))

    full_input_str = write_openmx_str(structure, params)
    with open(params.get('output', 'openmx_input.dat'),'w') as f:
        f.write(full_input_str)
    return params.get('output', 'openmx_input.dat'), full_input_str
