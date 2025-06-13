import numpy as np

def read_poscar(filename):
    """Read VASP POSCAR file and extract structure information"""
    with open(filename, 'r') as f:
        lines = f.readlines()

    # Extract comment line
    comment = lines[0].strip()

    # Extract scaling factor
    scale = float(lines[1].strip())

    # Extract lattice vectors
    lattice = np.zeros((3, 3))
    for i in range(3):
        lattice[i] = [float(x) for x in lines[i+2].split()]

    # Scale lattice vectors
    lattice *= scale

    # Extract element types
    elements = lines[5].split()

    # Extract number of atoms per element
    atom_counts = [int(x) for x in lines[6].split()]

    # Determine position format (Direct or Cartesian)
    pos_type = lines[7].strip().lower()
    direct = True if pos_type[0] in ['d', 's'] else False

    # Extract atomic positions
    positions = []
    line_index = 8
    for i, count in enumerate(atom_counts):
        for j in range(count):
            pos = [float(x) for x in lines[line_index].split()[:3]]
            positions.append((elements[i], pos))
            line_index += 1

    return {
        'comment': comment,
        'lattice': lattice,
        'elements': elements,
        'atom_counts': atom_counts,
        'positions': positions,
        'direct': direct
    }
