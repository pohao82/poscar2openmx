"""
Default conversion parameters, shared by the command line, the parameter file
reader and the Python API.
"""

DEFAULTS = {
    'xc': 'GGA-PBE',
    'pol': 'on',
    'output': 'openmx_input.dat',
    'coord_system': 'F',
    'basis_ver': '19',
    'basis_prec': 'Quick',
    'band': 'off',
    'element_order': None,
    'magmom': None,
    'vector_file': None,
    'basis': None,       # custom {element: basis} dict, parameter file / API only
    'kspacing': 35.0,    # automatic k-grid: n_i >= kspacing / d_i (Angstrom)
    'kgrid': None,       # explicit [n1, n2, n3], overrides kspacing
}

# allowed values, in the canonical spelling the rest of the code expects
CHOICES = {
    'xc': ['LDA', 'LSDA-CA', 'LSDA-PW', 'GGA-PBE'],
    'pol': ['on', 'off', 'nc'],
    'coord_system': ['F', 'C'],
    'basis_prec': ['Quick', 'Standard', 'Precise'],
    'band': ['on', 'off'],
}
# matched on the first letter only (e.g. q, Quick, standard, cart)
FIRST_LETTER_KEYS = {'coord_system', 'basis_prec'}
# extra first-letter aliases: D(irect) is fractional in VASP
ALIASES = {'coord_system': {'D': 'F'}}


def normalize_choice(key, value):
    """
    Return the canonical spelling of a choice parameter, case-insensitive.
    coord_system and basis_prec only compare the first letter; the others need
    the full word because their first letters are ambiguous (on/off, LDA/LSDA).
    Raises ValueError for an invalid value.
    """
    if value is None or key not in CHOICES:
        return value
    v = str(value).strip()
    if key in FIRST_LETTER_KEYS:
        letter = v[:1].upper()
        letter = ALIASES.get(key, {}).get(letter, letter)
        matches = [c for c in CHOICES[key] if c[0].upper() == letter]
    else:
        matches = [c for c in CHOICES[key] if c.upper() == v.upper()]
    if not matches:
        raise ValueError(f"invalid {key} '{value}', choose from {', '.join(CHOICES[key])}")
    return matches[0]


def normalize_params(params):
    """Canonical spelling for every choice parameter in a params dict (in place)."""
    for key in CHOICES:
        if key in params:
            params[key] = normalize_choice(key, params[key])
    return params
