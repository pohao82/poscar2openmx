import logging
import numpy as np
from poscar2openmx.defaults import DEFAULTS, normalize_params
from poscar2openmx.io.read_poscar import read_poscar
from poscar2openmx.io.parameter_reader import input_parameter_reader
from poscar2openmx.io.write_openmx_str import write_openmx_str
from poscar2openmx.utils.parse_magmom import parse_magmom_string
from poscar2openmx.utils.coordinate_transform import cartesian_to_spherical

logger = logging.getLogger(__name__)


def _as_n_by_3(vec_data):
    # 1d array (collinear moments) -> N-by-3 with the moment in the first column
    vec_data = np.asarray(vec_data, dtype=float)
    if vec_data.ndim == 1:
        N = len(vec_data)
        zero_col = np.zeros((N, 1))
        vec_x = vec_data.reshape(N, 1)
        return np.hstack((vec_x, zero_col, zero_col))
    return vec_data


def parse_input_moments(pol, natoms=None, magmom_str=None, vector_file=None):
    # Need natoms for magmom_string parsing
    # magmom_str can also be a list/array (N or N-by-3) when called from the Python API

    # double check just to be safe
    if magmom_str is not None and vector_file is not None:
        raise ValueError("either --magmom or --vector_file, pick one!")

    # Red from file
    elif vector_file:
        logger.info(f'read in vector file {vector_file}')
        vec_array = _as_n_by_3(np.loadtxt(vector_file))

    # moments given directly as an array (Python API)
    elif magmom_str is not None and not isinstance(magmom_str, str):
        vec_array = _as_n_by_3(magmom_str)

    # Read from magmom string
    elif magmom_str:
        logger.info('magmom string specified')
        # magmom also return N-by-3 (only 1st column filled)
        vec_array = parse_magmom_string(magmom_str, natoms, sqa=0)

    # Nohting specified
    else:
        logger.info('No moment specified, use default')
        vec_array = None

    if vec_array is not None and vec_array.shape != (natoms, 3):
        raise ValueError(f"moments have shape {vec_array.shape}, expected ({natoms}, 3) "
                         f"or {natoms} values for {natoms} atoms")

    # If noncollinear (pol=nc) Convert to spherical coordinate (|M|, theta, phi)
    if pol.lower()=='nc' and vec_array is not None:
        vec_array_sph = np.zeros(vec_array.shape)
        for i, vec in enumerate(vec_array):
            vec_array_sph[i,:] = cartesian_to_spherical(vec)
        return vec_array_sph

    # assign directly if collinear
    else:
        return vec_array


def build_input(poscar_path, params):
    """
    Build the OpenMX input text. params must contain every key in DEFAULTS.
    """
    params = normalize_params(dict(params))
    structure = read_poscar(poscar_path)
    natoms = sum(structure['atom_counts'])
    params['magmom'] = parse_input_moments(params['pol'], natoms,
                                           params['magmom'],
                                           params['vector_file'])
    return write_openmx_str(structure, params)


def run_conversion(poscar_path, params):
    """
    Programmatic entry point (kept for compatibility, see convert()).
    poscar_path: path to POSCAR file
    params: dict-like of parameters (same keys as argparse); missing keys use DEFAULTS
    returns: (output_filename, full_input_str)
    """
    params = {**DEFAULTS, **params}
    full_input_str = build_input(poscar_path, params)
    with open(params['output'],'w') as f:
        f.write(full_input_str)
    return params['output'], full_input_str


def convert(poscar, output=None, parameter_file=None, **params):
    """
    Convert a VASP POSCAR to OpenMX input text.

    poscar:         path to the POSCAR file
    output:         file to write; None (default) only returns the text
    parameter_file: optional parameter file, its values override the keyword arguments
    **params:       any key of poscar2openmx.defaults.DEFAULTS, e.g.
                    pol='nc', magmom='2*5 3*0' (or an N / N-by-3 array), kgrid=[6, 6, 1]

    returns: the OpenMX input file content as a string

    Example:
        from poscar2openmx import convert
        text = convert('POSCAR', pol='on', magmom='-1 1 3*0', output='openmx.dat')
    """
    unknown = set(params) - set(DEFAULTS)
    if unknown:
        raise TypeError(f"unknown parameter(s): {', '.join(sorted(unknown))}")
    params = {**DEFAULTS, **params, 'output': output}
    if parameter_file:
        params.update(input_parameter_reader(parameter_file))

    full_input_str = build_input(poscar, params)
    if params['output']:
        with open(params['output'], 'w') as f:
            f.write(full_input_str)
        logger.info(f"Written {params['output']}")
    return full_input_str
