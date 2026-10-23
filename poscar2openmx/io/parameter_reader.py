import configparser
import ast # For safely evaluating a string containing a Python literal
import logging
import os

logger = logging.getLogger(__name__)


def input_parameter_reader(config_file):
    """
    Read the [settings] section of a parameter file into a dict with the same keys
    as poscar2openmx.defaults.DEFAULTS. Only keys present in the file are returned.
    """
    if not os.path.exists(config_file):
        raise FileNotFoundError(f"parameter file {config_file} not found")

    config = configparser.ConfigParser()
    # plain string values
    param_keys = ['xc','pol','output','coord_system','basis_ver','basis_prec','band','magmom','vector_file']

    try:
        config.read(config_file)
    except configparser.Error as e:
        raise ValueError(f"Error reading configuration file {config_file}: {e}")
    if 'settings' not in config:
        raise ValueError(f"parameter file {config_file} has no [settings] section")
    settings = config['settings']

    param: dict = {key: settings.get(key) for key in param_keys if settings.get(key) != None }

    element_order = settings.get('element_order')
    if element_order:
        param['element_order'] = element_order.split()

    kspacing = settings.get('kspacing')
    if kspacing:
        param['kspacing'] = float(kspacing)

    kgrid_str = settings.get('kgrid')
    if kgrid_str:
        kgrid = [int(n) for n in kgrid_str.split()]
        if len(kgrid) != 3:
            raise ValueError(f"kgrid in {config_file} needs 3 integers, got {kgrid_str}")
        param['kgrid'] = kgrid

    # Read the 'basis' string and convert to dictionary
    basis_str = settings.get('basis')
    if basis_str:
        try:
            # Safely evaluate the string to a Python dictionary
            basis_dict = ast.literal_eval(basis_str)
        except (ValueError, SyntaxError) as e:
            raise ValueError(f"Error parsing 'basis' from {config_file} as a dictionary: {e}")
        if not isinstance(basis_dict, dict):
            raise ValueError(f"'basis' in {config_file} is not a valid dictionary. Got: {basis_dict}")
        param['basis'] = basis_dict
    else:
        logger.info("No basis set specified in parameter file")

    logger.info(f"parameters from {config_file}: {param}")
    return param
