- simplest (use default parameters)
./poscar2openmx.py  ../examples/POSCAR 

- Use commenline argument
./poscar2openmx.py  ../examples/POSCAR --pol nc -o output.dat --xc GGA-PBE --element_order Fe O La Se

- combine commandline parameters with external input file 
./poscar2openmx.py  ../examples/POSCAR --input_param input_param  --element_order Fe O La Se

- If the package seek-path is installed, one can use -b or --band flag to generate high symmetry point path for band calculations
./poscar2openmx.py  ../examples/POSCAR --pol nc -o output.dat --band on

Install seek-path:
pip install seekpath

Note that the whatever specified in the paramter file will overwrite the command line paramters. 
