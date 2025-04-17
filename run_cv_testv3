import subprocess
import sys
import os

def detect_droplet():
    """
    Activates the virtual environment, runs the OpenCV test script, 
    and retrieves the detected centroid coordinates.

    :return: The centroid coordinates as a tuple (cx, cy) or None if not found.
    """

    venv_path = "/home/researchlab1/myvenv/bin/activate"
    command = f"source {venv_path} && python /home/researchlab1/Documents/Testing/cv_test.py"

    process = subprocess.run(command, shell=True, executable="/bin/bash", capture_output=True, text=True)

    print("STDOUT:", process.stdout)
    print("STDERR:", process.stderr)

    try:
        drop_px = eval(process.stdout.strip())
        if isinstance(drop_px, tuple) and len(drop_px) == 2:
            return drop_px
        else:
            return None
    except:
        return None

def run_cv_test():
    """
    Runs droplet detection once and returns the droplet's centroid coordinates.
    Returns None if no droplet is detected.
    """
    print("Running droplet detection...")
    drop_px = detect_droplet()

    if drop_px:
        print(f"Droplet detected at pixel coordinates: {drop_px}")
        return drop_px
    else:
        print("No droplet detected.")
        return None
