import numpy as np
import json
import os.path
import sys 

from poscar2openmx.utils.expand_basis import expand_basis
from poscar2openmx.utils.omx_optimized_bases import omx_basis_data
from poscar2openmx.utils.symbol2atomicN import Zatom
#from .read_poscar import read_poscar
from poscar2openmx.utils.get_bandpath import get_bandpath

def write_openmx_str(structure, param):
    """Write OpenMX .dat input file"""

    #output_filename = param['output']
    spin_pol = param['pol'].lower()
    xc_info = param['xc'].upper()
    basis_ver = param['basis_ver']
    band = param['band'].lower()
    custom_order = param['element_order']

    basis_accuracy = param['basis_prec'] # "Standard"
    basis_external = None
    if param.get('basis') is not None:
        basis_external = param['basis'] # manually specified in the file read in using --parameter_file flag
    #print('external bases')
    #print(basis_external)
    # output coordinate system
    coord_system = param['coord_system'].upper() # 'F'
    magmom = param['magmom']

    # basis set parameters
    xc_parts = xc_info.split('-')
    if xc_parts[0]=='GGA':
        xc_type='PBE'
    else :
        xc_type='CA'

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

    content_lines = []
    # Create a simple OpenMX input file
    content_lines.append("#\n# OpenMX input file generated from VASP POSCAR\n")
    content_lines.append(f"# Original comment: {structure['comment']}\n#\n\n")

    # System settings
    content_lines.append("System.Name   system\n")
    content_lines.append("System.CurrentDirectory    ./\n")
    content_lines.append("level.of.stdout   1 \n")
    content_lines.append("level.of.fileout  0 \n")
    content_lines.append("HS.fileout        on     # on|off, default=off \n")
    content_lines.append("DATA.PATH  /home/pchang8/software/openmx/openmx3.9/DFT_DATA19 \n\n")
    # Species and atoms
    #unique_elements = set([p[0] for p in positions])
    unique_elements = list(dict.fromkeys(p[0] for p in positions))
    content_lines.append(f"Species.Number       {len(unique_elements)}\n")

    # tract the basis set 
    content_lines.append("<Definition.of.Atomic.Species\n")
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

        content_lines.append(f" {element:<4} {basis:<16} {xc_basis}\n")

    content_lines.append("Definition.of.Atomic.Species>\n")
    content_lines.append("\n")

    # Write lattice vectors (in Angstrom)
    content_lines.append("Atoms.UnitVectors.Unit  Ang\n")
    content_lines.append("<Atoms.UnitVectors \n")
    for i in range(3):
        content_lines.append(f"  {structure['lattice'][i][0]:.6f}  {structure['lattice'][i][1]:.6f}  {structure['lattice'][i][2]:.6f}\n")
    content_lines.append("Atoms.UnitVectors> \n\n")

    # Atomic positions (in Angstrom)
    content_lines.append(f"Atoms.Number        {total_atoms}\n")
    content_lines.append(f"Atoms.SpeciesAndCoordinates.Unit  {coord_unit}\n")

    # loop over atoms
    content_lines.append("<Atoms.SpeciesAndCoordinates\n")
    atom_index = 1
    atomic_numbers = []

    if custom_order != None:
        print('custom_order')
        print(custom_order)
        if set(custom_order) != set(unique_elements):
            print( set(custom_order)!=set(unique_elements))
            print('Error: inconsistent input elements. Check if all the atomic speices defined in --element_reorder exist in POSCAR')
            sys.exit()
        # reorder 
        # Create a mapping from the element symbol to its position in the custom order
        # This dictionary will help the sorting function understand the desired sequence.
        order_map = {symbol: index for index, symbol in enumerate(custom_order)}
        # Sort the list using the `sort()` method with a lambda function as the key.
        # The lambda function extracts the element symbol (the first item of each tuple, item[0])
        # and then uses `order_map` to find its sorting index.

        #positions.sort(key=lambda item: order_map[item[0]])
        # -----------------------------------------------------------
        # 1. Create a list of indices [0, 1, 2, ..., 8]
        indices = list(range(len(positions)))
        # 2. Sort the indices based on the element symbol in the original 'positions' list
        # The lambda function takes an index 'i' and looks up the corresponding element in positions.
        sorted_indices = sorted(indices, key=lambda i: order_map[positions[i][0]])
        print(f"Original index order after sorting: {sorted_indices}")
        # Expected output: [0, 1, 2, 3, 4, 5, 6, 7, 8] (because it's already sorted by Dy, then Ag, then Ge)
        # If positions were shuffled, this list would be different.
        # 3. Rebuild both lists using the sorted_indices map
        positions = [positions[i] for i in sorted_indices]
        if magmom is not None:
            magmom   = [magmom[i] for i in sorted_indices]

    # No moment specified, use default
    if magmom is None:
        for element, pos in positions:
            species_index = list(unique_elements).index(element) + 1
            n_up = unique_bases[element]["n_valence"][0] 
            n_dn = unique_bases[element]["n_valence"][1] 
            #noncol_angles = 's_theta s_phi orb_theta orb_phi 0' 
            noncol_angles = '' 
            if spin_pol.lower()=='nc':
                noncol_angles = '0.0   0.0   0.0   0.0  1'
            content_lines.append(f"  {atom_index:2}  {element:2}   {pos[0]: .8f}   {pos[1]: .8f}   {pos[2]: .8f} {n_up:5.2f} {n_dn:5.2f} {noncol_angles} on\n")
            atom_index += 1
            atomic_numbers.append(Zatom.index(element)+1)
    else:
        # combine positions with moments
        coord_mom = [
            (symbol, coords, moment) 
            for (symbol, coords), moment in zip(positions, magmom)
        ]

        for element, pos, moment in coord_mom:
            species_index = list(unique_elements).index(element) + 1
            n_elec = unique_bases[element]["n_valence"][0]+unique_bases[element]["n_valence"][1] 

            mag   = moment[0]
            n_up = (n_elec + mag)/2
            n_dn = (n_elec - mag)/2

            noncol_angles = '' 
            if spin_pol.lower()=='nc':
                theta = moment[1]
                phi   = moment[2]
                noncol_angles = f'  {theta:7.2f} {phi:7.2f} {theta:7.2f} {phi:7.2f} 1 on'

            content_lines.append(f"  {atom_index:2}  {element:2}   {pos[0]: .8f}   {pos[1]: .8f}   {pos[2]: .8f}  {n_up:5.2f}  {n_dn:5.2f}{noncol_angles}\n")
            atom_index += 1
            atomic_numbers.append(Zatom.index(element)+1)

    content_lines.append("Atoms.SpeciesAndCoordinates>\n\n")

    # DFT+U
    content_lines.append("<Hubbard.U.values\n")
    for i, element in enumerate(unique_elements):
        bases=expand_basis(unique_bases[element]['basis'])
        content_lines.append(f" {element:3}  {bases} \n")
    content_lines.append("Hubbard.U.values>\n\n")

    # if Hubbard.Occupation is full
    content_lines.append("<Hubbard.J.values\n")
    for i, element in enumerate(unique_elements):
        bases=expand_basis(unique_bases[element]['basis'])
        content_lines.append(f" {element:3}  {bases} \n")
    content_lines.append("Hubbard.J.values>\n\n")

    # Add some common OpenMX parameters
    content_lines.append(f"scf.XcType                 {xc_info}   # LDA|LSDA-CA|LSDA-PW|GGA-PBE\n")
    content_lines.append(f"scf.SpinPolarization       {spin_pol}  # On|Off|NC\n")
    content_lines.append("scf.Hubbard.U              off\n")
    content_lines.append("scf.Hubbard.Occupation     dual\n")
    content_lines.append("scf.spinorbit.coupling     off\n")
    content_lines.append("scf.ElectronicTemperature  300.0        # default=300 (K)\n")
    content_lines.append("scf.energycutoff           250.0        # default=150 (Ry)\n")
    content_lines.append("scf.EigenvalueSolver       band\n")
    content_lines.append("scf.Kgrid                  4 4 4\n")
    # mixing parameters 
    content_lines.append("scf.maxIter                100\n")
    content_lines.append("scf.Mixing.Type            rmm-diish    # Simple|Rmm-Diis|Gr-Pulay|Kerker|Rmm-Diisk|rmm-dissh\n")
    content_lines.append("scf.Init.Mixing.Weight     0.30\n")
    content_lines.append("scf.Min.Mixing.Weight      0.002\n")
    content_lines.append("scf.Max.Mixing.Weight      0.40\n")
    content_lines.append("scf.Mixing.History         15\n")
    content_lines.append("scf.Mixing.StartPulay      10\n")
    content_lines.append("#scf.Mixing.EveryPulay     6\n")
    content_lines.append("scf.criterion              1.0e-6\n")
    content_lines.append("scf.restart                off          # on|off|c2n\n\n")

    content_lines.append("scf.Constraint.NC.Spin     off          # on|off, default=off\n")
    content_lines.append("scf.Constraint.NC.Spin.v   0.5         # default=0.0(eV)\n")

    # For MFT
    content_lines.append("\n# The Following is useful for magnetic force theorem, where soc is included as PT\n")
    content_lines.append("# if restart = c2n\n")
    content_lines.append("#scf.Restart.Spin.Angle.Theta   90.0\n")
    content_lines.append("#scf.Restart.Spin.Angle.Phi      0.0\n")

    content_lines.append("\n# Some additional flags\n")
    content_lines.append("Voronoi.charge              off\n")
    content_lines.append("#scf.Electric.Field         0.0 0.0 1.0\n")
    content_lines.append("#scf.system.charge          0.0\n")
    content_lines.append("\n")

    content_lines.append("MD.Type nomd # Nomd|Opt|NVE|NVT_VS|NVT_NH\n\n")

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
    content_lines.append(f"Band.dispersion  {band}\n") 
    content_lines.append(f"Band.Nkpath  {npaths}\n")
    content_lines.append("<Band.kpath\n")
    if kpaths:
        [content_lines.append(f"{path}\n") for path in kpaths]
    content_lines.append("Band.kpath>\n\n") 

    # Density-of-states
    content_lines.append("Dos.fileout        off        # on|off, default=off\n") 
    content_lines.append("Dos.Erange        -8.0  8.0   # default=-20 20\n") 
    content_lines.append("Dos.Kgrid          15 15 15   # default=Kgrid1 Kgrid2 Kgrid3\n") 

    # --- 2. Join the content and write to file in one operation ---
    full_content = "".join(content_lines)
    
    #with open(output_filename, 'w') as f:
    #    f.write(full_content)

    return full_content
