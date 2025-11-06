import numpy as np

def cartesian_to_spherical(s):
    """
    Converts a Cartesian vector [sx, sy, sz] to Spherical coordinates [r, theta, phi].
    
    Args:
        s (list or np.ndarray): A list or array containing the Cartesian coordinates [sx, sy, sz].
        
    Returns:
        list: A list containing the Spherical coordinates [r, theta, phi] in radians.
    """
    sx, sy, sz = s
    # Calculate the radius (r)
    r = np.sqrt(sx**2 + sy**2 + sz**2)
    # Handle the case of the vector being at the origin to avoid division by zero
    if r == 0:
        return [0, 0, 0]
    # Calculate the polar angle (theta)
    # This is the angle from the positive z-axis, range [0, pi]
    theta = np.arccos(sz / r)
    # Calculate the azimuthal angle (phi)
    # This is the angle in the xy-plane from the positive x-axis, range [-pi, pi]
    phi = np.arctan2(sy, sx)

    grad2deg = 180.0/np.pi
    theta *= grad2deg 
    phi *= grad2deg 
    
    return [r, theta, phi]

