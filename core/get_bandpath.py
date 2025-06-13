import numpy as np
#import sys

def get_bandpath(positions,latvec,atomic_numbers):

    '''
    Use call SeeK-path library to generate common high-symmetry point paths 
    for band structure calculation.

    Takes fractional/direct coordinates

    '''

    #coords_array = np.array([site[1] for site in positions])
    #if coord_system != 'F' :
    #    inv_latvec = np.linalg.inv(latvec)
    #    coords_array = coords_array @ inv_latvec
    #    print(coords_array)

    kpaths=[]
    try:
        import seekpath
        print("SeeK-path is installed and available.")

        structure = (latvec, positions, atomic_numbers)
        # Use seekpath to get the path and k-points
        seekpath_output = seekpath.get_path(structure)
        # Extract high-symmetry points and the path
        k_points = seekpath_output['point_coords']
        kpath = seekpath_output['path']

        for segment in kpath:
            #print(f"{segment[0]} -> {segment[1]}")
            p_i = k_points[segment[0]]
            p_f = k_points[segment[1]]
            # convert high symmetry point coordinates to formmated strings
            pi_str = ' '.join(f"{p: .6f}" for p in p_i) 
            pf_str = ' '.join(f"{p: .6f}" for p in p_f)

            kpath =f" 50 {pi_str}  {pf_str}  {segment[0]:<7}  {segment[1]}"
            kpaths.append(kpath)

    except ImportError:
        print("SeeK-path is not installed. Install it with: pip install seekpath or set band to off")
        #sys.exit()

    return kpaths
