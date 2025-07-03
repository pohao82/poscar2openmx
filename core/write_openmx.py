import numpy as np
import json
import os.path
import sys 

from .expand_basis import expand_basis
from .omx_optimized_bases import omx_basis_data
from .symbol2atomicN import Zatom
from .read_poscar import read_poscar
from .get_bandpath import get_bandpath

def write_openmx(structure, param):
    """Write OpenMX .dat input file"""

    output_filename = param.output
    spin_pol = param.pol.lower()
    xc_info = param.xc.upper()
    basis_ver = param.basis_ver
    band = param.band.lower()
    custom_order = param.element_order

    noncollinear = True
    # basis set parameters
    xc_parts = xc_info.split('-')
    if xc_parts[0]=='GGA':
        xc_type='PBE'
    else :
        xc_type='CA'

    basis_accuracy = param.basis_prec # "Standard"
    basis_external = None
    if hasattr(param,'basis'):
        basis_external = param.basis # manually specified in the file read in using --parameter_file flag

    #print('external bases')
    #print(basis_external)

    # output coordinate system
    coord_system = param.coord_system.upper() # 'F'
    # Convert coordinate system
    positions = []
    # four scenarios
    latvec = structure['lattice']
    if structure['direct'] and coord_system=='C':
        for element, pos in structure['positions']:
            cart_pos = np.dot(pos,latvec)
            positions.append((element, cart_pos))
    elif (not structure['direct']) and coord_system=='F':
        # C -> F, divided by lattice vectors
        inv_latvec = np.linalg.inv(latvec)
        for element, pos in structure['positions']:
            frac_pos = np.dot(pos, inv_latvec)
            positions.append((element, frac_pos))
    else: # (structuce['direct'] and coord_system=='f') or (structuc['direct']==false and coord_system=='c')
        for element, pos in structure['positions']:
            positions.append((element, pos))

    if coord_system == 'F':
        coord_unit = 'Frac'
    else:
        coord_unit = 'Ang'

    # Calculate the total number of atoms
    total_atoms = sum(structure['atom_counts'])

    # Create a simple OpenMX input file
    with open(output_filename, 'w') as f:
        f.write("#\n# OpenMX input file generated from VASP POSCAR\n")
        f.write(f"# Original comment: {structure['comment']}\n#\n\n")

        # System settings
        f.write("System.Name   system\n")
        f.write("System.CurrentDirectory    ./\n")
        f.write("level.of.stdout   1 \n");
        f.write("level.of.fileout  0 \n");
        f.write("HS.fileout        on     # on|off, default=off \n");
        f.write("DATA.PATH  /home/pchang8/software/openmx/openmx3.9/DFT_DATA19 \n\n");
        # Species and atoms
        unique_elements = set([p[0] for p in positions])
        f.write(f"Species.Number       {len(unique_elements)}\n")

        # tract the basis set 
        f.write("<Definition.of.Atomic.Species\n")
        unique_bases = {}
        for i, element in enumerate(unique_elements):

            # database has only PBE but doesn't matter
            # only used to find basis set def
            element_info=f"{element}_PBE{basis_ver}"

            # default ultrasoft potential
            if element in ['Fe','Co','Ni','Cu','Zn']:
                element_info +='S'

            if basis_external:
                basis = basis_external[element]
            else:
                basis = omx_basis_data[element_info][basis_accuracy]

            basis_parts = basis.split('-')
            pao_basis = basis_parts[1]
            # check if pp type is Hard, Soft or standard
            pp_type = basis_parts[0][-1]
            xc_basis = f"{element}_{xc_type}{basis_ver}"
            if pp_type in ['H','S']:
                # if H  overwrite
                element_info=f"{element}_PBE{basis_ver}"+pp_type
                xc_basis = xc_basis + pp_type

            n_valence = omx_basis_data[element_info]["Valence electrons"]

            if element in ['V','Cr','Mn','Fe','Co','Ni','Cu','Zn']:
                nve = [float(n_valence)/2+1,float(n_valence)/2-1]
            else:
                nve = [float(n_valence)/2,float(n_valence)/2]

            unique_bases[element] = {"basis":pao_basis, "n_valence":nve}

            f.write(f" {element:<4} {basis:<16} {xc_basis}\n")

        f.write("Definition.of.Atomic.Species>\n")
        f.write("\n")

        # Write lattice vectors (in Angstrom)
        f.write("Atoms.UnitVectors.Unit  Ang\n")
        f.write("<Atoms.UnitVectors \n")
        for i in range(3):
            f.write(f"  {structure['lattice'][i][0]:.6f}  {structure['lattice'][i][1]:.6f}  {structure['lattice'][i][2]:.6f}\n")
        f.write("Atoms.UnitVectors> \n\n")

        # Atomic positions (in Angstrom)
        f.write(f"Atoms.Number        {total_atoms}\n")
        f.write(f"Atoms.SpeciesAndCoordinates.Unit  {coord_unit}\n")

        # loop over atoms
        f.write("<Atoms.SpeciesAndCoordinates\n")
        atom_index = 1
        atomic_numbers = []

        # recorder according to custom_order
        #custom_order = ['O','La', 'Fe', 'Se']

        if custom_order != None:

            print(custom_order)
            if set(custom_order) != set(unique_elements):
                print( set(custom_order)!=set(unique_elements))
                print('Error: inconsistent input elements. Check if all the atomic speices defined in --element_reorder exist in POSCAR')
                sys.exit()
            #[print(position) for position in positions]
            # reorder 
            # Create a mapping from the element symbol to its position in the custom order
            # This dictionary will help the sorting function understand the desired sequence.
            order_map = {symbol: index for index, symbol in enumerate(custom_order)}
            # Sort the list using the `sort()` method with a lambda function as the key.
            # The lambda function extracts the element symbol (the first item of each tuple, item[0])
            # and then uses `order_map` to find its sorting index.
            positions.sort(key=lambda item: order_map[item[0]])
            #print('reordered')
            #[print(position) for position in positions]


        for element, pos in positions:
            species_index = list(unique_elements).index(element) + 1
            n_up = unique_bases[element]["n_valence"][0] 
            n_dn = unique_bases[element]["n_valence"][1] 
            #noncol_angles = 's_theta s_phi orb_theta orb_phi 0' 
            noncol_angles = '' 
            if spin_pol.lower()=='nc':
                noncol_angles = '0.0   0.0   0.0   0.0  1'
            f.write(f"  {atom_index:2}  {element:2}   {pos[0]: .8f}   {pos[1]: .8f}   {pos[2]: .8f}  {n_up}  {n_dn}   {noncol_angles} on\n")
            atom_index += 1
            atomic_numbers.append(Zatom.index(element)+1)
        f.write("Atoms.SpeciesAndCoordinates>\n\n")

        # DFT+U
        # U
        f.write("<Hubbard.U.values\n")
        for i, element in enumerate(unique_elements):
            bases=expand_basis(unique_bases[element]['basis'])
            f.write(f" {element:3}  {bases} \n")
        f.write("Hubbard.U.values>\n\n")

        # if Hubbard.Occupation is full
        f.write("<Hubbard.J.values\n")
        for i, element in enumerate(unique_elements):
            bases=expand_basis(unique_bases[element]['basis'])
            f.write(f" {element:3}  {bases} \n")
        f.write("Hubbard.J.values>\n\n")

        # Add some common OpenMX parameters
        f.write(f"scf.XcType                 {xc_info}   # LDA|LSDA-CA|LSDA-PW|GGA-PBE\n")
        f.write(f"scf.SpinPolarization       {spin_pol}  # On|Off|NC\n")
        f.write("scf.Hubbard.U              off\n")
        f.write("scf.Hubbard.Occupation     dual\n")
        f.write("scf.spinorbit.coupling     off\n")
        f.write("scf.ElectronicTemperature  300.0        # default=300 (K)\n")
        f.write("scf.energycutoff           250.0        # default=150 (Ry)\n")
        f.write("scf.EigenvalueSolver       band\n")
        f.write("scf.Kgrid                  4 4 4\n")
        # mixing parameters 
        f.write("scf.maxIter                100\n")
        f.write("scf.Mixing.Type            rmm-diish    # Simple|Rmm-Diis|Gr-Pulay|Kerker|Rmm-Diisk|rmm-dissh\n")
        f.write("scf.Init.Mixing.Weight     0.30\n")
        f.write("scf.Min.Mixing.Weight      0.002\n")
        f.write("scf.Max.Mixing.Weight      0.40\n")
        f.write("scf.Mixing.History         15\n")
        f.write("scf.Mixing.StartPulay      10\n")
        f.write("#scf.Mixing.EveryPulay     6\n")
        f.write("scf.criterion              1.0e-6\n")
        f.write("scf.restart                off          # on|off|c2n\n\n")

        f.write("scf.Constraint.NC.Spin     off          # on|off, default=off\n")
        f.write("scf.Constraint.NC.Spin.v   0.5         # default=0.0(eV)\n")

        # For MFT
        f.write("# The Following is useful for magnetic force theorem, where soc is included as PT\n")
        f.write("# if restart = c2n\n")
        f.write("#scf.Restart.Spin.Angle.Theta   90.0\n")
        f.write("#scf.Restart.Spin.Angle.Phi      0.0\n")

        f.write("\n# Some additional flags\n")
        f.write("Voronoi.charge              off\n")
        f.write("#scf.Electric.Field         0.0 0.0 1.0\n")
        f.write("#scf.system.charge          0.0\n")
        f.write("\n")

        f.write("MD.Type nomd # Nomd|Opt|NVE|NVT_VS|NVT_NH\n\n")

        # --------------------------
        #      post-processing
        # --------------------------

        # Band structure 
        if band == 'on':
            # use Seek-path to generate high-symmetry points
            coords_array = np.array([site[1] for site in positions])
            if coord_system != 'F' :
                inv_latvec = np.linalg.inv(latvec)
                coords_array = coords_array @ inv_latvec

            kpaths = get_bandpath(coords_array,latvec,atomic_numbers)
            if kpaths == []:
                band = 'off'

        else:
            # some template in case you need that
            kpaths = [' 50  0.000000  0.000000  0.000000   0.500000  0.000000 0.000000  G X',
                      ' 50  0.000000  0.000000  0.000000   0.000000  0.500000 0.000000  G Y']

        npaths = len(kpaths) # number of paths
        f.write(f"Band.dispersion  {band}\n") 
        f.write(f"Band.Nkpath  {npaths}\n")
        f.write("<Band.kpath\n")
        if kpaths:
            [f.write(f"{path}\n") for path in kpaths]
        f.write("Band.kpath>\n\n") 

        # Density-of-states
        f.write("Dos.fileout        off        # on|off, default=off\n") 
        f.write("Dos.Erange        -8.0  8.0   # default=-20 20\n") 
        f.write("Dos.Kgrid          15 15 15   # default=Kgrid1 Kgrid2 Kgrid3\n") 
