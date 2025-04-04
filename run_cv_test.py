import subprocess
import sys
import os

def run_cv_test():
    """
    Activates the virtual environment, runs the OpenCV test script, 
    and retrieves the detected centroid coordinates.
    
    :return: The centroid coordinates as a tuple (cx, cy) or None if not found.
    """

    # Path to the virtual environment activation script
    venv_path = "/home/researchlab1/myvenv/bin/activate"

    # Construct the command to activate the virtual environment and run cv_test.py
    command = f"source {venv_path} && python /home/researchlab1/Documents/Testing/cv_test.py"

    # Run the command in a new shell
    process = subprocess.run(command, shell=True, executable="/bin/bash", capture_output=True, text=True)

    # Print the output and errors (for debugging)
    print("STDOUT:", process.stdout)
    print("STDERR:", process.stderr)

    # Extract the centroid coordinates from cv_test.py output
    try:
        drop_px = eval(process.stdout.strip())  # Convert string output to tuple
        if isinstance(drop_px, tuple) and len(drop_px) == 2:
            return drop_px  # Return valid centroid coordinates
        else:
            return None
    except:
        return None  # Return None if extraction fails
