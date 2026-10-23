# Usage

**Note on Execution: After installation via pip install -e ., the package makes the script available as a direct command. It is executed simply as poscar2openmx instead of running the Python file (./poscar2openmx.py).
**Added support for moments

## What's new

- **Example input:** `poscar2openmx --example` copies a ready-to-run example (`input_example_HoAgGe`) into the current folder and prints the standard commands. Running `poscar2openmx` with no arguments only prints a short hint.
- **Automatic k-point grid:** `scf.Kgrid` is now chosen from the cell size (n_i × d_i ≥ 35 Å) instead of a fixed `4 4 4`. Adjust it with `--kspacing`, or set it directly with `--kgrid`.
- **Python API:** `from poscar2openmx import convert` returns the OpenMX input as text and can also write it to a file. Moments can be passed as a MAGMOM string or an array.
- **Elements missing from the basis database** (e.g. Eu, Gd, Tb, Er, Tm, Yb) no longer crash the conversion. The output gets placeholders to edit by hand, and a warning is printed.
- **Case-insensitive options:** `-p standard`, `-c c`, `--pol NC` etc. now work. `--basis_prec` and `--coord_system` only look at the first letter.
- **Clearer errors:** bad input stops with a short `Error: ...` message instead of a traceback or a silent exit. This covers an `element_order` that doesn't match the POSCAR, a moment count that doesn't match the number of atoms, a missing parameter file, and an invalid `basis`.
- **Parameter file:** now also accepts `basis_ver`, `kspacing` and `kgrid`.
- **Fixes:** corrected the Ag basis in the HoAgGe example `params_file`. Fixed the example commands in `commandline_examples.txt`.

## 🚀 Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/pohao82/poscar2openmx.git
    cd poscar2openmx
    ```

2.  **(Optional) In case you want to use a virtual environment:**
    ```bash
    # Using Conda
    conda create -n venv python=3.11
    conda activate venv 

    # Or using Python's built-in venv (Python >= 3.8)
    python3 -m venv .venv
    source .venv/bin/activate      # Windows: .venv\Scripts\activate
    ```

3.  **Install in editable mode:**
    ```bash
    pip install -e .
    # with test dependencies (pytest)
    pip install -e ".[test]"
    ```

## input parameters 
poscar2openmx  --help

```

usage: poscar2openmx [-h] [--example] [--parameter_file PARAMETER_FILE]
                     [--xc {LDA,LSDA-CA,LSDA-PW,GGA-PBE}] [--pol {on,off,nc}]
                     [-o OUTPUT] [-c {F,C}] [-v BASIS_VER]
                     [-p {Quick,Standard,Precise}] [-b {on,off}]
                     [--element_order [ELEMENT_ORDER ...]]
                     poscar_file

Convert VASP POSCAR to OpenMX input format

positional arguments:
  poscar                POSCAR file to convert

options:
  -h, --help            show this help message and exit
  --example             copy an example input to ./input_example_HoAgGe and show how to run it
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
  --magmom MAGMOM       vasp MAGMOM string (enclose values with quotation marks).
  --vector_file VECTOR_FILE
                        (Alternative input for moments) file that stores the vector (cartesian) as a natoms-by-3 array
  --kspacing KSPACING   automatic k-grid, n_i = ceil(kspacing / d_i) with d_i the lattice-plane spacing in Ang (default: 35)
  --kgrid N1 N2 N3      explicit k-grid, overrides --kspacing

```
## Basic Usage

### Getting started: example input
```bash
poscar2openmx --example
```
Running `poscar2openmx` with no arguments only prints a short hint. `--example` copies an example input folder, `input_example_HoAgGe` (54-atom HoAgGe, noncollinear), into the current folder and prints the standard commands. An existing folder with that name is not overwritten. It contains the POSCAR (cartesian and fractional), a `params_file` with every supported parameter, a `vec_file`, a `magmom_string` and `commandline_examples.txt`.

### Simplest (default parameters)
```bash
poscar2openmx hoagge.poscar.cart
````

### Command Line Arguments

```bash
poscar2openmx hoagge.poscar.cart --pol nc -o output.dat --xc GGA-PBE --element_order Ag Ge Ho 
```

### Combining Command Line Parameters with External Input File

```bash
poscar2openmx hoagge.poscar.cart --pol nc -o output.dat --parameter_file params_file
```

