import configparser
import ast # For safely evaluating a string containing a Python literal
import os

def input_parameter_reader(config_file):

    config = configparser.ConfigParser()
    param_keys = ['xc','pol','output','coord_system','basis_prec','band','magmom','vector_file']

    basis_dict = None
    if os.path.exists(config_file):
        try:
            config.read(config_file)
            if 'settings' in config:
                settings = config['settings']

                param = {key: settings.get(key) for key in param_keys if settings.get(key) != None }

                # Read the 'basis' string and convert to dictionary
                basis_str = settings.get('basis')
                if basis_str:
                    try:
                        # Safely evaluate the string to a Python dictionary
                        basis_dict = ast.literal_eval(basis_str)
                        if not isinstance(basis_dict, dict):
                            print(f"Warning: 'basis' in {config_file} is not a valid dictionary. Got: {basis_dict}")
                            basis_dict = None # Reset if not a dict
                    except (ValueError, SyntaxError) as e:
                        print(f"Error parsing 'basis' from {config_file} as a dictionary: {e}")
                        basis_dict = None # Reset on error

        except configparser.Error as e:
            print(f"Error reading configuration file {config_file}: {e}")

    if settings.get('element_order'):
        param['element_order'] = settings.get('element_order').split(' ')

    if basis_dict:
        [print(basis_dict[x]) for x in basis_dict.keys()]
        param['basis'] = basis_dict
    else:
        print("No basis set specified")

    return param


#if __name__ == '__main__':
#    param, basis_dict = input_parameter_reader()
