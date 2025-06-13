# Usage

## Basic Usage

### Simplest (default parameters)
```bash
./poscar2openmx.py example/POSCAR
```

### Command Line Arguments
```bash
./poscar2openmx.py example/POSCAR --pol nc -o output.dat --xc GGA-PBE --element_order Fe O La Se
```

### Combining Command Line Parameters with External Input File
```bash
./poscar2openmx.py example/POSCAR --parameter_file example/param_file --element_order Fe O La S
```

### Band Structure Calculations
If the `seekpath` package is installed, you can use the `-b` or `--band` flag to generate high symmetry point paths for band calculations:

```bash
./poscar2openmx.py example/POSCAR --pol nc -o output.dat --band on
```

To install `seekpath`:
```bash
pip install seekpath
```

## Important Note

Parameters specified in the parameter file will override command line parameters.

Currently, custom defined basis set can only be specified in the external file through --parameter_file.