### The spin moments can be specified through commandline using either VASP magmom string (--magmom)
the spin moments can now be specified directly using two new command-line options. $N$ is the number of atoms.
If pol=on (collinear), while the specified moments are noncollinear, only Mx components will be read.

### 1\. Using a VASP-style MAGMOM string:

The input is the VASP `MAGMOM` string.

```bash
poscar2openmx hoagge.poscar.cart --pol nc -o output.dat --parameter_file params_file --magmom '108*0 0 5.5  0 -0 -5.5  0 -0 -5.5  0 0  5.5  0 0  5.5  0 0  5.5  0 4.7631  2.75  0 4.7631  2.75  0 -4.7631 -2.75  0 -4.7631 -2.75  0 4.7631  2.75  0 4.7631  2.75  0 4.7631 -2.75  0 -4.7631  2.75  0 -4.7631  2.75  0 -4.7631  2.75  0 -4.7631  2.75  0 4.7631 -2.75  0' 
```

### 2\. Using an external vector file:

Specify a file that stores the vector as an $N$-by-3 array.

```bash
poscar2openmx hoagge.poscar.cart --pol nc -o output.dat --parameter_file params_file --vector_file vec_file 
```
  * Both flags can also be specified inside the parameter file (see examples.) 
  * Only one can be used at a time, if --magmom and vector_file are used, an error will occur.


## Band Structure Calculations
If the `seekpath` package is installed, you can use the `-b` or `--band` flag to generate high symmetry point paths for band calculations:

```bash
poscar2openmx  hoagge.poscar.cart --pol nc -o output.dat --band on
```

To install `seekpath`:

```bash
pip install seekpath
```

## k-point grid
`scf.Kgrid` is set automatically so that n_i × d_i ≥ 35 Å along each direction, where d_i is the spacing between lattice planes (equal to the lattice constant for orthogonal cells). Change the target with `--kspacing`, or give the grid directly with `--kgrid 6 6 1`. Both can also go in the parameter file (`kspacing = 35`, `kgrid = 6 6 1`). For slabs, set the vacuum direction to 1 with `--kgrid`.

## Python API
```python
from poscar2openmx import convert

# returns the input file as a string; writes it only when output is given
text = convert('V2Se2O.cube_1F.vasp', pol='on', magmom='-1 1 3*0', output='openmx.dat')

# moments can also be a list/array (N values for collinear, N-by-3 for noncollinear)
text = convert('POSCAR', pol='nc', magmom=moments_array, kgrid=[6, 6, 1])

# the parameter file works the same way as on the command line (it overrides keyword arguments)
text = convert('POSCAR', parameter_file='params_file')
```
All keyword arguments and their defaults are in `poscar2openmx.DEFAULTS`. Informational messages go through Python `logging` (hidden by default in scripts); warnings, such as a missing basis, are still shown.

## Elements missing from the basis database
Some elements (e.g. Eu, Gd, Tb, Er, Tm, Yb) have no entry in the built-in basis database. The conversion still runs and prints a warning, and the output contains placeholders to edit by hand:
  * a placeholder basis (`<El>8.0-s2p2d2f1`) unless a basis is given for that element in the parameter file,
  * `X` for the up/down electron counts, with a comment saying what to replace them with,
  * Hubbard U = 7.0 on the first shell of the highest orbital (e.g. `1f 7.0`); J stays 0.

## Tests
```bash
pip install -e ".[test]"
pytest
```
`tests/golden/` holds reference output files. After an intended change to the output, regenerate them with `UPDATE_GOLDEN=1 pytest tests/test_golden.py` and review the diff.

## Important Note
  * Option values are case-insensitive, on the command line and in the parameter file. `--basis_prec` and `--coord_system` only look at the first letter (`q`, `standard`, `P`; `f`, `cart`, `Direct`). `--xc`, `--pol` and `--band` need the full word (e.g. `gga-pbe`, `NC`, `on`) because their first letters are shared.

  * Parameters specified in the **parameter file will override command line parameters**.
  * Do not use quotation marks inside the parameter_file (i.e. vec_file rather than 'vec_file'), Unless it's inside the basis dictionary.
  * Currently, custom defined basis set can only be specified in the external file through `--parameter_file`.
  * Three built-in options (`--basis_prec`) for basis set are extracted from the OpenMX official website.

