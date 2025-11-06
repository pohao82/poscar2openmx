def expand_basis(input_string):
    """
    Converts a PAO notation (e.g., 's3p2d2') to expanded form used for U and J defintion
    (e.g., '1s 0 2s 0 3s 0 1p 0 2p 0 1d 0 2d 0')  

    Args:
        input_string (str): Input in the form of 's3p2d2' 

    Returns:
        str: Expanded basis notation for U and J for OpenMX
    """
    # Initialize result string
    result = []

    # Define the orbital types we'll look for
    orbital_types = ['s', 'p', 'd', 'f']

    # Parse the input string
    current_orbital = None
    current_number = ""

    # Process each character in the input string
    for char in input_string:
        if char in orbital_types:
            # If we had a previous orbital and number, process it
            if current_orbital and current_number:
                max_count = int(current_number)
                for i in range(1, max_count + 1):
                    result.append(f"{i}{current_orbital} 0")

            # Set the new current orbital
            current_orbital = char
            current_number = ""
        elif char.isdigit():
            current_number += char

    # Process the last orbital and number
    if current_orbital and current_number:
        max_count = int(current_number)
        for i in range(1, max_count + 1):
            result.append(f"{i}{current_orbital} 0")

    # Join the result with spaces
    return " ".join(result)

# Test the function
#test_input = "s3p2d2"
#print(expand_basis(test_input))
