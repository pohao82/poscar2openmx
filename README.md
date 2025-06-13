# Usage

## Basic Usage

### Simplest (default parameters)
```bash
./poscar2openmx.py ../examples/POSCAR
```

### Command Line Arguments
```bash
./poscar2openmx.py ../examples/POSCAR --pol nc -o output.dat --xc GGA-PBE --element_order Fe O La Se
```

### Combining Command Line Parameters with External Input File
```bash
./poscar2openmx.py ../examples/POSCAR --input_param input_param --element_order Fe O La Se
```

### Band Structure Calculations
If the `seekpath` package is installed, you can use the `-b` or `--band` flag to generate high symmetry point paths for band calculations:

```bash
./poscar2openmx.py ../examples/POSCAR --pol nc -o output.dat --band on
```

To install `seekpath`:
```bash
pip install seekpath
```

## Important Note

Parameters specified in the parameter file will override command line parameters.
