# Usage

## input parameters 
./poscar2openmx.py  --help

```
usage: poscar2openmx.py [-h] [--parameter_file PARAMETER_FILE]
                        [--xc {LDA,LSDA-CA,LSDA-PW,GGA-PBE}] [--pol {on,off,nc}]
                        [-o OUTPUT] [-c {F,C}] [-v BASIS_VER]
                        [-p {Quick,Standard,Precise}] [-b {on,off}]
                        [--element_order [ELEMENT_ORDER ...]]
                        poscar

Convert VASP POSCAR to OpenMX input format

positional arguments:
  poscar                POSCAR file to convert

options:
  -h, --help            show this help message and exit
  --parameter_file PARAMETER_FILE
                        read input parameters from a file.
  --xc {LDA,LSDA-CA,LSDA-PW,GGA-PBE}
                        functionals (default: GGA-PBE)
  --pol {on,off,nc}     spin polarization type
  -o OUTPUT, --output OUTPUT
                        Output OpenMX file name (default: openmx_input.dat)
  -c {F,C}, --coord_system {F,C}
                        output coordinate system (F)raction/Direct or (C)artesian (default=F)
  -p {Quick,Standard,Precise}, --basis_prec {Quick,Standard,Precise}
                        basis accuracy (default: Quick)
  -b {on,off}, --band {on,off}
                        band structure
  --element_order [ELEMENT_ORDER ...]
                        A list of element symbols (e.g., O La Fe Se), defines how elements will be sorted
```

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

Three built-in options (--basis_prec) for basis set are extracted from the OpenMX official website https://www.openmx-square.org/openmx_man3.9/node27.html
Currently, custom defined basis set can only be specified in the external file through --parameter_file.

For magnetic systems, the magnetic moments need to be adjusted manually.

