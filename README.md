````markdown
# Usage

**Note on Execution: After installation via pip install -e ., the package makes the script available as a direct command. It is executed simply as poscar2openmx instead of running the Python file (./poscar2openmx.py).
**Added support for moments

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
    ```

3.  **Install in editable mode:**
    ```bash
    pip install -e .
    ```

## input parameters 
poscar2openmx  --help

````

usage: poscar2openmx [-h] [--parameter_file PARAMETER_FILE]
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
  --magmom MAGMOM       vasp MAGMOM string
  --vector_file VECTOR_FILE
                        (Alternative input for moments) file that stores the vector (cartesian) as a natoms-by-3 array

````
## Basic Usage

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

## Important Note

  * Parameters specified in the **parameter file will override command line parameters**.
  * Do not use quotation marks inside the parameter_file (i.e. vec_file rather than 'vec_file'), Unless it's inside the basis dictionary.
  * Currently, custom defined basis set can only be specified in the external file through `--parameter_file`.
  * Three built-in options (`--basis_prec`) for basis set are extracted from the OpenMX official website.

<!-- end list -->

